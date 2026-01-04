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
        template_path: Path to the template file (HTML or PDF)
        file_hash: Hash of the template file for integrity
        lang: Language of the template
        template_type: Type of template ('html' or 'pdf')
        form_fields: JSON field storing form field metadata
        html_structure: Parsed HTML structure with field mappings
    """
    __tablename__ = "templates"
    
    # Primary Key
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    
    # Fields
    template_path: Mapped[str] = mapped_column(Text, nullable=False)
    file_hash: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    lang: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    template_type: Mapped[str] = mapped_column(String(10), default='html', nullable=False)  # 'html' or 'pdf'
    form_fields: Mapped[Optional[dict]] = mapped_column(Text, nullable=True)  # JSON stored as text
    html_structure: Mapped[Optional[dict]] = mapped_column(Text, nullable=True)  # Parsed HTML structure
    created_at: Mapped[datetime.datetime] = mapped_column(default=datetime.datetime.now(datetime.timezone.utc), nullable=False)
    
    # Foreign key to user
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    def __repr__(self) -> str:
        return f"<Template(id={self.id}, file_hash='{self.file_hash}', type='{self.template_type}', lang='{self.lang}')>"