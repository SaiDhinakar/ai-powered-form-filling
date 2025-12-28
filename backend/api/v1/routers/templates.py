from fastapi import APIRouter, File, UploadFile, Depends, HTTPException, Form
from pathlib import Path
import sys
import hashlib
import shutil
import os

backend_path = Path(__file__).resolve().parent.parent.parent.parent
sys.path.append(str(backend_path))

from database.session import Session, get_db
from database.repository import TemplateRepository
from api.v1.routers.auth import get_current_user
from src.services.data_extraction.pdf_form_utils import get_template_metadata
from config import settings

router = APIRouter(tags=["Templates"])


# List all templates for the user
@router.get("/template")
def get_templates(
    limit: int = 10,
    skip: int = 0,
    user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    templates = TemplateRepository.get_all(db, user.id, skip=skip, limit=limit)
    return {"templates": [template.__dict__ for template in templates]}

@router.post("/template")
async def create_template(
    file: UploadFile = File(...),
    lang: str = Form(None),
    user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Compute hash
    file_content = await file.read()
    file_hash = hashlib.sha256(file_content).hexdigest()

    # If file with hash exists, return existing
    existing_template = TemplateRepository.get_by_hash(db, file_hash)
    if existing_template and existing_template.user_id == user.id:
        return {"template": existing_template.__dict__}

    # Prepare directory
    user_dir = Path(settings.UPLOAD_FILE_PATH) / "templates" / str(user.id)
    user_dir.mkdir(parents=True, exist_ok=True)
    file_path = user_dir / f"{file_hash}.pdf"
    # Save file
    with open(file_path, "wb") as f:
        f.write(file_content)

    # Extract metadata
    metadata = get_template_metadata(str(file_path), lang=lang or 'en')
    form_fields = metadata.get("form_fields", {})
    pdf_data = metadata.get("pdf_data", {})
    
    # Store in DB
    template = TemplateRepository.create(
        db=db,
        user_id=user.id,
        path=str(file_path),
        file_hash=file_hash,
        lang=lang,
        form_fields=form_fields,
        pdf_data=pdf_data
    )
    return {"template": template.__dict__}


# Update template file or metadata
@router.put("/template")
async def update_template(
    template_id: int = Form(...),
    file: UploadFile = File(None),
    lang: str = Form(None),
    user_id=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    template = TemplateRepository.get_by_id(db, template_id)
    if not template or template.user_id != user_id:
        raise HTTPException(status_code=404, detail="Template not found")

    file_hash = template.file_hash
    file_path = template.path
    # If new file, update file and hash
    if file:
        file_content = await file.read()
        new_file_hash = hashlib.sha256(file_content).hexdigest()
        user_dir = Path(settings.UPLOAD_FILE_PATH) / "templates" / str(user_id)
        user_dir.mkdir(parents=True, exist_ok=True)
        new_file_path = user_dir / f"{new_file_hash}.pdf"
        with open(new_file_path, "wb") as f:
            f.write(file_content)
        # Remove old file if different
        if file_path != str(new_file_path) and os.path.exists(file_path):
            os.remove(file_path)
        file_hash = new_file_hash
        file_path = str(new_file_path)

    # Optionally, re-extract metadata if file changed or lang changed
    metadata = get_template_metadata(str(file_path), lang=lang or template.lang or 'en')
    form_fields = metadata.get("form_fields", {})
    pdf_data = metadata.get("pdf_data", {})

    # Update DB (assuming update method supports these fields, else update directly)
    updated_template = TemplateRepository.update(
        db=db,
        entity_id=template_id,
        name=None,
        entity_metadata=form_fields,
        doc_path=file_path
    )
    # Directly update fields if needed
    updated_template.file_hash = file_hash
    updated_template.path = file_path
    updated_template.form_fields = form_fields
    updated_template.pdf_data = pdf_data
    if lang is not None:
        updated_template.lang = lang
    db.commit()
    db.refresh(updated_template)
    return {"template": updated_template.__dict__}


# Delete template and its file
@router.delete("/template")
def delete_template(
    template_id: int,
    user_id=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    template = TemplateRepository.get_by_id(db, template_id)
    if not template or template.user_id != user_id:
        raise HTTPException(status_code=404, detail="Template not found")
    # Delete file
    if template.path and os.path.exists(template.path):
        os.remove(template.path)
    # Delete DB record
    TemplateRepository.delete(db, template_id)
    return {"message": "Template deleted"}
