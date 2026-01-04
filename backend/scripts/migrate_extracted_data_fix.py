
import sqlite3
import json
import sys
import os

DB_PATH = "form_filling.db"

def migrate():
    print(f"Migrating database at {DB_PATH}...")
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    try:
        # 1. Read existing data
        cursor.execute("SELECT * FROM extracted_data")
        rows = cursor.fetchall()
        data_to_migrate = []
        for row in rows:
            data_to_migrate.append({
                "id": row["id"],
                "user_id": row["user_id"],
                "entity_id": row["entity_id"],
                "status": row["status"],
                "file_hash": row["file_hash"],
                "extracted_toon_object": row["extracted_toon_object"]
            })
        
        print(f"Found {len(data_to_migrate)} rows to migrate.")

        # 2. Rename old table
        cursor.execute("ALTER TABLE extracted_data RENAME TO extracted_data_old")

        # 3. Create new table matching the SQLAlchemy model
        create_table_sql = """
        CREATE TABLE extracted_data (
            id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            entity_id INTEGER NOT NULL,
            status INTEGER NOT NULL DEFAULT 0,
            processed_file_hashes JSON,
            extracted_toon_object JSON,
            FOREIGN KEY(user_id) REFERENCES users (id) ON DELETE CASCADE,
            FOREIGN KEY(entity_id) REFERENCES entities (id) ON DELETE CASCADE,
            CONSTRAINT uq_entity_id UNIQUE (entity_id)
        );
        """
        cursor.execute(create_table_sql)
        cursor.execute("CREATE INDEX ix_extracted_data_entity_id ON extracted_data (entity_id)")
        cursor.execute("CREATE INDEX ix_extracted_data_user_id ON extracted_data (user_id)")

        # 4. Insert migrated data
        insert_sql = """
        INSERT INTO extracted_data (id, user_id, entity_id, status, processed_file_hashes, extracted_toon_object)
        VALUES (?, ?, ?, ?, ?, ?)
        """
        
        # Group by entity_id if necessary (though current data has unique entity_ids)
        # But logical correctness: if multiple rows existed for same entity, we should merge.
        # However, the old schema didn't enforce unique entity_id? Wait, checking old schema...
        # "FOREIGN KEY(entity_id) REFERENCES entities (id) ON DELETE CASCADE" - no unique constraint on entity_id in old schema?
        # Let's check the old schema output I got earlier:
        # CREATE INDEX ix_extracted_data_entity_id ON extracted_data (entity_id);
        # No UNIQUE index on entity_id. So multiple rows COULD exist.
        
        migrated_data = {}
        for row in data_to_migrate:
            e_id = row['entity_id']
            if e_id not in migrated_data:
                migrated_data[e_id] = {
                    "id": row["id"], # Keep first ID
                    "user_id": row["user_id"],
                    "entity_id": row["entity_id"],
                    "status": row["status"],
                    "hashes": [row["file_hash"]],
                    "extracted_toon_object": json.loads(row["extracted_toon_object"]) if row["extracted_toon_object"] else {}
                }
            else:
                # Merge logic (simplified: append hash, merge dicts)
                migrated_data[e_id]["hashes"].append(row["file_hash"])
                # Merge extracted data? 
                # For now, let's assuming simply keeping the latest or merging is fine.
                # But since the goal is to fix the schema error first, simple merge.
                current_data = migrated_data[e_id]["extracted_toon_object"]
                new_data = json.loads(row["extracted_toon_object"]) if row["extracted_toon_object"] else {}
                current_data.update(new_data)
                migrated_data[e_id]["extracted_toon_object"] = current_data

        for item in migrated_data.values():
            cursor.execute(insert_sql, (
                item["id"],
                item["user_id"],
                item["entity_id"],
                item["status"],
                json.dumps(item["hashes"]),
                json.dumps(item["extracted_toon_object"])
            ))

        # 5. Drop old table
        cursor.execute("DROP TABLE extracted_data_old")

        conn.commit()
        print("Migration successful.")

    except Exception as e:
        conn.rollback()
        print(f"Migration failed: {e}")
        sys.exit(1)
    finally:
        conn.close()

if __name__ == "__main__":
    migrate()
