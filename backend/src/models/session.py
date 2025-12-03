"""Session model for managing user sessions."""

from datetime import datetime, timedelta
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
import uuid

from src.core.database import Base


class Session(Base):
    """Session model for tracking user sessions."""
    
    __tablename__ = "sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    session_id = Column(String(36), unique=True, index=True, nullable=False, default=lambda: str(uuid.uuid4()))
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    
    # Relationships
    user = relationship("User", backref="sessions")
    
    def __repr__(self) -> str:
        return f"<Session(id={self.id}, session_id='{self.session_id}', user_id={self.user_id})>"
    
    @property
    def is_expired(self) -> bool:
        """Check if the session has expired."""
        return datetime.utcnow() > self.expires_at
    
    @classmethod
    def create_session(cls, user_id: int, duration_hours: int = 24):
        """
        Create a new session for a user.
        
        Args:
            user_id: ID of the user
            duration_hours: Session duration in hours (default: 24)
            
        Returns:
            Session: New session instance
        """
        return cls(
            user_id=user_id,
            session_id=str(uuid.uuid4()),
            expires_at=datetime.utcnow() + timedelta(hours=duration_hours)
        )
