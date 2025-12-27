from minio import Minio
from minio.error import S3Error
import os
from io import BytesIO


class MinioService:
    def __init__(self, endpoint, access_key, secret_key, secure=False):
        """
        Initialize MinIO client
        
        Args:
            endpoint: MinIO server endpoint
            access_key: Access key for MinIO
            secret_key: Secret key for MinIO
            secure: Use HTTPS if True
        """
        self.client = Minio(
            endpoint,
            access_key=access_key,
            secret_key=secret_key,
            secure=secure
        )
    
    def ensure_bucket_exists(self, bucket_name):
        """
        Create bucket if it doesn't exist
        
        Args:
            bucket_name: Name of the bucket
        """
        try:
            if not self.client.bucket_exists(bucket_name):
                self.client.make_bucket(bucket_name)
                print(f"Bucket '{bucket_name}' created successfully")
            else:
                print(f"Bucket '{bucket_name}' already exists")
        except S3Error as e:
            print(f"Error creating bucket: {e}")
            raise
    
    def upload_file(self, bucket_name, user_id, entity_id, file_data, file_name):
        """
        Upload file to MinIO with nested directory structure
        
        Args:
            bucket_name: Name of the bucket
            user_id: User identifier for directory structure
            entity_id: Entity identifier for directory structure
            file_data: File data (bytes or file-like object)
            file_name: Name of the file
            
        Returns:
            str: Object path in MinIO
        """
        try:
            # Ensure bucket exists
            self.ensure_bucket_exists(bucket_name)
            
            # Create nested path: user_id/entity_id/file_name
            object_path = f"{user_id}/{entity_id}/{file_name}"
            
            # Convert to BytesIO if file_data is bytes
            if isinstance(file_data, bytes):
                file_data = BytesIO(file_data)
                file_size = len(file_data.getvalue())
            else:
                file_data.seek(0, os.SEEK_END)
                file_size = file_data.tell()
                file_data.seek(0)
            
            # Upload file
            self.client.put_object(
                bucket_name,
                object_path,
                file_data,
                file_size
            )
            
            print(f"File uploaded successfully to {object_path}")
            return object_path
            
        except S3Error as e:
            print(f"Error uploading file: {e}")
            raise
    
    def get_file(self, bucket_name, object_path):
        """
        Download file from MinIO
        
        Args:
            bucket_name: Name of the bucket
            object_path: Path to the object
            
        Returns:
            bytes: File content
        """
        try:
            response = self.client.get_object(bucket_name, object_path)
            data = response.read()
            response.close()
            response.release_conn()
            return data
        except S3Error as e:
            print(f"Error downloading file: {e}")
            raise
    
    def delete_file(self, bucket_name, object_path):
        """
        Delete file from MinIO
        
        Args:
            bucket_name: Name of the bucket
            object_path: Path to the object
        """
        try:
            self.client.remove_object(bucket_name, object_path)
            print(f"File {object_path} deleted successfully")
        except S3Error as e:
            print(f"Error deleting file: {e}")
            raise

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()

    endpoint, username, password = (
        os.getenv('MINIO_ENDPOINT', 'localhost:9000'),
        os.getenv('MINIO_ACCESS_KEY'),
        os.getenv('MINIO_SECRET_KEY')
    )
    # Example usage
    minio_service = MinioService(
        endpoint=os.getenv('MINIO_ENDPOINT', 'localhost:9000'),
        access_key=os.getenv('MINIO_ACCESS_KEY'),
        secret_key=os.getenv('MINIO_SECRET_KEY')
    )
    
    bucket = "my-bucket"
    user_id = "1"
    entity_id = "1"
    file_name = "example.txt"
    file_content = b"Hello, MinIO!"
    
    # Upload file
    object_path = minio_service.upload_file(bucket, user_id, entity_id, file_content, file_name)
    
    # Download file
    downloaded_content = minio_service.get_file(bucket, object_path)
    print(f"Downloaded content: {downloaded_content.decode()}")
    
    # Delete file
    # minio_service.delete_file(bucket, object_path)