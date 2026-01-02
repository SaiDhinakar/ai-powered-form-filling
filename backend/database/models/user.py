from typing import List, TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..base import Base

if TYPE_CHECKING:
    from .entity import Entity
    from .extracted_data import ExtractedData


class User(Base):
    """
    User model representing system users.
    
    Attributes:
        id: Primary key
        username: Unique username
        hashed_password: Hashed password for authentication
    """
    __tablename__ = "users"
    
    # Primary Key
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    
    # Fields
    email: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    
    # Relationships
    entities: Mapped[List["Entity"]] = relationship(
        "Entity",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    
    def __repr__(self) -> str:
        return f"<User(id={self.id}, email='{self.email}')>"