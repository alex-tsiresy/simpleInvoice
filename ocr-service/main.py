import os
import tempfile
from typing import Dict, Any, Optional, List
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from rapidocr_onnxruntime import RapidOCR
import uvicorn
from pathlib import Path
import json
from PIL import Image
import pypdfium2 as pdfium

app = FastAPI(title="RapidOCR Microservice", version="1.0.0")

# Initialize RapidOCR engine
engine = None


@app.on_event("startup")
async def startup_event():
    """Initialize RapidOCR engine on startup"""
    global engine

    try:
        # Initialize RapidOCR - works on both CPU and GPU
        engine = RapidOCR()
    except Exception as e:
        print(f"Error initializing RapidOCR engine: {e}")
        import traceback
        traceback.print_exc()
        raise


def pdf_to_images(pdf_path: str, dpi: int = 200) -> List[Image.Image]:
    """
    Convert PDF pages to PIL Images using pypdfium2

    Args:
        pdf_path: Path to PDF file
        dpi: Resolution for rendering (default 200)

    Returns:
        List of PIL Image objects, one per page
    """
    images = []
    try:
        pdf = pdfium.PdfDocument(pdf_path)

        for page_num in range(len(pdf)):
            page = pdf[page_num]

            # Render page to PIL Image
            # Scale factor for DPI (72 is base DPI)
            scale = dpi / 72
            pil_image = page.render(scale=scale).to_pil()

            images.append(pil_image)

        return images
    except Exception as e:
        raise Exception(f"Failed to convert PDF to images: {str(e)}")


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "RapidOCR",
        "engine_ready": engine is not None
    }


@app.post("/ocr")
async def process_ocr(file: UploadFile = File(...)):
    """
    Process document with RapidOCR

    Args:
        file: Uploaded document file (image or PDF)

    Returns:
        OCR results including text, bounding boxes, and confidence scores
    """
    if engine is None:
        raise HTTPException(status_code=503, detail="OCR engine not initialized")

    # Create temporary file to store uploaded document
    temp_file = None
    temp_dir = None

    try:
        # Read file content
        file_content = await file.read()

        # Create temporary directory for processing
        temp_dir = tempfile.mkdtemp()

        # Save uploaded file temporarily
        file_extension = Path(file.filename).suffix or ".png"
        temp_file = os.path.join(temp_dir, f"document{file_extension}")

        with open(temp_file, "wb") as f:
            f.write(file_content)

        # Check if file is a PDF
        is_pdf = file_extension.lower() == ".pdf"

        # For PDFs, convert to images first
        images_to_process = []
        if is_pdf:
            pdf_images = pdf_to_images(temp_file)
            images_to_process = [(img, f"page_{i+1}") for i, img in enumerate(pdf_images)]
        else:
            # For images, process directly
            images_to_process = [(temp_file, "page_1")]

        # Process all images/pages
        text_parts = []
        elements = []
        total_time = 0

        for img_source, page_label in images_to_process:
            # Process with RapidOCR
            result, elapse = engine(img_source)

            # Calculate processing time
            page_time = sum(elapse) if isinstance(elapse, list) else elapse
            total_time += page_time

            # Parse results
            if result:
                for idx, item in enumerate(result):
                    # RapidOCR returns: [box, text, confidence]
                    box, text, confidence = item

                    text_parts.append(text)

                    elements.append({
                        "id": len(elements),
                        "page": page_label,
                        "text": text,
                        "confidence": float(confidence),
                        "bbox": box
                    })

        # Combine all text
        combined_text = "\n".join(text_parts)

        response = {
            "success": True,
            "filename": file.filename,
            "text": combined_text,
            "elements": elements,
            "total_elements": len(elements),
            "processing_time": total_time
        }

        return JSONResponse(content=response)

    except Exception as e:
        print(f"Error processing OCR: {e}")
        raise HTTPException(status_code=500, detail=f"OCR processing failed: {str(e)}")

    finally:
        # Clean up temporary files
        if temp_file and os.path.exists(temp_file):
            try:
                os.remove(temp_file)
            except:
                pass

        if temp_dir and os.path.exists(temp_dir):
            try:
                import shutil
                shutil.rmtree(temp_dir)
            except:
                pass


@app.get("/")
async def root():
    """Root endpoint with service information"""
    return {
        "service": "RapidOCR Microservice",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "health": "/health",
            "ocr": "/ocr (POST)"
        }
    }


if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8119,
        log_level="info"
    )
