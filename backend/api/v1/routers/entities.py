from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pathlib import Path
import sys
import os

# Add backend directory to Python path
backend_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(backend_dir))

from database.session import get_db, Session
from database.repository import EntityRepository
from api.v1.models import User
from api.v1.routers.auth import get_current_user
from config import settings

router = APIRouter(tags=["entities"])

from config import settings
import os

def _attach_documents(entity, user_id: int):
    """Helper to attach documents from filesystem to entity dict."""
    if not entity:
        return None
    
    # Convert SQLAlchemy model to dict if needed
    entity_dict = {c.name: getattr(entity, c.name) for c in entity.__table__.columns}
    
    # Define path: uploads/{user_id}/{entity_id}
    entity_dir = Path(settings.UPLOAD_FILE_PATH) / str(user_id) / str(entity.id)
    
    documents = []
    if entity_dir.exists() and entity_dir.is_dir():
        for f in entity_dir.iterdir():
            if f.is_file() and not f.name.startswith('.'):
                documents.append({
                    "id": f.name, # Use filename as ID for now
                    "name": f.name,
                    "filename": f.name,
                    "size": f.stat().st_size,
                    "type": "application/pdf" if f.suffix == ".pdf" else "image/jpeg", # naive type guess
                    "language": "en" # default/unknown
                })
    
    entity_dict["documents"] = documents
    return entity_dict

@router.get("/")
async def list_entities(
    limit: int = 100,
    offset: int = 0,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    List entities with pagination.
    """
    entities = EntityRepository.get_by_user(db, current_user.id, skip=offset, limit=limit)
    return [_attach_documents(e, current_user.id) for e in entities]


@router.get("/{entity_id}")
async def get_entity(
    entity_id: int, 
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get a single entity by id.
    """
    entity = EntityRepository.get_by_id(db, entity_id)
    if not entity:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Entity not found")
    
    # Security check
    if entity.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
        
    return _attach_documents(entity, current_user.id)


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