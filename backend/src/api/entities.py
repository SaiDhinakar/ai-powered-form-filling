"""Entity management API endpoints."""

import logging
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_

from src.core.database import get_db
from src.core.deps import get_current_user
from src.models.user import User
from src.models.entity import Entity
from src.schemas.entity import (
    EntityCreate,
    EntityUpdate,
    EntityResponse,
    EntityListResponse,
    EntitySearchRequest,
    EntitySearchResponse,
    EntitySearchResult
)
from src.schemas.common import MessageResponse
from src.services.embedding_service import embedding_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/entities", tags=["Entities"])


@router.post("", response_model=EntityResponse, status_code=status.HTTP_201_CREATED)
async def create_entity(
    entity_data: EntityCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new entity for the current user.
    
    Args:
        entity_data: Entity creation data
        user: Current authenticated user
        db: Database session
        
    Returns:
        EntityResponse: Created entity
    """
    try:
        # Create entity with auto-generated 6-digit ID
        entity = Entity.create_entity(
            db=db,
            user_id=user.id,
            name=entity_data.name,
            metadata=entity_data.metadata
        )
        
        db.add(entity)
        db.commit()
        db.refresh(entity)
        
        logger.info(f"Created entity {entity.id} for user {user.id}")
        
        return entity
        
    except ValueError as e:
        logger.error(f"Failed to create entity: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Unexpected error creating entity: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create entity"
        )


@router.get("", response_model=EntityListResponse)
async def list_entities(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    search: str = Query(None, description="Search by name"),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List all entities for the current user.
    
    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return
        search: Optional search query for name
        user: Current authenticated user
        db: Database session
        
    Returns:
        EntityListResponse: List of entities with total count
    """
    query = db.query(Entity).filter(Entity.user_id == user.id)
    
    # Apply search filter if provided
    if search:
        query = query.filter(Entity.name.ilike(f"%{search}%"))
    
    # Get total count
    total = query.count()
    
    # Get paginated results
    entities = query.order_by(Entity.created_at.desc()).offset(skip).limit(limit).all()
    
    return EntityListResponse(
        total=total,
        entities=entities
    )


@router.get("/{entity_id}", response_model=EntityResponse)
async def get_entity(
    entity_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get a specific entity by ID.
    
    Args:
        entity_id: Entity ID (6-digit)
        user: Current authenticated user
        db: Database session
        
    Returns:
        EntityResponse: Entity details
        
    Raises:
        HTTPException: If entity not found or access denied
    """
    entity = db.query(Entity).filter(
        Entity.id == entity_id,
        Entity.user_id == user.id
    ).first()
    
    if not entity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Entity not found"
        )
    
    return entity


@router.put("/{entity_id}", response_model=EntityResponse)
async def update_entity(
    entity_id: int,
    entity_data: EntityUpdate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update an entity.
    
    Args:
        entity_id: Entity ID
        entity_data: Update data
        user: Current authenticated user
        db: Database session
        
    Returns:
        EntityResponse: Updated entity
        
    Raises:
        HTTPException: If entity not found or access denied
    """
    entity = db.query(Entity).filter(
        Entity.id == entity_id,
        Entity.user_id == user.id
    ).first()
    
    if not entity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Entity not found"
        )
    
    # Update fields if provided
    if entity_data.name is not None:
        entity.name = entity_data.name
    
    if entity_data.metadata is not None:
        # Merge with existing metadata
        existing_metadata = entity.metadata or {}
        existing_metadata.update(entity_data.metadata)
        entity.metadata = existing_metadata
    
    try:
        # Update embedding if text exists
        if entity.extracted_text:
            embedding_service.update_entity_embedding(
                user_id=user.id,
                entity_id=entity.id,
                text=entity.extracted_text,
                metadata={
                    "name": entity.name,
                    **(entity.metadata or {})
                }
            )
        
        db.commit()
        db.refresh(entity)
        
        logger.info(f"Updated entity {entity_id} for user {user.id}")
        
        return entity
        
    except Exception as e:
        logger.error(f"Failed to update entity {entity_id}: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update entity"
        )


@router.delete("/{entity_id}", response_model=MessageResponse)
async def delete_entity(
    entity_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete an entity.
    
    Args:
        entity_id: Entity ID
        user: Current authenticated user
        db: Database session
        
    Returns:
        MessageResponse: Deletion confirmation
        
    Raises:
        HTTPException: If entity not found or access denied
    """
    entity = db.query(Entity).filter(
        Entity.id == entity_id,
        Entity.user_id == user.id
    ).first()
    
    if not entity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Entity not found"
        )
    
    try:
        # Delete embedding from ChromaDB
        embedding_service.delete_entity_embedding(
            user_id=user.id,
            entity_id=entity.id
        )
        
        # Delete from database
        db.delete(entity)
        db.commit()
        
        logger.info(f"Deleted entity {entity_id} for user {user.id}")
        
        return MessageResponse(message="Entity deleted successfully")
        
    except Exception as e:
        logger.error(f"Failed to delete entity {entity_id}: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete entity"
        )


@router.post("/search", response_model=EntitySearchResponse)
async def search_entities(
    search_request: EntitySearchRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Semantic search for entities using embeddings.
    
    Args:
        search_request: Search parameters
        user: Current authenticated user
        db: Database session
        
    Returns:
        EntitySearchResponse: Search results with similarity scores
    """
    try:
        # Perform semantic search
        similar_entities = embedding_service.search_similar_entities(
            user_id=user.id,
            query=search_request.query,
            limit=search_request.limit,
            min_score=search_request.min_score
        )
        
        # Fetch entity details from database
        results = []
        for entity_id, similarity_score, matched_text in similar_entities:
            entity = db.query(Entity).filter(
                Entity.id == entity_id,
                Entity.user_id == user.id
            ).first()
            
            if entity:
                # Extract a relevant excerpt (first 200 chars)
                excerpt = matched_text[:200] + "..." if len(matched_text) > 200 else matched_text
                
                results.append(EntitySearchResult(
                    entity=entity,
                    similarity_score=similarity_score,
                    matched_text=excerpt
                ))
        
        logger.info(f"Search for '{search_request.query}' returned {len(results)} results")
        
        return EntitySearchResponse(
            query=search_request.query,
            total=len(results),
            results=results
        )
        
    except Exception as e:
        logger.error(f"Search failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Search failed"
        )
