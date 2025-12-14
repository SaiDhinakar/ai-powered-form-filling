"""Script to verify ChromaDB embeddings and their contents."""

import chromadb
from chromadb.config import Settings
from src.core.database import SessionLocal
from src.models.user import User  # Import User first
from src.models.entity import Entity
from src.models.processing_job import ProcessingJob
from src.models.file_upload import FileUpload
import json

def check_database():
    """Check database for entities and processing status."""
    db = SessionLocal()
    
    try:
        print("\n" + "=" * 60)
        print("DATABASE STATUS")
        print("=" * 60)
        
        # Check entities
        entities = db.query(Entity).all()
        print(f"\n📊 Total Entities: {len(entities)}")
        
        for entity in entities:
            print(f"\n  Entity ID: {entity.id}")
            print(f"  Name: {entity.name}")
            print(f"  User ID: {entity.user_id}")
            print(f"  Extracted Text Length: {len(entity.extracted_text) if entity.extracted_text else 0} chars")
            print(f"  Metadata: {json.dumps(entity.entity_metadata, indent=4) if entity.entity_metadata else 'None'}")
            print(f"  Created: {entity.created_at}")
            print(f"  Updated: {entity.updated_at}")
        
        # Check processing jobs
        jobs = db.query(ProcessingJob).all()
        print(f"\n📋 Total Processing Jobs: {len(jobs)}")
        
        for job in jobs:
            file = db.query(FileUpload).filter(FileUpload.id == job.file_id).first()
            print(f"\n  Job ID: {job.id}")
            print(f"  File: {file.filename if file else 'Unknown'}")
            print(f"  Status: {job.status.value}")
            if job.error_message:
                print(f"  Error: {job.error_message}")
            if job.extracted_data:
                print(f"  Extracted Data: {json.dumps(job.extracted_data, indent=4)}")
        
    except Exception as e:
        print(f"❌ Error checking database: {e}")
    finally:
        db.close()

def check_chromadb():
    """Check ChromaDB for stored embeddings."""
    try:
        print("\n" + "=" * 60)
        print("CHROMADB STATUS")
        print("=" * 60)
        
        client = chromadb.PersistentClient(
            path='./chroma_db',
            settings=Settings(anonymized_telemetry=False, allow_reset=True)
        )
        
        collections = client.list_collections()
        print(f"\n🗄️  Total Collections: {len(collections)}")
        
        if len(collections) == 0:
            print("\n⚠️  No collections found!")
            print("   This means no embeddings have been stored yet.")
            print("   Possible reasons:")
            print("   - No files have been processed successfully")
            print("   - Extracted text was empty (OCR didn't run)")
            print("   - Embedding service failed to store")
            return
        
        for coll in collections:
            print(f"\n📦 Collection: {coll.name}")
            count = coll.count()
            print(f"   Total Embeddings: {count}")
            
            if count > 0:
                # Get all items
                results = coll.get(include=['metadatas', 'documents', 'embeddings'])
                
                print(f"\n   Entity IDs stored: {results['ids']}")
                
                for i, (entity_id, doc, metadata, embedding) in enumerate(
                    zip(results['ids'], results['documents'], results['metadatas'], results['embeddings'])
                ):
                    print(f"\n   --- Entity {entity_id} ---")
                    print(f"   Metadata: {json.dumps(metadata, indent=6)}")
                    print(f"   Document (first 200 chars):")
                    print(f"   {doc[:200] if doc else 'None'}...")
                    print(f"   Embedding dimension: {len(embedding)}")
                    print(f"   Embedding sample (first 5 values): {embedding[:5]}")
        
    except Exception as e:
        print(f"❌ Error checking ChromaDB: {e}")
        import traceback
        traceback.print_exc()

def test_semantic_search():
    """Test semantic search functionality."""
    try:
        print("\n" + "=" * 60)
        print("SEMANTIC SEARCH TEST")
        print("=" * 60)
        
        from src.services.embedding_service import embedding_service
        
        # Initialize if needed
        if not hasattr(embedding_service, '_model') or embedding_service._model is None:
            print("\n🔧 Initializing embedding service...")
            embedding_service.initialize()
        
        db = SessionLocal()
        
        try:
            entities = db.query(Entity).all()
            
            if not entities:
                print("\n⚠️  No entities found to search")
                return
            
            user_id = entities[0].user_id
            
            # Test search
            test_queries = [
                "resume",
                "experience",
                "education",
                "skills"
            ]
            
            print(f"\n🔍 Testing searches for user {user_id}:")
            
            for query in test_queries:
                print(f"\n  Query: '{query}'")
                try:
                    results = embedding_service.search_similar_entities(
                        user_id=user_id,
                        query_text=query,
                        top_k=3,
                        min_similarity=0.0
                    )
                    
                    if results:
                        for entity_id, similarity in results:
                            print(f"    - Entity {entity_id}: {similarity:.4f} similarity")
                    else:
                        print(f"    No results found")
                        
                except Exception as e:
                    print(f"    ❌ Search failed: {e}")
        
        finally:
            db.close()
            
    except Exception as e:
        print(f"❌ Error in semantic search test: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Run all checks."""
    print("\n" + "=" * 60)
    print("CHROMADB EMBEDDINGS VERIFICATION REPORT")
    print("=" * 60)
    print("Generated:", "2025-12-06")
    
    check_database()
    check_chromadb()
    test_semantic_search()
    
    print("\n" + "=" * 60)
    print("VERIFICATION COMPLETE")
    print("=" * 60)
    
    # Summary
    print("\n📋 SUMMARY:")
    print("   ✅ Check database status above")
    print("   ✅ Check ChromaDB collections above")
    print("   ✅ Check semantic search results above")
    
    print("\n💡 NEXT STEPS:")
    print("   1. If no embeddings found, run: uv run python reprocess_files.py")
    print("   2. Make sure Celery worker is running")
    print("   3. Upload a new PDF file to test end-to-end")
    print()

if __name__ == "__main__":
    main()
