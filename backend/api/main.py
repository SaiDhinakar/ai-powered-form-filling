from fastapi import FastAPI
from backend.api.v1.routers import auth, templates, form_fill
from backend.database.base import engine, Base

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="AI Powered Form Filling API", version="1.0.0")

# Include routers
app.include_router(auth.router, prefix="/api/v1/auth")
app.include_router(templates.router, prefix="/api/v1/templates")
app.include_router(form_fill.router, prefix="/api/v1/form-fill")

@app.get("/")
def read_root():
    return {"message": "Welcome to AI Powered Form Filling API"}
