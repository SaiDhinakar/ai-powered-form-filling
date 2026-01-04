from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile
from dotenv import load_dotenv
import hashlib
from pathlib import Path
import sys

# Add backend directory to Python path
backend_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(backend_dir))

from database.session import get_db, Session
from database.repository import ExtractedDataRepository
from api.v1.routers.auth import get_current_user
from api.v1.models import User
from src.services.data_extraction.extract_contents import extract_and_save_organize_data
from config import settings

load_dotenv()

router = APIRouter(prefix="/entities-data", tags=["entities-data"])

def generate_file_hash(file_content: bytes) -> str:
    return hashlib.sha256(file_content).hexdigest()

@router.get("/")
async def list_entity_data(
    entity_id: int,
    db: Session = Depends(get_db),
):
    """
    Get consolidated data for a specific entity.
    """
    return ExtractedDataRepository.get_single_by_entity(db, entity_id)

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_entity_data(
    entity_id: int,
    lang: str = 'en',
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Create or update extracted data record for an entity.
    Data is merged into a single consolidated record per entity.
    """
    file_content = await file.read()
    file_hash = generate_file_hash(file_content)

    # Check if this file has already been processed for this entity
    if ExtractedDataRepository.is_file_processed(db, entity_id, file_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Extracted data with this file already exists."
        )
    
    # Store file 
    try:
        # object_path = settings.ENTITY_DATA_STORAGE.upload_file(
        #                     user_id=current_user.id,
        #                     entity_id=entity_id,
        #                     file_data=file.file,
        #                     file_name=file.filename
        #                 )

        # file_path = settings.ENTITY_DATA_STORAGE.get_file_path(object_path)

        file_path = Path(settings.UPLOAD_FILE_PATH) / f"{current_user.id}" / f"{entity_id}" / f"{file.filename}"
        file_path.parent.mkdir(parents=True, exist_ok=True)

        with open(file_path, "wb") as f:
            f.write(file_content)

        extraction_status = extract_and_save_organize_data(db, current_user.id, entity_id, file_path, lang=lang)

        return {"status": extraction_status}

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error uploading file to storage."
        )
