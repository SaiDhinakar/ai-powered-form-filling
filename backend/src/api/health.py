"""Health check router."""

from fastapi import APIRouter
from datetime import datetime

from src.schemas.common import HealthResponse
from src.core.config import settings

router = APIRouter(tags=["Health"])


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint.
    
    Returns:
        HealthResponse: API health status
    """
    return HealthResponse(
        status="healthy",
        version=settings.APP_VERSION,
        timestamp=datetime.utcnow().isoformat()
    )


@router.get("/")
async def root():
    """
    Root endpoint.
    
    Returns:
        dict: Welcome message
    """
    return {
        "message": "AI-Powered Form Filling API",
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "health": "/health"
    }
