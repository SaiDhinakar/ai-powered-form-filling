import sys
from pathlib import Path

# Add backend directory to Python path
backend_dir = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(backend_dir))

from database.repository import ExtractedDataRepository
from src.services.data_extraction.pdf_extract import extract_text_from_pdf_with_metadata
from src.services.agent_service.llm import extract_data_to_toon
import hashlib

def extract_and_save_organize_data(db_session, user_id: int, entity_id: int, pdf_path: str, lang: str = 'en'):
    """
    Extract data from a PDF and save it to the database.
    
    Args:
        db_session: Database session
        user_id: ID of the user
        entity_id: ID of the entity
        pdf_path: Path to the PDF file
    """
    try:
        extraction_result = ''
        extracted_text = ''
        extracted_toon_object = ''
        status = 0
        try:
            extraction_result = extract_text_from_pdf_with_metadata(pdf_path, lang=lang)
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
                try:
                    # Spelling correction in the native language (if supported)
                    try:
                        corrected_native = asyncio.run(correct_spelling(extracted_text, lang))
                    except Exception as e:
                        print(f"[WARN] Native spell correction failed ({lang}): {e}")
                        corrected_native = extracted_text

                    # Translate to English to normalize for LLM processing
                    try:
                        translated_text = asyncio.run(translate(corrected_native, src=lang, dest='en'))
                    except Exception as e:
                        print(f"[WARN] Translation to English failed: {e}")
                        translated_text = corrected_native if lang == 'en' else extracted_text

                    # Final English spelling correction
                    try:
                        corrected_english = asyncio.run(correct_spelling(translated_text, 'en'))
                    except Exception as e:
                        print(f"[WARN] English spell correction failed: {e}")
                        corrected_english = translated_text

                    extracted_toon_object = extract_data_to_toon(corrected_english)
                except Exception:
                    status = 0
                    raise
            except Exception as e:
                status = 0
                raise

        try:
            with open(pdf_path, 'rb') as f:
                file_hash = hashlib.sha256(f.read()).hexdigest()
        except Exception as e:
            status = 0
            raise ValueError(f"Error generating file hash: {str(e)}")

        ExtractedDataRepository.create(
            db=db_session,
            user_id=user_id,
            entity_id=entity_id,
            file_hash=file_hash,
            status=status,
            extracted_toon_object=str(extracted_toon_object)
        )
        
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