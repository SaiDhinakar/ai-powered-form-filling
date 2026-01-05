#!/usr/bin/env python3
"""
Migration script to consolidate existing ExtractedData records.

This script addresses Issue #10: Remove entity data redundancy.

Before this migration:
- Multiple ExtractedData rows could exist per entity (one per uploaded document)
- Each row had its own file_hash and extracted_toon_object
- Data was merged at query time, causing overhead

After this migration:
- Only ONE ExtractedData row exists per entity
- All file hashes are stored in processed_file_hashes JSON list
- All extracted data is merged into a single extracted_toon_object
- entity_id has a unique constraint

Run this script BEFORE applying the new schema to consolidate existing data.

Usage:
    python scripts/migrate_consolidate_extracted_data.py
"""

import sys
from pathlib import Path
from collections import defaultdict

# Add backend directory to Python path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from sqlalchemy import text
from database.base import SessionLocal


def deep_merge(existing: dict, new: dict) -> dict:
    """Deep merge two dictionaries. New values take precedence for non-empty values."""
    merged = existing.copy() if existing else {}
    if not new:
        return merged
    for key, value in new.items():
        if value and value not in ['', 'N/A', '""', None]:
            merged[key] = value
        elif key not in merged:
            merged[key] = value
    return merged


def consolidate_extracted_data():
    """Consolidate multiple ExtractedData records per entity into single records."""
    db = SessionLocal()
    
    try:
        # Get all extracted data grouped by entity_id
        result = db.execute(text("""
            SELECT id, user_id, entity_id, status, file_hash, extracted_toon_object
            FROM extracted_data
            ORDER BY entity_id, id
        """))
        rows = result.fetchall()
        
        if not rows:
            print("No extracted data records found. Nothing to migrate.")
            return
        
        # Group by entity_id
        entity_groups = defaultdict(list)
        for row in rows:
            entity_groups[row.entity_id].append({
                'id': row.id,
                'user_id': row.user_id,
                'entity_id': row.entity_id,
                'status': row.status,
                'file_hash': row.file_hash,
                'extracted_toon_object': row.extracted_toon_object
            })
        
        print(f"Found {len(rows)} records across {len(entity_groups)} entities")
        
        entities_with_multiple = {k: v for k, v in entity_groups.items() if len(v) > 1}
        print(f"Entities with multiple records: {len(entities_with_multiple)}")
        
        if not entities_with_multiple:
            print("No entities have multiple records. Migration will only update schema.")
            print("\nTo update schema, run the following SQL:")
            print("""
-- Add new column for processed file hashes
ALTER TABLE extracted_data ADD COLUMN processed_file_hashes JSON DEFAULT '[]';

-- Migrate file_hash to processed_file_hashes array
UPDATE extracted_data SET processed_file_hashes = JSON_ARRAY(file_hash) WHERE file_hash IS NOT NULL;

-- Drop the old file_hash column
ALTER TABLE extracted_data DROP COLUMN file_hash;

-- Add unique constraint on entity_id
ALTER TABLE extracted_data ADD CONSTRAINT uq_extracted_data_entity_id UNIQUE (entity_id);
            """)
            return
        
        # Process each entity with multiple records
        for entity_id, records in entities_with_multiple.items():
            print(f"\nProcessing entity {entity_id} with {len(records)} records...")
            
            # Collect all file hashes
            file_hashes = []
            merged_data = {}
            best_status = 0
            keep_id = records[0]['id']  # Keep the first record
            user_id = records[0]['user_id']
            
            for record in records:
                if record['file_hash']:
                    file_hashes.append(record['file_hash'])
                
                # Merge extracted data
                if record['extracted_toon_object']:
                    import json
                    data = record['extracted_toon_object']
                    if isinstance(data, str):
                        try:
                            data = json.loads(data)
                        except json.JSONDecodeError:
                            data = {}
                    merged_data = deep_merge(merged_data, data)
                
                # Keep success status if any record was successful
                if record['status'] == 1:
                    best_status = 1
            
            # Delete all records except the first one
            ids_to_delete = [r['id'] for r in records[1:]]
            if ids_to_delete:
                db.execute(text(f"""
                    DELETE FROM extracted_data WHERE id IN ({','.join(map(str, ids_to_delete))})
                """))
                print(f"  Deleted {len(ids_to_delete)} redundant records")
            
            # Update the kept record with consolidated data
            import json
            db.execute(text("""
                UPDATE extracted_data 
                SET extracted_toon_object = :merged_data,
                    status = :status
                WHERE id = :keep_id
            """), {
                'merged_data': json.dumps(merged_data),
                'status': best_status,
                'keep_id': keep_id
            })
            print(f"  Consolidated into record {keep_id} with {len(file_hashes)} file hashes")
        
        db.commit()
        print("\n" + "="*60)
        print("Data consolidation complete!")
        print("="*60)
        
        print("\nNow run the following SQL to update the schema:")
        print("""
-- Add new column for processed file hashes
ALTER TABLE extracted_data ADD COLUMN processed_file_hashes JSON DEFAULT '[]';

-- Migrate file_hash to processed_file_hashes array
UPDATE extracted_data SET processed_file_hashes = JSON_ARRAY(file_hash) WHERE file_hash IS NOT NULL;

-- Drop the old file_hash column  
ALTER TABLE extracted_data DROP COLUMN file_hash;

-- Add unique constraint on entity_id (if not already present)
ALTER TABLE extracted_data ADD CONSTRAINT uq_extracted_data_entity_id UNIQUE (entity_id);
        """)
        
    except Exception as e:
        db.rollback()
        print(f"Error during migration: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    print("="*60)
    print("ExtractedData Consolidation Migration")
    print("Issue #10: Remove entity data redundancy")
    print("="*60)
    print()
    
    response = input("This will consolidate multiple ExtractedData records per entity. Continue? [y/N]: ")
    if response.lower() != 'y':
        print("Migration cancelled.")
        sys.exit(0)
    
    consolidate_extracted_data()
