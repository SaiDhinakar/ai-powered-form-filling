from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import HTMLResponse, FileResponse
import requests
import json
from pathlib import Path
import sys

backend_path = Path(__file__).resolve().parent.parent.parent.parent
sys.path.append(str(backend_path))

from database.session import Session, get_db
from database.repository import ExtractedDataRepository, TemplateRepository
from api.v1.routers.auth import get_current_user
from config import settings
from src.services.template_processing.html_parser import fill_html_template, validate_field_data

router = APIRouter(tags=["Form Fill"])

@router.post("/")
def form_fill(
    template_id: int = Query(...),
    entity_id: int = Query(...),
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    """
    Fill HTML template with extracted entity data.
    Returns filled HTML content.
    """
    # Get template
    template_data = TemplateRepository.get_by_id(db, template_id)
    if not template_data:
        raise HTTPException(status_code=404, detail="Template not found")
    
    # Ensure it's an HTML template
    if template_data.template_type != 'html':
        raise HTTPException(status_code=400, detail="Only HTML templates are supported for form filling")

    # Parse form_fields if they are JSON strings
    if isinstance(template_data.form_fields, str):
        try:
            form_fields_map = json.loads(template_data.form_fields)
        except Exception:
            form_fields_map = {}
    else:
        form_fields_map = template_data.form_fields or {}

    template_lang = template_data.lang or 'en'

    # Read template HTML
    try:
        with open(template_data.template_path, 'r', encoding='utf-8') as f:
            template_html = f.read()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to read template: {str(e)}")

    # Get consolidated entity data (single record per entity)
    entity_data = {}
    
    def parse_toon_data(raw_str: str) -> dict:
        """Parse TOON format string into dict."""
        data = {}
        for line in raw_str.split('\n'):
            line = line.strip()
            if ':' in line and not line.startswith('#') and not line.endswith(':'):
                key, _, value = line.partition(':')
                key = key.strip().replace('[', '_').replace(']', '').replace(' ', '_').lower()
                value = value.strip().strip('"')
                if key and value and value not in ['', 'N/A', '""']:
                    if key not in data or not data[key]:
                        data[key] = value
        return data
    
    # Fetch single consolidated record (no more looping/merging at query time)
    extracted_record = ExtractedDataRepository.get_single_by_entity(db, entity_id)
    if extracted_record and extracted_record.extracted_toon_object:
        raw = extracted_record.extracted_toon_object
        if isinstance(raw, str):
            try:
                entity_data = json.loads(raw)
            except json.JSONDecodeError:
                entity_data = parse_toon_data(raw)
        else:
            entity_data = raw
    
    if not entity_data:
        print(f"[WARNING] No extracted data found for entity_id: {entity_id}")
    
    print(f"[DEBUG] Merged entity data keys: {list(entity_data.keys())}")
    print(f"[DEBUG] Form fields to fill: {list(form_fields_map.keys())}")

    # Call AI agent to map entity data to form fields
    try:
        response = requests.post(
            url=f"{settings.AGENTS_API_ENDPOINT}/fill-form/",
            json={
                "form_fields_map": form_fields_map,
                "template_lang": template_lang,
                "entity_data": entity_data
            },
            timeout=120
        )

        if response.status_code != 200:
            raise ValueError(f"Error from AI agent: {response.text}")

        filled_form_data = response.json().get("filled_form", {})
        print(f"Form data to fill: {filled_form_data}")

    except Exception as e:
        print(f"Error calling AI agent: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to process form data: {str(e)}")

    # Validate filled data
    validation_warnings = []
    for field_name, field_info in form_fields_map.items():
        if field_name in filled_form_data:
            is_valid, error_msg = validate_field_data(field_info, filled_form_data[field_name])
            if not is_valid:
                validation_warnings.append(error_msg)

    if validation_warnings:
        print(f"Validation warnings: {validation_warnings}")

    # Fill HTML template
    try:
        filled_html = fill_html_template(template_html, filled_form_data)
    except Exception as e:
        print(f"Error filling template: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fill template: {str(e)}")

    # Save filled HTML
    output_dir = Path(settings.OUTPUT_FILE_PATH) / "filled_forms" / str(user.id)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    output_filename = f"filled_{template_id}_{entity_id}_{Path(template_data.template_path).stem}.html"
    output_path = output_dir / output_filename
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(filled_html)
    
    print(f"Successfully filled template and saved to {output_path}")

    return {
        "filled_html_path": str(output_path),
        "filled_data": filled_form_data,
        "validation_warnings": validation_warnings
    }


@router.get("/{user_id}/{filename}")
def get_filled_form(
    user_id: int,
    filename: str,
    user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieve a filled HTML form file."""
    # Security check - users can only access their own files
    if user.id != user_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    file_path = Path(settings.OUTPUT_FILE_PATH) / "filled_forms" / str(user_id) / filename
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Filled form not found")
    
    return FileResponse(
        path=file_path,
        media_type="text/html",
        filename=filename
    )


@router.get("/preview/{template_id}/{entity_id}")
def preview_filled_form(
    template_id: int,
    entity_id: int,
    user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Preview filled form as HTML response."""
    result = form_fill(template_id=template_id, entity_id=entity_id, db=db, user=user)
    
    with open(result["filled_html_path"], 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    return HTMLResponse(content=html_content)