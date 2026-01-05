import sys
import hashlib
from pathlib import Path
from datetime import datetime
import re
import requests

# Add backend directory to Python path
backend_dir = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(backend_dir))

from database.session import Session, get_db
from database.repository import ExtractedDataRepository
from src.services.data_extraction.pdf_extract import extract_text_from_pdf_or_img_with_metadata
from config import settings


def calculate_age_from_dob(dob_str: str) -> int | None:
    """
    Calculate age from date of birth string.
    
    Supports formats:
    - DD/MM/YYYY, DD-MM-YYYY
    - YYYY/MM/DD, YYYY-MM-DD
    - DD.MM.YYYY
    
    Args:
        dob_str: Date of birth string
        
    Returns:
        Age in years, or None if parsing fails
    """
    if not dob_str or not isinstance(dob_str, str):
        return None
    
    dob_str = dob_str.strip()
    
    # Common date formats to try
    date_formats = [
        '%d/%m/%Y',   # DD/MM/YYYY
        '%d-%m-%Y',   # DD-MM-YYYY
        '%d.%m.%Y',   # DD.MM.YYYY
        '%Y/%m/%d',   # YYYY/MM/DD
        '%Y-%m-%d',   # YYYY-MM-DD
        '%d %b %Y',   # DD Mon YYYY (e.g., 15 Jan 1990)
        '%d %B %Y',   # DD Month YYYY (e.g., 15 January 1990)
    ]
    
    dob_date = None
    for fmt in date_formats:
        try:
            dob_date = datetime.strptime(dob_str, fmt)
            break
        except ValueError:
            continue
    
    if not dob_date:
        # Try to extract year if full parsing fails
        year_match = re.search(r'\b(19|20)\d{2}\b', dob_str)
        if year_match:
            try:
                birth_year = int(year_match.group())
                current_year = datetime.now().year
                if 1900 < birth_year <= current_year:
                    return current_year - birth_year
            except:
                pass
        return None
    
    # Calculate age
    today = datetime.now()
    age = today.year - dob_date.year
    
    # Adjust if birthday hasn't occurred yet this year
    if (today.month, today.day) < (dob_date.month, dob_date.day):
        age -= 1
    
    return age if age >= 0 else None


def enrich_extracted_data(data: dict) -> dict:
    """
    Enrich extracted data with computed fields.
    
    Currently:
    - Calculates age from DOB if age is missing
    
    Args:
        data: Extracted data dictionary
        
    Returns:
        Enriched data dictionary
    """
    if not isinstance(data, dict):
        return data
    
    enriched = data.copy()
    
    # Calculate age from DOB if age is missing
    age_keys = ['age', 'current_age']
    dob_keys = ['date_of_birth', 'dob', 'birth_date', 'birthdate', 'date_of_birth_dob']
    
    # Check if age already exists
    has_age = any(
        key in enriched and enriched[key] and str(enriched[key]).strip()
        for key in age_keys
    )
    
    if not has_age:
        # Try to find DOB and calculate age
        for dob_key in dob_keys:
            if dob_key in enriched and enriched[dob_key]:
                calculated_age = calculate_age_from_dob(str(enriched[dob_key]))
                if calculated_age is not None:
                    enriched['age'] = str(calculated_age)
                    print(f"[DEBUG] Calculated age {calculated_age} from {dob_key}: {enriched[dob_key]}")
                    break
    
    return enriched

def extract_and_save_organize_data(db_session, user_id: int, entity_id: int, file_path: str, lang: str = 'en'):
    """
    Extract data from a PDF and save it to the database.
    
    Args:
        db_session: Database session
        user_id: ID of the user
        entity_id: ID of the entity
        file_path: Path to the file
    """
    try:
        with open(file_path, 'rb') as f:
            file_hash = hashlib.sha256(f.read()).hexdigest()
    except Exception as e:
        status = 0
        raise ValueError(f"Error generating file hash: {str(e)}")

    # Check if this file has already been processed for this entity
    if ExtractedDataRepository.is_file_processed(db_session, entity_id, file_hash):
        print("Extracted data with this file already exists. Skipping extraction.")
        return

    try:
        extraction_result = ''
        extracted_text = ''
        extracted_toon_text = ''
        status = 0
        try:
            extraction_result = extract_text_from_pdf_or_img_with_metadata(file_path, lang=lang)
            extracted_text = extraction_result.get('text', '')
            print(f"[DEBUG] Extraction result metadata: {extracted_text}")
            # metadata = extraction_result.get('metadata', {}) # Currently unused, can be used later
        except Exception as e:
            raise ValueError(f"Error extracting text from PDF: {str(e)}")
        status = 1

        if not extracted_text:
            status = 0
            raise ValueError("No text extracted from PDF.")
        else:
            try:
                response = requests.post(
                            url=f"{settings.AGENTS_API_ENDPOINT}/extract-data/",
                            params={
                                "document_text": extracted_text,
                                "lang": lang
                            },
                            timeout=120
                        )
                
                if response.status_code != 200:
                    status = 0
                    error_detail = response.text
                    status = 0
                    print(f"[ERROR] Agent service failed: {error_detail}")
                    raise ValueError(f"Agent service returned status code {response.status_code}. Detail: {error_detail}")
                
                agent_response = response.json()
                print(f"[DEBUG] Agent response: {agent_response}")
                extracted_toon_text = agent_response.get("extracted_data", "")
                if not extracted_toon_text:
                    status = 0
                    raise ValueError("No data extracted by agent service.")
                
                # Enrich data with computed fields (e.g., calculate age from DOB)
                if isinstance(extracted_toon_text, dict):
                    extracted_toon_text = enrich_extracted_data(extracted_toon_text)
            except Exception:
                status = 0
                raise

        print(f"[DEBUG] Final extracted Data: {extracted_toon_text}")
        # Use upsert_or_merge to consolidate data into single record per entity
        ExtractedDataRepository.upsert_or_merge(
            db=db_session,
            user_id=user_id,
            entity_id=entity_id,
            file_hash=file_hash,
            status=status,
            extracted_toon_object=extracted_toon_text  # Will be merged with existing data
        )
        return status
    
    except Exception as e:
        print(f"Error during extraction and saving: {e}")
        raise e

if __name__ == "__main__":
    from database.base import SessionLocal

    db = SessionLocal()
    
    try:
        user_id = 1
        entity_id = 1
        pdf_path = "/home/spidey/Downloads/ta.pdf"
        
        extract_and_save_organize_data(db, user_id, entity_id, pdf_path, lang='ta')
    finally:
        db.close()