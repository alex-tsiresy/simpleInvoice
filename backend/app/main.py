from fastapi import FastAPI, UploadFile, File, Depends, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
import uuid
from datetime import datetime

from app.database import get_db, init_db
from app.models import Document, DocumentStatus
from app.auth import get_current_user
from app.storage import storage
from app.ocr_service import ocr_service
from app.invoice_extractor import invoice_extractor
from app.config import get_settings

settings = get_settings()

app = FastAPI(
    title="Compass Document Processing API",
    description="Document processing with OCR and classification",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    await init_db()


@app.get("/")
async def root():
    return {
        "message": "Compass Document Processing API",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


async def process_document_task(document_id: str, file_content: bytes, file_type: str, filename: str):
    """Background task to process document with OCR and summarization"""
    from app.database import async_session

    async with async_session() as db:
        try:
            # Update status to processing
            result = await db.execute(
                select(Document).where(Document.id == document_id)
            )
            document = result.scalar_one_or_none()

            if not document:
                print(f"Error: Document {document_id} not found")
                return

            document.status = DocumentStatus.PROCESSING
            await db.commit()

            # Step 1: OCR Processing
            ocr_result = await ocr_service.process_document(file_content, file_type, filename)

            if not ocr_result.get("success"):
                print(f"OCR failed for '{filename}': {ocr_result.get('error')}")
                document.status = DocumentStatus.FAILED
                document.error_message = ocr_result.get("error", "OCR processing failed")
                await db.commit()
                return

            # Update with OCR results
            total_elements = ocr_result.get("total_elements", 0)
            document.ocr_text = ocr_result.get("text", "")
            document.ocr_metadata = {
                "pages": ocr_result.get("pages", []),
                "total_pages": ocr_result.get("total_pages", 0),
                "elements": ocr_result.get("elements", []),
                "total_elements": total_elements
            }
            document.ocr_completed_at = datetime.utcnow()
            document.status = DocumentStatus.OCR_COMPLETE
            await db.commit()

            # Step 2: Extract Invoice Data
            if document.ocr_text:
                extraction_result = await invoice_extractor.extract_invoice_data(document.ocr_text)

                if extraction_result.get("success"):
                    document.invoice_data = extraction_result.get("invoice_data", {})
                    document.invoice_extracted_at = datetime.utcnow()
                    document.status = DocumentStatus.COMPLETED
                else:
                    print(f"Invoice extraction failed for '{filename}': {extraction_result.get('error')}")
                    document.error_message = extraction_result.get("error", "Invoice extraction failed")
                    document.status = DocumentStatus.OCR_COMPLETE  # Keep OCR results even if extraction fails

            await db.commit()

        except Exception as e:
            print(f"Error processing document {document_id}: {str(e)}")
            if 'document' in locals() and document:
                document.status = DocumentStatus.FAILED
                document.error_message = str(e)
                await db.commit()
            raise


@app.post("/api/documents/upload")
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    current_user: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Upload a document for processing

    Accepts: PDF, PNG, JPG, JPEG, TIFF, BMP
    """
    # Validate file type
    allowed_types = [
        "application/pdf",
        "image/png",
        "image/jpeg",
        "image/jpg",
        "image/tiff",
        "image/bmp"
    ]

    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {file.content_type}. Allowed types: PDF, PNG, JPG, TIFF, BMP"
        )

    try:
        # Read file content
        file_content = await file.read()

        # Upload to MinIO
        object_key, file_size = storage.upload_file(
            file=file.file,
            filename=file.filename,
            content_type=file.content_type
        )

        # Create database record
        document_id = str(uuid.uuid4())
        document = Document(
            id=document_id,
            user_id=current_user,
            filename=object_key,
            original_filename=file.filename,
            file_type=file.content_type,
            file_size=file_size,
            s3_key=object_key,
            s3_bucket=settings.minio_bucket,
            status=DocumentStatus.UPLOADED
        )

        db.add(document)
        await db.commit()
        await db.refresh(document)

        # Start background processing
        await file.seek(0)
        file_content = await file.read()
        background_tasks.add_task(
            process_document_task,
            document_id,
            file_content,
            file.content_type,
            file.filename
        )

        return {
            "message": "Document uploaded successfully",
            "document": document.to_dict()
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/documents/{document_id}")
async def get_document(
    document_id: str,
    current_user: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get document by ID"""
    result = await db.execute(
        select(Document).where(
            Document.id == document_id,
            Document.user_id == current_user
        )
    )
    document = result.scalar_one_or_none()

    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    # Generate presigned URL for file access
    file_url = storage.get_file_url(document.s3_key)

    response = document.to_dict()
    response["file_url"] = file_url

    return response


@app.get("/api/documents")
async def list_documents(
    skip: int = 0,
    limit: int = 50,
    current_user: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List all documents for current user"""
    result = await db.execute(
        select(Document)
        .where(Document.user_id == current_user)
        .order_by(Document.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    documents = result.scalars().all()

    return {
        "documents": [doc.to_dict() for doc in documents],
        "total": len(documents)
    }


@app.delete("/api/documents/{document_id}")
async def delete_document(
    document_id: str,
    current_user: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete document"""
    result = await db.execute(
        select(Document).where(
            Document.id == document_id,
            Document.user_id == current_user
        )
    )
    document = result.scalar_one_or_none()

    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    # Delete from storage
    storage.delete_file(document.s3_key)

    # Delete from database
    await db.delete(document)
    await db.commit()

    return {"message": "Document deleted successfully"}


@app.get("/api/documents/{document_id}/download")
async def download_document(
    document_id: str,
    current_user: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get download URL for document"""
    result = await db.execute(
        select(Document).where(
            Document.id == document_id,
            Document.user_id == current_user
        )
    )
    document = result.scalar_one_or_none()

    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    # Generate presigned URL (valid for 1 hour)
    download_url = storage.get_file_url(document.s3_key, expires=3600)

    return {
        "download_url": download_url,
        "filename": document.original_filename,
        "expires_in": 3600
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
