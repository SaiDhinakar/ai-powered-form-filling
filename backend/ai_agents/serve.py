from fastapi import FastAPI, HTTPException, Body, Form
from typing import Dict, Any
from pathlib import Path
import sys

# Add backend directory to Python path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from ai_agents.agent import extract_data, fill_html_form

app = FastAPI(title="Agent Service", version="1.0.0")

@app.get("/health")
def health_check():
    return {"status": "Agent service is healthy"}

@app.post("/agent/extract-data/")
def extract_data_endpoint(document_text: str, lang: str):
    """
    Endpoint to extract data from document text using AI agent.
    
    Args:
        document_text (str): The text content of the document to process.
        lang (str): Language code of the original document text.
    Returns:
        dict: Extracted data in TOON format as JSON.
    """
    try:
        print(f"[DEBUG] Received document text: {document_text[:10]}...")  # Log first 10 chars
        extracted_toon_text = extract_data(document_text, lang)
        print(f"[DEBUG] Extracted TOON Data: {extracted_toon_text}")
        return {"extracted_data": extracted_toon_text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/agent/fill-form/")
def fill_form_endpoint(
    form_fields_map: Dict[str, Any] = Body(...),
    template_lang: str = Body(...),
    entity_data: Dict[str, Any] = Body(...)
):
    """
    Endpoint to fill HTML form fields using AI agent.
    
    Args:
        form_fields_map (dict): HTML form fields with metadata
        template_lang (str): Language code of the template
        entity_data (dict): Extracted entity data in English
    Returns:
        dict: Filled form fields
    """
    try:
        print(f"[DEBUG] Filling form for lang: {template_lang}")
        print(f"[DEBUG] Form fields: {list(form_fields_map.keys())}")
        print(f"[DEBUG] Entity data keys: {list(entity_data.keys())}")
        
        filled = fill_html_form(form_fields_map, template_lang, entity_data)
        
        print(f"[DEBUG] Filled form: {filled}")
        return {"filled_form": filled}
    except Exception as e:
        print(f"[ERROR] {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))