from fastapi import FastAPI, Depends
from pathlib import Path
import sys

# Add backend directory to Python path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from api.v1.routers import auth, templates, form_fill, entities, user_data
from api.v1.routers.auth import get_current_user
from database import init_db

init_db()

# PROBE THE DATABASE IMMEDIATELY
from database.base import engine
from sqlalchemy import text
with engine.connect() as conn:
    try:
        print("DEBUG: PROBING entities TABLE...")
        result = conn.execute(text("SELECT count(*) FROM entities"))
        print(f"DEBUG: PROBE SUCCESS. Count: {result.scalar()}")
        result = conn.execute(text("SELECT count(*) FROM users"))
        print(f"DEBUG: PROBE USERS SUCCESS. Count: {result.scalar()}")
    except Exception as e:
        print(f"DEBUG: PROBE FAILED: {e}")

app = FastAPI(title="AI Powered Form Filling API", version="1.0.0")

from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from config import settings
import os

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ensure directories exist
os.makedirs(settings.UPLOAD_FILE_PATH, exist_ok=True)
os.makedirs(settings.OUTPUT_FILE_PATH, exist_ok=True)

# Mount static files
app.mount("/static/uploads", StaticFiles(directory=settings.UPLOAD_FILE_PATH), name="uploads")
app.mount("/static/outputs", StaticFiles(directory=settings.OUTPUT_FILE_PATH), name="outputs")

# Include routers
# Auth router remains public (login/signup)
app.include_router(auth.router, prefix="/api/v1/auth")
# All other routers require a valid authenticated user
auth_dep = [Depends(get_current_user)]
app.include_router(templates.router, prefix="/api/v1/templates", dependencies=auth_dep)
app.include_router(form_fill.router, prefix="/api/v1/form-fill", dependencies=auth_dep)
app.include_router(entities.router, prefix="/api/v1/entities", dependencies=auth_dep)
app.include_router(user_data.router, prefix="/api/v1/entities-data", dependencies=auth_dep)

@app.get("/")
def read_root():
    return {"message": "Welcome to AI Powered Form Filling API"}
