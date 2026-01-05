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
@router.get("/")
def get_templates(
    limit: int = 10,
    skip: int = 0,
    user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    templates = TemplateRepository.get_all(db, user.id, skip=skip, limit=limit)
    results = []
    for t in templates:
        t_dict = t.__dict__.copy() 
        # Ensure name or filename is available
        if 'name' not in t_dict or not t_dict['name']:
            t_dict['name'] = Path(t.template_path).name
        t_dict['filename'] = Path(t.template_path).name
        results.append(t_dict)
    return {"templates": results}

@router.post("/")
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

    # Check if file with same hash exists for THIS user only
    existing_template = TemplateRepository.get_by_hash(db, file_hash)
    if existing_template and existing_template.user_id == user.id:
        # Same file already uploaded by this user - return existing
        return {"template": existing_template.__dict__}
    
    # If template exists for another user, create a unique hash for this user
    if existing_template:
        # Append user_id to create unique hash per user
        file_hash = hashlib.sha256(f"{file_hash}_{user.id}".encode()).hexdigest()

    # Prepare directory
    user_dir = Path(settings.UPLOAD_FILE_PATH) / "templates" / str(user.id)
    user_dir.mkdir(parents=True, exist_ok=True)
    
    # Use filename, handle collisions
    file_path = user_dir / file.filename
    if file_path.exists():
        # Append hash suffix if file exists to prevent collision
        # But if it's the exact same file (hash check passed earlier but we are here), it means we are uploading a new file with same hash?
        # No, hash check earlier returns existing_template if found. 
        # So here we have a NEW file (different content/hash) but SAME filename.
        # We must rename to avoid overwriting the existing different file.
        stem = Path(file.filename).stem
        suffix = Path(file.filename).suffix
        file_path = user_dir / f"{stem}_{file_hash[:8]}{suffix}"
    
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
        name=file.filename,
        lang=lang or 'en',
        template_type='html',
        form_fields=form_fields,
        html_structure=html_structure
    )
    return {"template": template.__dict__}


# Update template file or metadata
@router.put("/")
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
        
        # Use filename, handle collisions
        new_file_path = user_dir / file.filename
        if new_file_path.exists() and str(new_file_path) != file_path:
             # If exists and is NOT the current file we are updating (unlikely if name changed, but possible)
             # OR if we are updating content but filename is same as another existing file?
             # To be safe, if it exists, append hash.
             stem = Path(file.filename).stem
             suffix = Path(file.filename).suffix
             new_file_path = user_dir / f"{stem}_{new_file_hash[:8]}{suffix}"
        
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
@router.delete("/")
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


@router.get("/{template_id}/preview")
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
