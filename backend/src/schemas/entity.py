"""Pydantic schemas for entity management."""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, field_validator


class EntityBase(BaseModel):
    """Base schema for entity."""
    name: str = Field(..., min_length=1, max_length=255, description="Entity name")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Additional metadata (phone, email, etc.)")


class EntityCreate(EntityBase):
    """Schema for creating a new entity."""
    pass


class EntityUpdate(BaseModel):
    """Schema for updating an entity."""
    name: Optional[str] = Field(None, min_length=1, max_length=255, description="Entity name")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


class EntityResponse(EntityBase):
    """Schema for entity response."""
    id: int = Field(..., ge=100000, le=999999, description="6-digit entity ID")
    user_id: int
    extracted_text: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    model_config = {"from_attributes": True}


class EntityListResponse(BaseModel):
    """Schema for list of entities."""
    total: int
    entities: List[EntityResponse]


class EntitySearchRequest(BaseModel):
    """Schema for semantic search request."""
    query: str = Field(..., min_length=1, description="Search query text")
    limit: int = Field(default=10, ge=1, le=100, description="Maximum number of results")
    min_score: float = Field(default=0.5, ge=0.0, le=1.0, description="Minimum similarity score")


class EntitySearchResult(BaseModel):
    """Schema for individual search result."""
    entity: EntityResponse
    similarity_score: float = Field(..., ge=0.0, le=1.0, description="Cosine similarity score")
    matched_text: Optional[str] = Field(None, description="Excerpt of matched text")


class EntitySearchResponse(BaseModel):
    """Schema for search results."""
    query: str
    total: int
    results: List[EntitySearchResult]
