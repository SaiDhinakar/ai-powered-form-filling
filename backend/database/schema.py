"""
Database schema module.

This module provides backwards compatibility and easy imports for database models.
For new code, prefer importing from database.models or database.base directly.
"""
from .base import Base, engine, get_db, init_db, SessionLocal
from .models import User, Entity, Template, ExtractedData

__all__ = [
    "Base",
    "engine",
    "get_db",
    "init_db",
    "SessionLocal",
    "User",
    "Entity",
    "Template",
    "ExtractedData",
]