# AI-Powered Form Filling - Backend API

Professional FastAPI backend with authentication, session management, file uploads to MinIO, and document processing capabilities.

## 🏗️ Project Structure

```
backend/
├── main.py                      # FastAPI application entry point
├── pyproject.toml              # Project dependencies
├── .env.example                # Environment variables template
├── .gitignore                  # Git ignore rules
├── src/
│   ├── __init__.py
│   ├── api/                    # API route handlers
│   │   ├── __init__.py
│   │   ├── auth.py            # Authentication endpoints
│   │   ├── files.py           # File upload endpoints
│   │   └── health.py          # Health check endpoint
│   ├── core/                   # Core functionality
│   │   ├── __init__.py
│   │   ├── config.py          # Application configuration
│   │   ├── database.py        # Database setup
│   │   ├── security.py        # JWT & password hashing
│   │   └── deps.py            # Dependency injection
│   ├── models/                 # SQLAlchemy models
│   │   ├── __init__.py
│   │   ├── user.py            # User model
│   │   ├── session.py         # Session model
│   │   ├── file_upload.py     # File upload model
│   │   └── processing_job.py  # Processing job model
│   ├── schemas/                # Pydantic schemas
│   │   ├── __init__.py
│   │   ├── user.py            # User schemas
│   │   ├── session.py         # Session schemas
│   │   ├── file.py            # File schemas
│   │   └── common.py          # Common schemas
│   └── services/               # Business logic
│       ├── __init__.py
│       └── minio_service.py   # MinIO storage service
└── data_processor/             # Separate data processing module
    ├── __init__.py
    ├── extractor.py           # OCR extraction (placeholder)
    ├── mapper.py              # Form field mapping (placeholder)
    ├── postprocessor.py       # Data validation (placeholder)
    └── README.md              # Data processor documentation
```

## 🚀 Features

### ✅ Implemented

- **Authentication System**
  - User registration with email validation
  - JWT-based login
  - Password hashing with bcrypt
  - Protected routes with Bearer token authentication

- **Session Management**
  - Automatic session creation on login
  - Session-based file organization
  - Session expiration tracking (24-hour default)

- **File Upload to MinIO**
  - Multi-part file upload support
  - File type validation (PDF, PNG, JPG, JPEG, TIFF, BMP)
  - File size limits (10MB default)
  - Organization by session_id in MinIO buckets
  - File metadata stored in SQLite database

- **Database Management**
  - SQLAlchemy ORM with SQLite
  - Models: User, Session, FileUpload, ProcessingJob
  - Automatic table creation on startup

- **Modular Architecture**
  - Separate routers for each domain
  - Service layer for business logic
  - Clean separation of concerns
  - Type hints throughout

### 🔄 Placeholder (For Data Team)

- **Data Processor Module**
  - Document extraction (PaddleOCR integration needed)
  - Form field mapping (templates ready)
  - Data validation and cleaning (basic rules)
  - See `data_processor/README.md` for details

## 📋 Prerequisites

- Python 3.12+
- MinIO server (for file storage)
- `uv` package manager (recommended) or `pip`

## 🛠️ Setup

### 1. Install Dependencies

```bash
# Using uv (recommended)
uv sync

# Or using pip
pip install -e .
```

### 2. Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your settings
nano .env
```

**Required environment variables:**

```env
SECRET_KEY=your-secret-key-here-change-in-production
MINIO_ENDPOINT=localhost:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
```

### 3. Set Up MinIO

```bash
# Using Docker
docker run -d \
  -p 9000:9000 \
  -p 9001:9001 \
  --name minio \
  -e "MINIO_ROOT_USER=minioadmin" \
  -e "MINIO_ROOT_PASSWORD=minioadmin" \
  quay.io/minio/minio server /data --console-address ":9001"

# Access MinIO Console: http://localhost:9001
```

### 4. Run the Application

```bash
# Development mode with auto-reload
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Production mode
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

The API will be available at `http://localhost:8000`

## 📚 API Documentation

### Interactive Docs

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Endpoints

#### Authentication

- `POST /auth/register` - Register new user
- `POST /auth/login` - Login and get JWT token
- `GET /auth/me` - Get current user info (protected)

#### File Management

- `POST /files/upload` - Upload document (protected)
- `GET /files/list` - List uploaded files (protected)
- `GET /files/{file_id}` - Get file info (protected)
- `DELETE /files/{file_id}` - Delete file (protected)
- `GET /files/processing/{file_id}` - Get processing status (protected)

#### Health

- `GET /` - Root endpoint with API info
- `GET /health` - Health check

### Example Usage

```bash
# Register a user
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "SecurePass123"
  }'

# Login
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "SecurePass123"
  }'

# Upload file (replace YOUR_TOKEN)
curl -X POST "http://localhost:8000/files/upload" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@/path/to/document.pdf"

# List files
curl -X GET "http://localhost:8000/files/list" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## 🗄️ Database Schema

### Users Table
- `id` - Primary key
- `username` - Unique username
- `email` - Unique email
- `hashed_password` - Bcrypt hashed password
- `is_active` - Account status
- `created_at` - Registration timestamp

### Sessions Table
- `id` - Primary key
- `user_id` - Foreign key to users
- `session_id` - UUID for MinIO organization
- `created_at` - Session creation time
- `expires_at` - Session expiration time

### File Uploads Table
- `id` - Primary key
- `session_id` - UUID for file organization
- `filename` - Original filename
- `file_path` - MinIO object path
- `file_type` - MIME type
- `file_size` - Size in bytes
- `status` - Processing status
- `upload_time` - Upload timestamp

### Processing Jobs Table
- `id` - Primary key
- `session_id` - UUID
- `file_id` - Foreign key to file_uploads
- `status` - Job status (pending/processing/completed/failed)
- `extracted_data` - JSON of extracted fields
- `error_message` - Error details if failed
- `created_at` - Job creation time
- `updated_at` - Last update time

## 🔧 Configuration

All configuration is in `src/core/config.py` and loaded from environment variables:

- `SECRET_KEY` - JWT secret key (required)
- `DATABASE_URL` - Database connection string
- `MINIO_ENDPOINT` - MinIO server endpoint
- `MINIO_ACCESS_KEY` - MinIO access key
- `MINIO_SECRET_KEY` - MinIO secret key
- `MINIO_BUCKET_NAME` - Bucket name for uploads
- `CORS_ORIGINS` - Allowed CORS origins
- `MAX_UPLOAD_SIZE` - Maximum file size in bytes
- `ACCESS_TOKEN_EXPIRE_MINUTES` - JWT expiration time

## 👥 For Data Processing Team

See `data_processor/README.md` for detailed documentation on implementing:
- PaddleOCR document extraction
- Form field mapping
- Data validation and cleaning

The placeholder functions return dummy data for testing the API flow.

## 🧪 Testing

```bash
# Install test dependencies (if added)
pip install pytest pytest-asyncio httpx

# Run tests
pytest

# With coverage
pytest --cov=src tests/
```

## 📝 TODO

- [ ] Implement actual OCR extraction with PaddleOCR
- [ ] Complete form mapping templates
- [ ] Add background task queue for processing
- [ ] Implement session cleanup background job
- [ ] Add rate limiting
- [ ] Add request logging
- [ ] Add API versioning
- [ ] Add comprehensive tests
- [ ] Add Alembic migrations
- [ ] Add Docker Compose setup
- [ ] Add monitoring and metrics

## 🤝 Contributing

1. Keep code modular and well-documented
2. Follow PEP 8 style guidelines
3. Add type hints to all functions
4. Update this README for any new features
5. Test endpoints before committing

## 📄 License

[Your License Here]
