"""File upload router for handling document uploads."""

import os
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from sqlalchemy import func

from src.core.database import get_db
from src.core.deps import get_current_user
from src.core.config import settings
from src.models.user import User
from src.models.session import Session as UserSession
from src.models.file_upload import FileUpload, FileStatus
from src.models.processing_job import ProcessingJob, ProcessingStatus
from src.schemas.file import FileUploadResponse, FileListResponse, ProcessingJobResponse
from src.schemas.common import MessageResponse
from src.services.minio_service import minio_service
from data_processor.extractor import extract_document_data

router = APIRouter(prefix="/files", tags=["Files"])


def validate_file_extension(filename: str) -> bool:
    """
    Validate file extension against allowed types.
    
    Args:
        filename: Name of the file
        
    Returns:
        bool: True if valid extension
    """
    ext = Path(filename).suffix.lower()
    return ext in settings.ALLOWED_EXTENSIONS


def validate_file_size(file_size: int) -> bool:
    """
    Validate file size against maximum allowed size.
    
    Args:
        file_size: Size of file in bytes
        
    Returns:
        bool: True if within limit
    """
    return file_size <= settings.MAX_UPLOAD_SIZE


@router.post("/upload", response_model=FileUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_file(
    file: UploadFile = File(...),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Upload a document file to MinIO storage.
    
    Args:
        file: Uploaded file
        user: Current authenticated user
        db: Database session
        
    Returns:
        FileUploadResponse: Upload confirmation with metadata
        
    Raises:
        HTTPException: If validation fails or upload fails
    """
    # Validate file extension
    if not validate_file_extension(file.filename):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file type. Allowed types: {', '.join(settings.ALLOWED_EXTENSIONS)}"
        )
    
    # Read file content
    file_content = await file.read()
    file_size = len(file_content)
    
    # Validate file size
    if not validate_file_size(file_size):
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File too large. Maximum size: {settings.MAX_UPLOAD_SIZE / (1024*1024):.2f} MB"
        )
    
    # Get or create active session for user
    active_session = db.query(UserSession).filter(
        UserSession.user_id == user.id,
        UserSession.expires_at > func.now()
    ).order_by(UserSession.created_at.desc()).first()
    
    if not active_session:
        active_session = UserSession.create_session(user.id)
        db.add(active_session)
        db.commit()
        db.refresh(active_session)
    
    session_id = active_session.session_id
    
    # Upload to MinIO
    try:
        import io
        file_stream = io.BytesIO(file_content)
        file_path = minio_service.upload_file(
            session_id=session_id,
            filename=file.filename,
            file_data=file_stream,
            content_type=file.content_type or "application/octet-stream",
            file_size=file_size
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload file: {str(e)}"
        )
    
    # Store file metadata in database
    file_upload = FileUpload(
        session_id=session_id,
        filename=file.filename,
        file_path=file_path,
        file_type=file.content_type or "application/octet-stream",
        file_size=file_size,
        status=FileStatus.UPLOADED
    )
    
    db.add(file_upload)
    db.commit()
    db.refresh(file_upload)
    
    # Create processing job (will be triggered by separate service later)
    processing_job = ProcessingJob(
        session_id=session_id,
        file_id=file_upload.id,
        status=ProcessingStatus.PENDING
    )
    
    db.add(processing_job)
    db.commit()
    
    return file_upload


@router.get("/list", response_model=FileListResponse)
async def list_files(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List all uploaded files for the current user's session.
    
    Args:
        user: Current authenticated user
        db: Database session
        
    Returns:
        FileListResponse: List of uploaded files
    """
    # Get active session
    active_session = db.query(UserSession).filter(
        UserSession.user_id == user.id,
        UserSession.expires_at > func.now()
    ).order_by(UserSession.created_at.desc()).first()
    
    if not active_session:
        return FileListResponse(files=[], total=0)
    
    # Get files for session
    files = db.query(FileUpload).filter(
        FileUpload.session_id == active_session.session_id
    ).all()
    
    return FileListResponse(files=files, total=len(files))


@router.get("/{file_id}", response_model=FileUploadResponse)
async def get_file_info(
    file_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get information about a specific file.
    
    Args:
        file_id: ID of the file
        user: Current authenticated user
        db: Database session
        
    Returns:
        FileUploadResponse: File information
        
    Raises:
        HTTPException: If file not found
    """
    file_upload = db.query(FileUpload).filter(FileUpload.id == file_id).first()
    
    if not file_upload:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )
    
    # Verify user owns this file's session
    session = db.query(UserSession).filter(
        UserSession.session_id == file_upload.session_id,
        UserSession.user_id == user.id
    ).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    return file_upload


@router.delete("/{file_id}", response_model=MessageResponse)
async def delete_file(
    file_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete a file.
    
    Args:
        file_id: ID of the file to delete
        user: Current authenticated user
        db: Database session
        
    Returns:
        MessageResponse: Deletion confirmation
        
    Raises:
        HTTPException: If file not found or deletion fails
    """
    file_upload = db.query(FileUpload).filter(FileUpload.id == file_id).first()
    
    if not file_upload:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )
    
    # Verify user owns this file's session
    session = db.query(UserSession).filter(
        UserSession.session_id == file_upload.session_id,
        UserSession.user_id == user.id
    ).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    # Delete from MinIO
    success = minio_service.delete_file(file_upload.session_id, file_upload.filename)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete file from storage"
        )
    
    # Delete associated processing jobs first
    db.query(ProcessingJob).filter(ProcessingJob.file_id == file_id).delete()
    
    # Delete from database
    db.delete(file_upload)
    db.commit()
    
    return MessageResponse(message="File deleted successfully")


@router.get("/processing/{file_id}", response_model=ProcessingJobResponse)
async def get_processing_status(
    file_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get processing status for a file.
    
    Args:
        file_id: ID of the file
        user: Current authenticated user
        db: Database session
        
    Returns:
        ProcessingJobResponse: Processing job information
        
    Raises:
        HTTPException: If processing job not found
    """
    # Get file and verify ownership
    file_upload = db.query(FileUpload).filter(FileUpload.id == file_id).first()
    
    if not file_upload:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )
    
    session = db.query(UserSession).filter(
        UserSession.session_id == file_upload.session_id,
        UserSession.user_id == user.id
    ).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    # Get processing job
    processing_job = db.query(ProcessingJob).filter(
        ProcessingJob.file_id == file_id
    ).first()
    
    if not processing_job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Processing job not found"
        )
    
    return processing_job
