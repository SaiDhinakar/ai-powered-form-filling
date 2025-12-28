from typing import Optional, TYPE_CHECKING
from sqlalchemy import ForeignKey
import datetime
from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column

from ..base import Base

if TYPE_CHECKING:
    from .user import User

class Template(Base):
    """
    Template model representing form templates.
    
    Attributes:
        id: Primary key
        user_id: Foreign key to User
        pdf_path: Path to the template file (PDF)
        file_hash: Hash of the template file for integrity
        lang: Language of the template
        form_fields: JSON field storing form field metadata
        pdf_data: Extracted pdf data for additional informations (incase fields missed the checkbox, radio keys)
    """
    __tablename__ = "templates"
    
    # Primary Key
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    
    # Fields
    pdf_path: Mapped[str] = mapped_column(Text, nullable=False)
    file_hash: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    lang: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    form_fields: Mapped[Optional[dict]] = mapped_column(Text, nullable=True)  # JSON stored as text
    pdf_data: Mapped[Optional[dict]] = mapped_column(Text, nullable=True)  # JSON stored as text
    created_at: Mapped[datetime.datetime] = mapped_column(default=datetime.datetime.now(datetime.timezone.utc), nullable=False)
    
    # Forigen key entity id
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    def __repr__(self) -> str:
        return f"<Template(id={self.id}, file_hash='{self.file_hash}', lang='{self.lang}')>"