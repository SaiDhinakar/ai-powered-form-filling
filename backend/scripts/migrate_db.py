import sqlite3
import os

DB_PATH = "form_filling.db"

def migrate():
    if not os.path.exists(DB_PATH):
        print(f"Database {DB_PATH} not found.")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Check if column exists
        cursor.execute("PRAGMA table_info(templates)")
        columns = [info[1] for info in cursor.fetchall()]
        
        if 'name' not in columns:
            print("Adding 'name' column to templates table...")
            cursor.execute("ALTER TABLE templates ADD COLUMN name VARCHAR(255)")
            conn.commit()
            print("Migration successful.")
        else:
            print("'name' column already exists.")
            
    except Exception as e:
        print(f"Migration failed: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    migrate()
