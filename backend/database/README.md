# Database Schema

This directory contains the SQLAlchemy database schema for the AI-Powered Form Filling application.

## Structure

```
database/
├── __init__.py           # Package initialization with exports
├── base.py              # Base configuration and engine setup
├── schema.py            # Legacy schema file (backwards compatibility)
├── models/              # Database models
│   ├── __init__.py
│   ├── user.py          # User model
│   ├── entity.py        # Entity model
│   ├── template.py      # Template model
│   └── extracted_data.py # ExtractedData model
└── README.md            # This file
```

## Models

### User

Represents system users with authentication credentials.

**Fields:**

- `id` (int, PK): Auto-incrementing primary key
- `username` (str): Unique username
- `hashed_password` (str): Hashed password for authentication

**Relationships:**

- `entities`: One-to-many relationship with Entity
- `extracted_data`: One-to-many relationship with ExtractedData

### Entity

Represents user entities (documents, forms, etc.).

**Fields:**

- `id` (int, PK): Auto-incrementing primary key
- `user_id` (int, FK): Foreign key to User
- `name` (str): Entity name
- `metadata` (JSON): JSON metadata for the entity
- `doc_path` (str): Path to the document

**Relationships:**

- `user`: Many-to-one relationship with User
- `extracted_data`: One-to-many relationship with ExtractedData

### Template

Represents form templates.

**Fields:**

- `id` (int, PK): Auto-incrementing primary key
- `path` (str): Path to the template file
- `file_hash` (str): Hash of the template file (unique)
- `lang` (str): Language of the template
- `html_code` (str): HTML code of the template

### ExtractedData

Represents extracted data from documents.

**Fields:**

- `id` (int, PK): Auto-incrementing primary key
- `user_id` (int, FK): Foreign key to User
- `entity_id` (int, FK): Foreign key to Entity
- `status` (int): Status of extraction (1=success, 0=pending/failed)
- `file_hash` (str): Hash of the processed file
- `extracted_toon_object` (JSON): JSON object containing extracted data

**Relationships:**

- `user`: Many-to-one relationship with User
- `entity`: Many-to-one relationship with Entity

## Usage

### Initialize Database

```python
from database import init_db

# Create all tables
init_db()
```

### Using Models

```python
from database import SessionLocal, User, Entity, ExtractedData

# Create a session
db = SessionLocal()

# Create a new user
user = User(username="john_doe", hashed_password="hashed_pwd_here")
db.add(user)
db.commit()

# Create an entity for the user
entity = Entity(
    user_id=user.id,
    name="My Document",
    metadata={"type": "form", "version": 1},
    doc_path="/path/to/document.pdf"
)
db.add(entity)
db.commit()

# Query users
users = db.query(User).all()
```

### With Dependency Injection (FastAPI)

```python
from fastapi import Depends
from database import get_db
from sqlalchemy.orm import Session

@app.get("/users")
def list_users(db: Session = Depends(get_db)):
    return db.query(User).all()
```

## Database Configuration

Set the `DATABASE_URL` environment variable in your `.env` file:

```bash
# SQLite (default)
DATABASE_URL=sqlite:///./app.db

# PostgreSQL
DATABASE_URL=postgresql://user:password@localhost/dbname

# MySQL
DATABASE_URL=mysql://user:password@localhost/dbname
```

## Migration Guide

For existing code using the old schema:

**Before:**

```python
from database.schema import engine
```

**After:**

```python
from database import engine
# or
from database.base import engine
```

All models are now available from the main database package:

```python
from database import User, Entity, Template, ExtractedData
```
