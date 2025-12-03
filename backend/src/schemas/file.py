"""Pydantic schemas for file upload requests and responses."""

from datetime import datetime
from pydantic import BaseModel, Field


class FileUploadResponse(BaseModel):
    """Schema for file upload response."""
    id: int
    session_id: str
    filename: str
    file_path: str
    file_type: str
    file_size: int
    status: str
    upload_time: datetime
    
    class Config:
        from_attributes = True


class FileListResponse(BaseModel):
    """Schema for listing files."""
    files: list[FileUploadResponse]
    total: int


class ProcessingJobResponse(BaseModel):
    """Schema for processing job response."""
    id: int
    session_id: str
    file_id: int
    status: str
    extracted_data: dict | None = None
    error_message: str | None = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
