from fastapi import FastAPI, HTTPException, Body, Form
from typing import Dict, Any
from pathlib import Path
import sys

# Add backend directory to Python path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from ai_agents.agent import extract_data, fill_form

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
    pdf_form_map: Dict[str, Any] = Body(...),
    pdf_text: str = Body(...),
    template_lang: str = Body(...),
    entity_data: Dict[str, Any] = Body(...)
):
    """
    Endpoint to fill PDF form fields using AI agent.
    Args:
        pdf_form_map (dict): Mapping of PDF form fields with empty/default values.
        pdf_text (str): Extracted text from the PDF document.
        template_lang (str): Language code of the template.
        entity_data (dict): Canonical entity values in English.
    Returns:
        dict: Filled PDF form fields.
    """
    try:
        filled = fill_form(pdf_form_map, pdf_text, template_lang, entity_data)
        return {"filled_form": filled}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))