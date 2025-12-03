"""Processing job model for OCR and data extraction tasks."""

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON, Enum
from sqlalchemy.orm import relationship
import enum

from src.core.database import Base


class ProcessingStatus(str, enum.Enum):
    """Processing job status enum."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class ProcessingJob(Base):
    """Processing job model for document extraction tasks."""
    
    __tablename__ = "processing_jobs"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(36), index=True, nullable=False)
    file_id = Column(Integer, ForeignKey("file_uploads.id", ondelete="CASCADE"), nullable=False)
    status = Column(Enum(ProcessingStatus), default=ProcessingStatus.PENDING, nullable=False)
    extracted_data = Column(JSON, nullable=True)  # Stores extracted fields as JSON
    error_message = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    file_upload = relationship("FileUpload", backref="processing_jobs")
    
    def __repr__(self) -> str:
        return f"<ProcessingJob(id={self.id}, file_id={self.file_id}, status='{self.status}')>"
