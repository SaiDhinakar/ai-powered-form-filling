from fastapi import APIRouter, Depends
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

from src.services.pdf_doc_service import auto_fill

router = APIRouter(tags=["Form Fill"])

@router.post("/form-fill")
def form_fill(
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
    template_id: int = None,
    entity_id: int = None  
):
    template_data = TemplateRepository.get_by_id(db, template_id)

    # Parse form_fields and pdf_data if they are JSON strings
    if isinstance(template_data.form_fields, str):
        try:
            pdf_form_map = json.loads(template_data.form_fields)
        except Exception:
            pdf_form_map = {}
    else:
        pdf_form_map = template_data.form_fields

    # Automatically handle any dropdown field
    # If value is not in allowed options, leave it blank
    # Assume template_data has a field_options dict: {field_name: [allowed_options]}
    field_options = getattr(template_data, 'field_options', {})
    for field, value in pdf_form_map.items():
        options = field_options.get(field)
        if options and value not in options:
            pdf_form_map[field] = ''

    if isinstance(template_data.pdf_data, str):
        try:
            pdf_data_dict = json.loads(template_data.pdf_data)
        except Exception:
            pdf_data_dict = {}
    else:
        pdf_data_dict = template_data.pdf_data

    # pdf_text should be just the text string
    pdf_text = pdf_data_dict.get("text", "")

    template_lang = template_data.lang

    # entity_data: get first non-empty, parse if string
    entity_data_raw = None
    for row in ExtractedDataRepository.get_by_entity(db, entity_id):
        if row.extracted_toon_object:
            entity_data_raw = row.extracted_toon_object
            break
    if entity_data_raw is None:
        entity_data = {}
    elif isinstance(entity_data_raw, str):
        try:
            entity_data = json.loads(entity_data_raw)
        except Exception:
            entity_data = {"raw": entity_data_raw}
    elif isinstance(entity_data_raw, dict):
        entity_data = entity_data_raw
    else:
        entity_data = {"raw": entity_data_raw}

    try:
        response = requests.post(
            url=f"{settings.AGENTS_API_ENDPOINT}/fill-form/",
            json={
                "pdf_form_map": pdf_form_map,
                "pdf_text": pdf_text,
                "template_lang": template_lang,
                "entity_data": entity_data
            },
            timeout=120
        )

        if response.status_code != 200:
            raise ValueError(f"Error from AI agent: {response.text}")

        template_pdf_path = template_data.pdf_path
        filled_form = response.json().get("filled_form", {})
        output_pdf_path = Path(settings.OUTPUT_FILE_PATH) / "filled_forms" / f"filled_{Path(template_pdf_path).name}"
        output_pdf_path.parent.mkdir(parents=True, exist_ok=True)

        auto_fill.fill_pdf_form(template_pdf_path, output_pdf_path, filled_form)

        # Return relative URL for frontend access
        relative_path = output_pdf_path.relative_to(settings.OUTPUT_FILE_PATH)
        return {"filled_pdf_path": f"/static/outputs/{relative_path}"}

    except Exception as e:
        print(f"An error occurred during form filling: {e}")
        raise e