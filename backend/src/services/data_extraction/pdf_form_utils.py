from fillpdf import fillpdfs
from typing import Dict
from pathlib import Path
import sys

backend_dir = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(backend_dir)) 

from src.services.data_extraction.pdf_extract import extract_text_from_pdf_or_img_with_metadata

def get_template_metadata(pdf_path: str, lang: str = 'en') -> Dict[Dict[str, str], Dict[str, str]]:
    form_fileds = fillpdfs.get_form_fields(pdf_path)
    print(f"OCR is running for language: {lang}")
    extracted_data = extract_text_from_pdf_or_img_with_metadata(pdf_path, lang)
    del extracted_data["metadata"]
    print(f"Extracted data: {extracted_data}")
    return {
        "form_fields": form_fileds,
        "pdf_data": extracted_data
    }


if __name__ == "__main__":
    pdf_path = "/home/spidey/Downloads/sample.pdf"
    lang = "en"
    try:
        result = get_template_metadata(pdf_path, lang)
        print("Form Fields:")
        print(result['form_fields'])
        print("\nExtracted PDF Data:")
        print(result['pdf_data'])
    except Exception as e:
        print(f"Error: {e}")