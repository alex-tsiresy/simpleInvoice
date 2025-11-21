from sqlalchemy import Column, String, DateTime, Integer, Text, JSON, Enum as SQLEnum
from sqlalchemy.sql import func
from datetime import datetime
from enum import Enum
from app.database import Base


class DocumentStatus(str, Enum):
    UPLOADED = "uploaded"
    PROCESSING = "processing"
    OCR_COMPLETE = "ocr_complete"
    COMPLETED = "completed"
    FAILED = "failed"


class Document(Base):
    __tablename__ = "documents"

    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, nullable=False, index=True)
    filename = Column(String, nullable=False)
    original_filename = Column(String, nullable=False)
    file_type = Column(String, nullable=False)
    file_size = Column(Integer, nullable=False)

    # Storage
    s3_key = Column(String, nullable=False)
    s3_bucket = Column(String, nullable=False)

    # Processing status
    status = Column(SQLEnum(DocumentStatus), default=DocumentStatus.UPLOADED)

    # OCR results
    ocr_text = Column(Text, nullable=True)
    ocr_metadata = Column(JSON, nullable=True)
    ocr_completed_at = Column(DateTime(timezone=True), nullable=True)

    # Invoice data extracted by LLM (structured JSON)
    invoice_data = Column(JSON, nullable=True)
    invoice_extracted_at = Column(DateTime(timezone=True), nullable=True)

    # Error handling
    error_message = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "filename": self.filename,
            "original_filename": self.original_filename,
            "file_type": self.file_type,
            "file_size": self.file_size,
            "status": self.status.value,
            "ocr_text": self.ocr_text,
            "ocr_metadata": self.ocr_metadata,
            "invoice_data": self.invoice_data,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "ocr_completed_at": self.ocr_completed_at.isoformat() if self.ocr_completed_at else None,
            "invoice_extracted_at": self.invoice_extracted_at.isoformat() if self.invoice_extracted_at else None,
            "error_message": self.error_message
        }
