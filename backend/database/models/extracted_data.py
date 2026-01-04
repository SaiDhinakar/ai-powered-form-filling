from typing import Optional, List, TYPE_CHECKING

from sqlalchemy import ForeignKey, JSON, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..base import Base

if TYPE_CHECKING:
    from .user import User
    from .entity import Entity


class ExtractedData(Base):
    """ExtractedData model representing consolidated extracted data for an entity.
    
    This model stores ONE record per entity, containing merged data from all
    uploaded documents. This reduces redundancy and token consumption for LLM.
    
    Attributes:
        id: Primary key
        user_id: Foreign key to User
        entity_id: Foreign key to Entity (unique - one record per entity)
        status: Status of extraction (1=success, 0=pending/failed)
        processed_file_hashes: JSON list of file hashes that have been processed
        extracted_toon_object: JSON object containing merged extracted data
    """
    __tablename__ = "extracted_data"
    
    # Primary Key
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    
    # Foreign Keys
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    entity_id: Mapped[int] = mapped_column(ForeignKey("entities.id", ondelete="CASCADE"), nullable=False, index=True, unique=True)
    
    # Fields
    status: Mapped[int] = mapped_column(Integer, default=0, nullable=False)  # 1=success, 0=pending/failed
    processed_file_hashes: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True, default=list)  # List of processed file hashes
    extracted_toon_object: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    
    # Relationships
    entity: Mapped["Entity"] = relationship("Entity", back_populates="extracted_data")
    
    def __repr__(self) -> str:
        return f"<ExtractedData(id={self.id}, user_id={self.user_id}, entity_id={self.entity_id}, status={self.status})>"