from typing import List, Optional, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pathlib import Path
import sys

# Add backend directory to Python path
backend_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(backend_dir))

from database.session import get_db, Session
from database.repository import EntityRepository
from api.v1.models import User, EntityResponse
from api.v1.routers.auth import get_current_user

router = APIRouter(prefix="/entities", tags=["entities"])

@router.get("/", response_model=List[EntityResponse])
def list_entities(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    List entities with pagination.
    """
    entities = EntityRepository.get_by_user(db, current_user.id, skip=skip, limit=limit)
    return entities


@router.get("/{entity_id}")
async def get_entity(entity_id: int, db: Session = Depends(get_db)):
    """
    Get a single entity by id.
    """
    entity = EntityRepository.get_by_id(db, entity_id)
    if not entity:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Entity not found")
    return entity


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_entity(
    entity_name: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Create a new entity.
    """
    return EntityRepository.create(db, current_user.id, entity_name)


@router.put("/{entity_id}")
async def update_entity(
    entity_id: int,
    name: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """
    Update an existing entity.
    """
    updated = EntityRepository.update(db, entity_id, name)
    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Entity not found")
    return updated


@router.delete("/{entity_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_entity(entity_id: int, db: Session = Depends(get_db)):
    """
    Delete an entity.
    """
    deleted = EntityRepository.delete(db, entity_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Entity not found")
    return None