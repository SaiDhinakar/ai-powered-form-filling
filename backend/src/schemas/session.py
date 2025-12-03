"""Pydantic schemas for session-related requests and responses."""

from datetime import datetime
from pydantic import BaseModel


class SessionResponse(BaseModel):
    """Schema for session response."""
    id: int
    user_id: int
    session_id: str
    created_at: datetime
    expires_at: datetime
    is_expired: bool
    
    class Config:
        from_attributes = True
