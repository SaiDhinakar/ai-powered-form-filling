from dotenv import load_dotenv
import os
# from src.services.storage.minio_service import MinioService

load_dotenv()

class Settings:
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./test.db")
    MINIO_ENDPOINT: str = os.getenv("MINIO_ENDPOINT", "localhost:9000")
    MINIO_ACCESS_KEY: str = os.getenv("MINIO_ACCESS_KEY", "minioadmin")
    MINIO_SECRET_KEY: str = os.getenv("MINIO_SECRET_KEY", "minioadmin")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "supersecretkey")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    UPLOAD_FILE_PATH: str = os.getenv("UPLOAD_FILE_PATH", "./uploads")
    OUTPUT_FILE_PATH: str = os.getenv("OUTPUT_FILE_PATH", "./outputs")
    AGENTS_API_ENDPOINT: str = os.getenv("AGENTS_API_ENDPOINT", "http://localhost:8907/agent")
    # ENTITY_DATA_STORAGE = MinioService(
    #     endpoint=MINIO_ENDPOINT,
    #     access_key=MINIO_ACCESS_KEY,
    #     secret_key=MINIO_SECRET_KEY,
    #     bucket_name=MINIO_BUCKET_NAME
    # )

    # TEMPLATE_STORAGE = MinioService(
    #     endpoint=MINIO_ENDPOINT,
    #     access_key=MINIO_ACCESS_KEY,
    #     secret_key=MINIO_SECRET_KEY,
    #     bucket_name=MINIO_BUCKET_NAME
    # )

settings = Settings()
# settings.ENTITY_DATA_STORAGE.ensure_bucket_exists("user-data")
# settings.TEMPLATE_STORAGE.ensure_bucket_exists("templates")
os.makedirs(settings.UPLOAD_FILE_PATH, exist_ok=True)