"""Background tasks for PDF processing and embedding generation."""

import logging
from typing import Optional
from celery import Task

from src.tasks import celery_app
from src.core.database import SessionLocal
from src.models.file_upload import FileUpload
from src.models.processing_job import ProcessingJob, ProcessingStatus
from src.models.entity import Entity
from src.services.pdf_extractor import pdf_extractor
from src.services.embedding_service import embedding_service
from src.services.minio_service import minio_service

logger = logging.getLogger(__name__)


class DatabaseTask(Task):
    """Base task with database session management."""
    
    _db = None
    
    @property
    def db(self):
        if self._db is None:
            self._db = SessionLocal()
        return self._db
    
    def after_return(self, *args, **kwargs):
        if self._db is not None:
            self._db.close()
            self._db = None


@celery_app.task(bind=True, base=DatabaseTask, max_retries=3)
def process_pdf_task(self, file_id: int, entity_id: int, user_id: int) -> dict:
    """
    Background task to process uploaded PDF file.
    
    This task:
    1. Downloads the PDF from MinIO
    2. Extracts text, tables, and images
    3. Updates entity with extracted text
    4. Generates embeddings and stores in ChromaDB
    5. Updates processing job status
    
    Args:
        file_id: ID of the uploaded file
        entity_id: ID of the entity this file belongs to
        user_id: ID of the user who uploaded the file
        
    Returns:
        dict: Processing result with status and extracted data
    """
    db = self.db
    
    try:
        logger.info(f"Starting PDF processing for file_id={file_id}, entity_id={entity_id}")
        
        # Get file upload record
        file_upload = db.query(FileUpload).filter(FileUpload.id == file_id).first()
        if not file_upload:
            raise ValueError(f"File upload {file_id} not found")
        
        # Get or create processing job
        processing_job = db.query(ProcessingJob).filter(
            ProcessingJob.file_id == file_id
        ).first()
        
        if not processing_job:
            processing_job = ProcessingJob(
                session_id=file_upload.session_id,
                file_id=file_id,
                status=ProcessingStatus.PROCESSING
            )
            db.add(processing_job)
        else:
            processing_job.status = ProcessingStatus.PROCESSING
        
        db.commit()
        
        # Download file from MinIO
        logger.info(f"Downloading file from MinIO: {file_upload.filename}")
        file_data = minio_service.get_file(file_upload.session_id, file_upload.filename)
        
        if not file_data:
            raise ValueError(f"Failed to download file from MinIO")
        
        # Extract PDF content
        logger.info(f"Extracting PDF content")
        extraction_result = pdf_extractor.extract_from_bytes(file_data)
        
        if not extraction_result.success:
            raise ValueError(f"PDF extraction failed: {extraction_result.error_message}")
        
        # Get entity
        entity = db.query(Entity).filter(Entity.id == entity_id).first()
        if not entity:
            raise ValueError(f"Entity {entity_id} not found")
        
        # Update entity with extracted text
        logger.info(f"Updating entity {entity_id} with extracted text")
        entity.extracted_text = extraction_result.text
        
        # Update entity metadata with extraction results
        entity_metadata = entity.metadata or {}
        entity_metadata.update({
            "pdf_pages": extraction_result.total_pages,
            "pdf_metadata": extraction_result.metadata,
            "has_tables": len(extraction_result.tables) > 0,
            "has_images": len(extraction_result.images) > 0,
            "table_count": len(extraction_result.tables),
            "image_count": len(extraction_result.images),
            "character_count": len(extraction_result.text)
        })
        entity.metadata = entity_metadata
        
        # Generate and store embeddings
        if extraction_result.text and extraction_result.text.strip():
            logger.info(f"Generating and storing embeddings for entity {entity_id}")
            embedding_service.store_entity_embedding(
                user_id=user_id,
                entity_id=entity_id,
                text=extraction_result.text,
                metadata={
                    "name": entity.name,
                    "file_id": file_id,
                    "filename": file_upload.filename
                }
            )
        
        # Update processing job with results
        processing_job.status = ProcessingStatus.COMPLETED
        processing_job.extracted_data = {
            "total_pages": extraction_result.total_pages,
            "text_length": len(extraction_result.text),
            "tables_found": len(extraction_result.tables),
            "images_found": len(extraction_result.images),
            "metadata": extraction_result.metadata
        }
        processing_job.error_message = None
        
        # Update file upload status
        file_upload.status = "processed"
        
        db.commit()
        
        logger.info(f"Successfully processed PDF for file_id={file_id}, entity_id={entity_id}")
        
        return {
            "success": True,
            "file_id": file_id,
            "entity_id": entity_id,
            "extracted_data": processing_job.extracted_data
        }
        
    except Exception as e:
        logger.error(f"Failed to process PDF for file_id={file_id}: {e}", exc_info=True)
        
        # Update processing job with error
        try:
            if 'processing_job' in locals() and processing_job:
                processing_job.status = ProcessingStatus.FAILED
                processing_job.error_message = str(e)[:500]
                db.commit()
        except Exception as commit_error:
            logger.error(f"Failed to update processing job status: {commit_error}")
        
        # Retry task if not max retries
        if self.request.retries < self.max_retries:
            logger.info(f"Retrying task, attempt {self.request.retries + 1}/{self.max_retries}")
            raise self.retry(exc=e, countdown=60 * (self.request.retries + 1))
        
        return {
            "success": False,
            "file_id": file_id,
            "entity_id": entity_id,
            "error": str(e)
        }
