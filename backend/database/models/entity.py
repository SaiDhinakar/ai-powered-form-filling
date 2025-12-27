from typing import List, Optional, TYPE_CHECKING

from sqlalchemy import ForeignKey, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..base import Base

if TYPE_CHECKING:
    from .user import User
    from .extracted_data import ExtractedData


class Entity(Base):
    """
    Entity model representing user entities (documents, forms, etc.).
    
    Attributes:
        id: Primary key
        user_id: Foreign key to User
        name: Entity name
        entity_metadata: JSON metadata for the entity
        doc_path: Path to the document
    """
    __tablename__ = "entities"
    
    # Primary Key
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    
    # Foreign Keys
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Fields
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    entity_metadata: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    doc_path: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="entities")
    
    extracted_data: Mapped[List["ExtractedData"]] = relationship(
        "ExtractedData",
        back_populates="entity",
        cascade="all, delete-orphan"
    )
    
    def __repr__(self) -> str:
        return f"<Entity(id={self.id}, name='{self.name}', user_id={self.user_id})>"