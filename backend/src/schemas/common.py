"""Common response schemas."""

from pydantic import BaseModel
from typing import Any, Optional


class MessageResponse(BaseModel):
    """Generic message response."""
    message: str
    detail: Optional[str] = None


class ErrorResponse(BaseModel):
    """Error response schema."""
    error: str
    detail: Optional[str] = None
    status_code: int


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    version: str
    timestamp: str
