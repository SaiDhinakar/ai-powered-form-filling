from fastapi import APIRouter, File, UploadFile, Depends, HTTPException, Form
from fastapi.responses import HTMLResponse
from pathlib import Path
import sys
import hashlib
import os

backend_path = Path(__file__).resolve().parent.parent.parent.parent
sys.path.append(str(backend_path))

from database.session import Session, get_db
from database.repository import TemplateRepository
from api.v1.routers.auth import get_current_user
from src.services.template_processing.html_parser import parse_html_template
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
    """
    Upload a new HTML template.
    Accepts .html files for flexible form filling.
    """
    # Validate file type - only HTML files
    if not file.filename.endswith('.html'):
        raise HTTPException(status_code=400, detail="Only HTML files are supported. Please upload an .html file.")
    
    # Compute hash
    file_content = await file.read()
    file_hash = hashlib.sha256(file_content).hexdigest()

    # If file with hash exists for this user, return existing
    existing_template = TemplateRepository.get_by_hash(db, file_hash)
    if existing_template:
        if existing_template.user_id == user.id:
            return {"template": existing_template.__dict__}
        else:
            # Template exists but belongs to another user
            raise HTTPException(
                status_code=409, 
                detail="This template has already been uploaded. Please use a different file or modify the template."
            )

    # Prepare directory
    user_dir = Path(settings.UPLOAD_FILE_PATH) / "templates" / str(user.id)
    user_dir.mkdir(parents=True, exist_ok=True)
    file_path = user_dir / f"{file_hash}.html"
    
    # Save file
    with open(file_path, "wb") as f:
        f.write(file_content)

    # Parse HTML template to extract form fields
    print(f"Parsing HTML template: {file_path}")
    try:
        html_content = file_content.decode('utf-8')
        parsed_data = parse_html_template(html_content)
        form_fields = parsed_data.get("form_fields", {})
        html_structure = parsed_data.get("html_structure", {})
        print(f"Extracted {len(form_fields)} form fields from HTML template")
    except Exception as e:
        # Cleanup file on error
        if file_path.exists():
            os.remove(file_path)
        raise HTTPException(status_code=400, detail=f"Failed to parse HTML template: {str(e)}")
    
    # Store in DB
    template = TemplateRepository.create(
        db=db,
        user_id=user.id,
        path=str(file_path),
        file_hash=file_hash,
        lang=lang or 'en',
        template_type='html',
        form_fields=form_fields,
        html_structure=html_structure
    )
    return {"template": template.__dict__}


# Update template file or metadata
@router.put("/template")
async def update_template(
    template_id: int = Form(...),
    file: UploadFile = File(None),
    lang: str = Form(None),
    user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update an existing HTML template."""
    template = TemplateRepository.get_by_id(db, template_id)
    if not template or template.user_id != user.id:
        raise HTTPException(status_code=404, detail="Template not found")

    file_hash = template.file_hash
    file_path = template.template_path
    form_fields = template.form_fields
    html_structure = template.html_structure
    
    # If new file, update file and hash
    if file:
        # Validate file type
        if not file.filename.endswith('.html'):
            raise HTTPException(status_code=400, detail="Only HTML files are supported")
        
        file_content = await file.read()
        new_file_hash = hashlib.sha256(file_content).hexdigest()
        user_dir = Path(settings.UPLOAD_FILE_PATH) / "templates" / str(user.id)
        user_dir.mkdir(parents=True, exist_ok=True)
        new_file_path = user_dir / f"{new_file_hash}.html"
        
        with open(new_file_path, "wb") as f:
            f.write(file_content)
        
        # Remove old file if different
        if file_path != str(new_file_path) and os.path.exists(file_path):
            os.remove(file_path)
        
        file_hash = new_file_hash
        file_path = str(new_file_path)
        
        # Re-parse HTML template
        try:
            html_content = file_content.decode('utf-8')
            parsed_data = parse_html_template(html_content)
            form_fields = parsed_data.get("form_fields", {})
            html_structure = parsed_data.get("html_structure", {})
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to parse HTML template: {str(e)}")

    # Update DB record
    import json
    template.file_hash = file_hash
    template.template_path = file_path
    template.form_fields = json.dumps(form_fields) if isinstance(form_fields, dict) else form_fields
    template.html_structure = json.dumps(html_structure) if isinstance(html_structure, dict) else html_structure
    template.template_type = 'html'
    
    if lang is not None:
        template.lang = lang
    
    db.commit()
    db.refresh(template)
    return {"template": template.__dict__}


# Delete template and its file
@router.delete("/template")
def delete_template(
    template_id: int,
    user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a template and its file."""
    template = TemplateRepository.get_by_id(db, template_id)
    if not template or template.user_id != user.id:
        raise HTTPException(status_code=404, detail="Template not found")
    
    # Delete file
    if template.template_path and os.path.exists(template.template_path):
        os.remove(template.template_path)
    
    # Delete DB record
    TemplateRepository.delete(db, template_id)
    return {"message": "Template deleted"}


@router.get("/template/{template_id}/preview")
def preview_template(
    template_id: int,
    user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get template HTML for preview."""
    template = TemplateRepository.get_by_id(db, template_id)
    if not template or template.user_id != user.id:
        raise HTTPException(status_code=404, detail="Template not found")
    
    try:
        with open(template.template_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        return {"html": html_content, "fields": template.form_fields}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to read template: {str(e)}")
