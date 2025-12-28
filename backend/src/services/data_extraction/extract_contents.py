import sys
import hashlib
from pathlib import Path
import requests

# Add backend directory to Python path
backend_dir = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(backend_dir))

from database.session import Session, get_db
from database.repository import ExtractedDataRepository
from src.services.data_extraction.pdf_extract import extract_text_from_pdf_or_img_with_metadata
from config import settings

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

    data = ExtractedDataRepository.get_by_entity(db_session, entity_id)
    existing_hashes = [row.file_hash for row in data]
    if file_hash in existing_hashes:
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
                    raise ValueError(f"Agent service returned status code {response.status_code}")
                
                agent_response = response.json()
                print(f"[DEBUG] Agent response: {agent_response}")
                extracted_toon_text = agent_response.get("extracted_data", "")
                if not extracted_toon_text:
                    status = 0
                    raise ValueError("No data extracted by agent service.")            
            except Exception:
                status = 0
                raise

        print(f"[DEBUG] Final extracted TOON Data: {extracted_toon_text}")
        ExtractedDataRepository.create(
            db=db_session,
            user_id=user_id,
            entity_id=entity_id,
            file_hash=file_hash,
            status=status,
            extracted_toon_object=str(extracted_toon_text)
        )
        return status
    
    except Exception as e:
        print(f"Error during extraction and saving: {e}")

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