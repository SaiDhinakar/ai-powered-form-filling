# AI-Powered Form Filling Backend

An intelligent backend system that automates form filling using AI-powered document extraction, OCR, and semantic field mapping.

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                         Backend Services                            │
├─────────────────────┬─────────────────────┬─────────────────────────┤
│   FastAPI Backend   │   AI Agent Service  │      OCR Service        │
│     (Port 8000)     │     (Port 8907)     │      (Port 8909)        │
├─────────────────────┴─────────────────────┴─────────────────────────┤
│                         SQLite Database                             │
│                           (app.db)                                  │
└─────────────────────────────────────────────────────────────────────┘
```

## 🛠️ Tech Stack

### Core Framework

- **Python 3.12** - Programming language
- **FastAPI** - High-performance async web framework
- **SQLAlchemy 2.0** - ORM with async support
- **SQLite** - Lightweight database (production-ready with PostgreSQL option)
- **UV** - Fast Python package manager

### AI & Machine Learning

- **Google Gemini API** (`gemini-2.5-flash`) - LLM for data extraction and form filling
- **PaddleOCR** - Deep learning-based OCR engine
- **PaddlePaddle** - Deep learning framework

### Document Processing

- **PyMuPDF (fitz)** - PDF parsing and text extraction
- **BeautifulSoup4** - HTML template parsing
- **python-docx** - DOCX document processing
- **FillPDF** - PDF form filling

### OCR Engine

- **[plug-n-play-ocr](https://github.com/SaiDhinakar/plug-n-play-ocr)** - Custom OCR service integration for multi-language document processing with PaddleOCR backend

### Authentication & Security

- **python-jose** - JWT token generation/validation
- **passlib[bcrypt]** - Password hashing
- **OAuth2** - Bearer token authentication

### Utilities

- **googletrans** - Language translation
- **fastText** - Language detection (`lid.176.ftz`)
- **Pillow** - Image processing

## 📁 Project Structure

```
backend/
├── api/                          # REST API layer
│   ├── main.py                   # FastAPI app with routers
│   └── v1/
│       ├── models.py             # Pydantic schemas
│       └── routers/
│           ├── auth.py           # Authentication endpoints
│           ├── entities.py       # Entity management
│           ├── form_fill.py      # Form filling logic
│           ├── templates.py      # Template management
│           └── user_data.py      # User data upload
│
├── ai_agents/                    # AI Agent services
│   ├── agent.py                  # Gemini AI integration
│   ├── serve.py                  # Agent FastAPI server
│   └── tools/
│       └── translator.py         # Translation utilities
│
├── database/                     # Database layer
│   ├── base.py                   # SQLAlchemy base & engine
│   ├── init_db.py                # Database initialization
│   ├── repository.py             # Repository pattern implementation
│   ├── schema.py                 # Schema exports
│   ├── session.py                # Session management
│   └── models/
│       ├── entity.py             # Entity model
│       ├── extracted_data.py     # ExtractedData model
│       ├── template.py           # Template model
│       └── user.py               # User model
│
├── ocr/                          # OCR service
│   ├── server.py                 # OCR FastAPI server
│   └── languages.json            # Supported languages
│
├── src/
│   ├── lang_detect.py            # Language detection
│   ├── lid.176.ftz               # fastText model
│   └── services/
│       ├── data_extraction/      # Document extraction
│       │   ├── extract_contents.py
│       │   ├── pdf_extract.py
│       │   └── pdf_form_utils.py
│       ├── pdf_doc_service/      # PDF operations
│       │   └── auto_fill.py
│       ├── storage/              # File storage
│       │   └── minio_service.py
│       └── template_processing/  # HTML processing
│           └── html_parser.py
│
├── scripts/                      # Utility scripts
│   ├── run_server.sh             # Start all services
│   ├── stop_server.sh            # Stop all services
│   ├── run_ocr_service.sh        # Start OCR only
│   └── run_agent.sh              # Start agent only
│
├── templates/                    # Sample form templates
├── uploads/                      # User uploaded files
├── outputs/                      # Generated filled forms
│
├── config.py                     # Configuration management
├── Dockerfile                    # Docker image definition
├── docker-compose.yml            # Docker Compose setup
├── pyproject.toml                # Python dependencies
└── uv.lock                       # Locked dependencies
```

## 💾 Database Schema

### Entity Relationship Diagram

```
┌─────────────────┐       ┌─────────────────┐       ┌─────────────────┐
│     users       │       │    entities     │       │   templates     │
├─────────────────┤       ├─────────────────┤       ├─────────────────┤
│ id (PK)         │──┐    │ id (PK)         │       │ id (PK)         │
│ username        │  │    │ user_id (FK)────│───────│ user_id (FK)────│──┐
│ hashed_password │  │    │ name            │       │ template_path   │  │
└─────────────────┘  │    │ entity_metadata │       │ file_hash       │  │
                     │    │ doc_path        │       │ lang            │  │
                     │    └─────────────────┘       │ template_type   │  │
                     │            │                 │ form_fields     │  │
                     │            │                 │ html_structure  │  │
                     │            ▼                 └─────────────────┘  │
                     │    ┌─────────────────┐                            │
                     │    │ extracted_data  │                            │
                     │    ├─────────────────┤                            │
                     │    │ id (PK)         │                            │
                     └────│ user_id (FK)    │                            │
                          │ entity_id (FK)  │◄───────────────────────────┘
                          │ status          │   (One record per entity)
                          │ processed_file_hashes (JSON) │
                          │ extracted_toon_object (JSON) │
                          └─────────────────┘
```

### Data Storage Strategy

**Consolidated Entity Data (Issue #10 Fix)**

Each entity has **ONE** `ExtractedData` record containing:

- `processed_file_hashes`: JSON array of all processed file hashes
- `extracted_toon_object`: Merged JSON from all uploaded documents

This eliminates redundancy and reduces LLM token consumption.

```python
# Data is merged at write-time, not query-time
ExtractedDataRepository.upsert_or_merge(
    db=session,
    entity_id=entity_id,
    file_hash=new_file_hash,
    extracted_toon_object=new_data  # Merged with existing
)
```

## 🔌 API Endpoints

### Authentication

| Method | Endpoint                | Description           |
| ------ | ----------------------- | --------------------- |
| POST   | `/api/v1/auth/signup` | Register new user     |
| POST   | `/api/v1/auth/login`  | Login & get JWT token |

### Entities

| Method | Endpoint                  | Description        |
| ------ | ------------------------- | ------------------ |
| GET    | `/api/v1/entities/`     | List user entities |
| POST   | `/api/v1/entities/`     | Create new entity  |
| GET    | `/api/v1/entities/{id}` | Get entity details |
| PUT    | `/api/v1/entities/{id}` | Update entity      |
| DELETE | `/api/v1/entities/{id}` | Delete entity      |

### Entity Data

| Method | Endpoint                   | Description                    |
| ------ | -------------------------- | ------------------------------ |
| GET    | `/api/v1/entities-data/` | Get extracted data             |
| POST   | `/api/v1/entities-data/` | Upload document for extraction |

### Templates

| Method | Endpoint                   | Description          |
| ------ | -------------------------- | -------------------- |
| GET    | `/api/v1/templates/`     | List templates       |
| POST   | `/api/v1/templates/`     | Upload HTML template |
| GET    | `/api/v1/templates/{id}` | Get template details |
| DELETE | `/api/v1/templates/{id}` | Delete template      |

### Form Filling

| Method | Endpoint               | Description                    |
| ------ | ---------------------- | ------------------------------ |
| POST   | `/api/v1/form-fill/` | Fill template with entity data |

## 🚀 Getting Started

### Prerequisites

- Python 3.12+
- UV package manager
- Google Gemini API key

### Local Development

```bash
# Clone repository
git clone <repo-url>
cd backend

# Install uv
pip install uv

# Install dependencies
uv sync

# Create .env file
cp .env.example .env
# Edit .env with your GEMINI_API_KEY

# Start all services
./scripts/run_server.sh

# Or start individually:
# Terminal 1: OCR service
./scripts/run_ocr_service.sh

# Terminal 2: AI Agent
./scripts/run_agent.sh

# Terminal 3: FastAPI backend
uv run fastapi run ./api/main.py
```

### Docker Deployment

```bash
# Build and run with Docker Compose
docker-compose up -d

# Or build image manually
docker build -t ai-form-filling-backend .
docker run -d -p 8000:8000 -p 8907:8907 -p 8909:8909 \
    -e GEMINI_API_KEY=your_key \
    -v $(pwd)/uploads:/app/uploads \
    -v $(pwd)/outputs:/app/outputs \
    ai-form-filling-backend
```

## ⚙️ Configuration

### Environment Variables

| Variable                        | Default                         | Description                |
| ------------------------------- | ------------------------------- | -------------------------- |
| `DATABASE_URL`                | `sqlite:///./app.db`          | Database connection string |
| `SECRET_KEY`                  | `supersecretkey`              | JWT signing key            |
| `ALGORITHM`                   | `HS256`                       | JWT algorithm              |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `30`                          | Token expiry               |
| `UPLOAD_FILE_PATH`            | `./uploads`                   | Upload directory           |
| `OUTPUT_FILE_PATH`            | `./outputs`                   | Output directory           |
| `AGENTS_API_ENDPOINT`         | `http://localhost:8907/agent` | AI agent URL               |
| `GEMINI_API_KEY`              | -                               | Google Gemini API key      |
| `MODEL`                       | `gemini-2.5-flash`            | Gemini model name          |

## 🔄 Data Flow

### Document Upload & Extraction

```
1. User uploads document (PDF/Image)
         │
         ▼
2. Generate file hash for deduplication
         │
         ▼
3. Check if file already processed
         │
         ▼
4. OCR Service extracts text (PaddleOCR)
         │
         ▼
5. AI Agent extracts structured data (Gemini)
         │
         ▼
6. Enrich data (calculate age from DOB, etc.)
         │
         ▼
7. Upsert/merge into ExtractedData record
```

### Form Filling

```
1. User selects template + entity
         │
         ▼
2. Load template HTML & parse form fields
         │
         ▼
3. Add semantic information to fields
         │
         ▼
4. Fetch consolidated entity data
         │
         ▼
5. AI Agent maps entity data → form fields
         │
         ▼
6. Fill HTML template with mapped values
         │
         ▼
7. Save and return filled form
```

## 🧠 AI Agent Features

### Semantic Field Mapping

The HTML parser enriches form fields with semantic metadata:

```python
{
    "full_name": {
        "label": "Full Name:",
        "type": "text",
        "semantic_type": "person_name",
        "description": "Full name of the person/applicant",
        "likely_data_keys": ["full_name", "name", "applicant_name"]
    }
}
```

### Data Enrichment

Automatic field calculation during extraction:

- **Age calculation**: If DOB exists but age is missing, calculates age automatically
- Supports multiple date formats (DD/MM/YYYY, YYYY-MM-DD, etc.)

## 🔗 External Dependencies

### OCR Service

This project integrates with [plug-n-play-ocr](https://github.com/SaiDhinakar/plug-n-play-ocr) for multi-language OCR capabilities. The OCR service uses PaddleOCR as the backend and supports 80+ languages.

```bash
# Clone OCR repository
git clone https://github.com/SaiDhinakar/plug-n-play-ocr.git ocr/

# Install OCR dependencies
cd ocr && pip install -r requirements.txt
```
