"""File upload model for tracking uploaded files."""

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Enum
import enum

from src.core.database import Base


class FileStatus(str, enum.Enum):
    """File processing status enum."""
    UPLOADED = "uploaded"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class FileUpload(Base):
    """File upload model for tracking uploaded documents."""
    
    __tablename__ = "file_uploads"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(36), index=True, nullable=False)
    filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)  # MinIO path: {session_id}/uploads/{filename}
    file_type = Column(String(50), nullable=False)
    file_size = Column(Integer, nullable=False)  # Size in bytes
    status = Column(Enum(FileStatus), default=FileStatus.UPLOADED, nullable=False)
    upload_time = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    def __repr__(self) -> str:
        return f"<FileUpload(id={self.id}, filename='{self.filename}', status='{self.status}')>"
