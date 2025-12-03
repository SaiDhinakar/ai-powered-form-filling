"""MinIO storage service for file management."""

import io
from typing import BinaryIO, Optional
from minio import Minio
from minio.error import S3Error
import logging

from src.core.config import settings

logger = logging.getLogger(__name__)


class MinIOService:
    """Service for managing file storage in MinIO."""
    
    def __init__(self):
        """Initialize MinIO client."""
        self.client = Minio(
            settings.MINIO_ENDPOINT,
            access_key=settings.MINIO_ACCESS_KEY,
            secret_key=settings.MINIO_SECRET_KEY,
            secure=settings.MINIO_SECURE
        )
        self.bucket_name = settings.MINIO_BUCKET_NAME
    
    def initialize_bucket(self) -> None:
        """
        Create bucket if it doesn't exist.
        
        Raises:
            Exception: If bucket creation fails
        """
        try:
            if not self.client.bucket_exists(self.bucket_name):
                self.client.make_bucket(self.bucket_name)
                logger.info(f"Created bucket: {self.bucket_name}")
            else:
                logger.info(f"Bucket already exists: {self.bucket_name}")
        except S3Error as e:
            logger.error(f"Error initializing bucket: {e}")
            raise
    
    def upload_file(
        self,
        session_id: str,
        filename: str,
        file_data: BinaryIO,
        content_type: str,
        file_size: int
    ) -> str:
        """
        Upload a file to MinIO.
        
        Args:
            session_id: Session ID for organizing files
            filename: Name of the file
            file_data: File data stream
            content_type: MIME type of the file
            file_size: Size of the file in bytes
            
        Returns:
            str: Object path in MinIO (session_id/uploads/filename)
            
        Raises:
            Exception: If upload fails
        """
        object_name = f"{session_id}/uploads/{filename}"
        
        try:
            self.client.put_object(
                bucket_name=self.bucket_name,
                object_name=object_name,
                data=file_data,
                length=file_size,
                content_type=content_type
            )
            logger.info(f"Uploaded file: {object_name}")
            return object_name
        except S3Error as e:
            logger.error(f"Error uploading file: {e}")
            raise
    
    def get_file(self, session_id: str, filename: str) -> Optional[bytes]:
        """
        Retrieve a file from MinIO.
        
        Args:
            session_id: Session ID
            filename: Name of the file
            
        Returns:
            Optional[bytes]: File data or None if not found
        """
        object_name = f"{session_id}/uploads/{filename}"
        
        try:
            response = self.client.get_object(self.bucket_name, object_name)
            data = response.read()
            response.close()
            response.release_conn()
            return data
        except S3Error as e:
            logger.error(f"Error retrieving file: {e}")
            return None
    
    def list_files(self, session_id: str) -> list[str]:
        """
        List all files for a session.
        
        Args:
            session_id: Session ID
            
        Returns:
            list[str]: List of filenames
        """
        prefix = f"{session_id}/uploads/"
        
        try:
            objects = self.client.list_objects(
                self.bucket_name,
                prefix=prefix,
                recursive=True
            )
            return [obj.object_name.replace(prefix, "") for obj in objects]
        except S3Error as e:
            logger.error(f"Error listing files: {e}")
            return []
    
    def delete_file(self, session_id: str, filename: str) -> bool:
        """
        Delete a file from MinIO.
        
        Args:
            session_id: Session ID
            filename: Name of the file
            
        Returns:
            bool: True if deleted successfully
        """
        object_name = f"{session_id}/uploads/{filename}"
        
        try:
            self.client.remove_object(self.bucket_name, object_name)
            logger.info(f"Deleted file: {object_name}")
            return True
        except S3Error as e:
            logger.error(f"Error deleting file: {e}")
            return False
    
    def delete_session_files(self, session_id: str) -> bool:
        """
        Delete all files for a session.
        
        Args:
            session_id: Session ID
            
        Returns:
            bool: True if deleted successfully
        """
        prefix = f"{session_id}/"
        
        try:
            objects = self.client.list_objects(
                self.bucket_name,
                prefix=prefix,
                recursive=True
            )
            
            for obj in objects:
                self.client.remove_object(self.bucket_name, obj.object_name)
            
            logger.info(f"Deleted all files for session: {session_id}")
            return True
        except S3Error as e:
            logger.error(f"Error deleting session files: {e}")
            return False


# Global MinIO service instance
minio_service = MinIOService()
