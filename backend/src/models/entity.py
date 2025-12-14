"""Entity model for managing people/entities with extracted data."""

from datetime import datetime
import random
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON, Index
from sqlalchemy.orm import relationship, Session as DBSession

from src.core.database import Base


def generate_unique_entity_id(db: DBSession, max_retries: int = 5) -> int:
    """
    Generate a unique 6-digit entity ID (100000-999999).
    
    Args:
        db: Database session
        max_retries: Maximum number of retry attempts
        
    Returns:
        int: Unique 6-digit entity ID
        
    Raises:
        ValueError: If unable to generate unique ID after max_retries
    """
    for attempt in range(max_retries):
        # Generate 6-digit number (100000-999999)
        entity_id = random.randint(100000, 999999)
        
        # Check if ID already exists
        existing = db.query(Entity).filter(Entity.id == entity_id).first()
        if not existing:
            return entity_id
    
    raise ValueError(f"Failed to generate unique entity ID after {max_retries} attempts")


class Entity(Base):
    """Entity model for storing people/entities with their extracted data."""
    
    __tablename__ = "entities"
    
    # Primary key: 6-digit unique ID (100000-999999)
    id = Column(Integer, primary_key=True, autoincrement=False)
    
    # Foreign key to user
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Entity information
    name = Column(String(255), nullable=False, index=True)
    extracted_text = Column(Text, nullable=True)  # Full extracted text from PDF
    
    # Metadata storage (JSON for flexible data)
    entity_metadata = Column("metadata", JSON, nullable=True)  # Additional info: phone, email, address, etc.
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship("User", backref="entities")
    
    # Indexes for efficient querying
    __table_args__ = (
        Index('idx_user_name', 'user_id', 'name'),
        Index('idx_user_created', 'user_id', 'created_at'),
    )
    
    def __repr__(self) -> str:
        return f"<Entity(id={self.id}, name='{self.name}', user_id={self.user_id})>"
    
    @classmethod
    def create_entity(cls, db: DBSession, user_id: int, name: str, extracted_text: str = None, metadata: dict = None) -> "Entity":
        """
        Create a new entity with auto-generated 6-digit ID.
        
        Args:
            db: Database session
            user_id: ID of the owning user
            name: Entity name
            extracted_text: Extracted text content
            metadata: Additional metadata
            
        Returns:
            Entity: Created entity instance
        """
        entity_id = generate_unique_entity_id(db)
        
        entity = cls(
            id=entity_id,
            user_id=user_id,
            name=name,
            extracted_text=extracted_text,
            entity_metadata=metadata or {}
        )
        
        return entity
