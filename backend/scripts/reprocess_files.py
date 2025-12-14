"""Script to reprocess existing files with new OCR capability."""

import asyncio
from src.core.database import SessionLocal
from src.models.file_upload import FileUpload
from src.models.entity import Entity
from src.tasks.processing_tasks import process_pdf_task

def reprocess_files():
    """Reprocess all completed files that have zero extracted text."""
    db = SessionLocal()
    
    try:
        # Find entities with no extracted text
        entities = db.query(Entity).filter(
            (Entity.extracted_text == None) | (Entity.extracted_text == "")
        ).all()
        
        print(f"Found {len(entities)} entities with no extracted text")
        
        for entity in entities:
            print(f"\nEntity ID: {entity.id} - Name: {entity.name}")
            
            # Find associated files
            # Note: We need to find files for this entity through the session_id
            # For now, we'll manually trigger reprocessing
            files = db.query(FileUpload).all()
            
            for file in files:
                if file.file_type == 'application/pdf':
                    print(f"  Triggering reprocessing for file: {file.filename} (ID: {file.id})")
                    
                    # Trigger background task
                    result = process_pdf_task.delay(
                        file_id=file.id,
                        entity_id=entity.id,
                        user_id=entity.user_id
                    )
                    
                    print(f"  Task ID: {result.id}")
        
        print("\nAll files queued for reprocessing!")
        print("Monitor Celery worker logs to see progress.")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    print("=" * 60)
    print("PDF Reprocessing Script - With OCR Support")
    print("=" * 60)
    print("\nThis script will reprocess all PDF files with OCR enabled.")
    print("Make sure the Celery worker is running!")
    print()
    
    response = input("Continue? (yes/no): ")
    if response.lower() in ['yes', 'y']:
        reprocess_files()
    else:
        print("Cancelled.")
