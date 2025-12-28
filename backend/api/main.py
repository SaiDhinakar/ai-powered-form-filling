from fastapi import FastAPI
from pathlib import Path
import sys

# Add backend directory to Python path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from api.v1.routers import auth, templates, form_fill
from database import init_db

init_db()

app = FastAPI(title="AI Powered Form Filling API", version="1.0.0")

# Include routers
app.include_router(auth.router, prefix="/api/v1/auth")
app.include_router(templates.router, prefix="/api/v1/templates")
app.include_router(form_fill.router, prefix="/api/v1/form-fill")

@app.get("/")
def read_root():
    return {"message": "Welcome to AI Powered Form Filling API"}
