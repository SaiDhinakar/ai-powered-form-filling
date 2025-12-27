import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from database import init_db, engine, Base
from database.models import User, Entity, Template, ExtractedData


def main():
    """Initialize the database."""
    print("Initializing database...")
    print(f"Database URL: {engine.url}")
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    print("\n✅ Database initialized successfully!")
    print("\nCreated tables:")
    for table_name in Base.metadata.tables.keys():
        print(f"  - {table_name}")


if __name__ == "__main__":
    main()