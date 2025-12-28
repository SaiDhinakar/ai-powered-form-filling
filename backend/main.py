from fastapi import FastAPI
from src.services.pdf_doc_service.routes import router as pdf_router

app = FastAPI(title="Backend API")

app.include_router(pdf_router)
