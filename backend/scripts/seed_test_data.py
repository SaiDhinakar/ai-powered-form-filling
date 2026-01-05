#!/usr/bin/env python3
"""
Seed script to populate dummy user data for testing.
Creates entities and extracted data for user_id 1.
"""

import sys
from pathlib import Path
import json

# Add backend directory to Python path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from database.session import SessionLocal
from database.models.entity import Entity
from database.models.extracted_data import ExtractedData

# Dummy extracted data simulating Aadhaar card information
# Contains ALL fields from the Aadhaar form template
DUMMY_EXTRACTED_DATA = {
    # Resident type
    "residentType": "resident",
    "pre_enrolment_id": "PRE-2025-001234",
    
    # Update flags (checkboxes)
    "updateBiometric": "on",
    "updateMobile": "on",
    "updateName": "",
    "updateGender": "",
    "updateDOB": "",
    "updateAddress": "on",
    "updateEmail": "on",
    
    # Personal Information
    "aadhaar_number": "1234 5678 9012",
    "full_name": "Rajesh Kumar Singh",
    "gender": "male",
    "dob_day": "15",
    "dob_month": "08",
    "dob_year": "1990",
    "age": "35",
    "dobType": "verified",
    
    # Address Information
    "care_of_name": "Suresh Kumar Singh",
    "house_number": "42-B",
    "street": "MG Road",
    "landmark": "Near City Mall",
    "area_locality": "Koramangala",
    "village_town_city": "Bangalore",
    "post_office": "Koramangala Post Office",
    "district": "Bangalore Urban",
    "sub_district": "Bangalore South",
    "state": "Karnataka",
    "pincode": "560034",
    
    # Contact Information
    "email": "rajesh.kumar@example.com",
    "mobile_number": "9876543210",
    
    # Parent/Guardian Information
    "parentRelation": "father",
    "parent_guardian_name": "Suresh Kumar Singh",
    "parent_guardian_aadhaar": "9876 5432 1098",
    
    # Verification Information
    "verificationType": "document",
    "doc_poi": "Passport",
    "doc_poa": "Utility Bill",
    "doc_dob": "Birth Certificate",
    "doc_por": "Rent Agreement",
    
    # Introducer/HOF Information
    "introducer_aadhaar": "5678 1234 9012",
    "hofRelation": "father",
    "hof_aadhaar": "9876 5432 1098",
    "introducer_hof_name": "Suresh Kumar Singh",
    
    # Enrolment datetime
    "enrolment_datetime": "2026-01-05 10:30:00"
}

# Second entity with different data
DUMMY_EXTRACTED_DATA_2 = {
    # Resident type
    "residentType": "resident",
    "pre_enrolment_id": "PRE-2025-005678",
    
    # Update flags (checkboxes)
    "updateBiometric": "",
    "updateMobile": "on",
    "updateName": "on",
    "updateGender": "",
    "updateDOB": "",
    "updateAddress": "",
    "updateEmail": "on",
    
    # Personal Information
    "aadhaar_number": "9876 5432 1098",
    "full_name": "Priya Sharma",
    "gender": "female",
    "dob_day": "22",
    "dob_month": "03",
    "dob_year": "1995",
    "age": "30",
    "dobType": "declared",
    
    # Address Information
    "care_of_name": "Amit Sharma",
    "house_number": "15-A",
    "street": "Park Street",
    "landmark": "Opposite Central Park",
    "area_locality": "Whitefield",
    "village_town_city": "Bangalore",
    "post_office": "Whitefield Post Office",
    "district": "Bangalore Urban",
    "sub_district": "Bangalore East",
    "state": "Karnataka",
    "pincode": "560066",
    
    # Contact Information
    "email": "priya.sharma@example.com",
    "mobile_number": "8765432109",
    
    # Parent/Guardian Information
    "parentRelation": "husband",
    "parent_guardian_name": "Amit Sharma",
    "parent_guardian_aadhaar": "1234 9876 5432",
    
    # Verification Information
    "verificationType": "hof",
    "doc_poi": "Driving License",
    "doc_poa": "Bank Statement",
    "doc_dob": "School Certificate",
    "doc_por": "Property Tax Receipt",
    
    # Introducer/HOF Information
    "introducer_aadhaar": "4567 8901 2345",
    "hofRelation": "husband",
    "hof_aadhaar": "1234 9876 5432",
    "introducer_hof_name": "Amit Sharma",
    
    # Enrolment datetime
    "enrolment_datetime": "2026-01-05 11:45:00"
}


def seed_test_data():
    """Seed the database with test data for user_id 1."""
    db = SessionLocal()
    
    try:
        user_id = 1
        
        # Check if user exists
        from database.models.user import User
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            print(f"[ERROR] User with id={user_id} does not exist. Please create the user first.")
            return False
        
        print(f"[INFO] Seeding test data for user: {user.username}")
        
        # ============ Entity 1: Rajesh Kumar ============
        entity1 = db.query(Entity).filter(
            Entity.user_id == user_id,
            Entity.name == "Rajesh Kumar"
        ).first()
        
        if not entity1:
            entity1 = Entity(
                user_id=user_id,
                name="Rajesh Kumar",
                entity_metadata={"type": "individual", "source": "aadhaar"}
            )
            db.add(entity1)
            db.flush()  # Get the ID
            print(f"[INFO] Created entity: Rajesh Kumar (id={entity1.id})")
        else:
            print(f"[INFO] Entity already exists: Rajesh Kumar (id={entity1.id})")
        
        # Create or update extracted data for entity1
        extracted1 = db.query(ExtractedData).filter(
            ExtractedData.entity_id == entity1.id
        ).first()
        
        if not extracted1:
            extracted1 = ExtractedData(
                user_id=user_id,
                entity_id=entity1.id,
                status=1,
                processed_file_hashes=["dummy_hash_aadhaar_001", "dummy_hash_pan_001"],
                extracted_toon_object=DUMMY_EXTRACTED_DATA
            )
            db.add(extracted1)
            print(f"[INFO] Created extracted data for entity: Rajesh Kumar")
        else:
            extracted1.extracted_toon_object = DUMMY_EXTRACTED_DATA
            extracted1.status = 1
            extracted1.processed_file_hashes = ["dummy_hash_aadhaar_001", "dummy_hash_pan_001"]
            print(f"[INFO] Updated extracted data for entity: Rajesh Kumar")
        
        # ============ Entity 2: Priya Sharma ============
        entity2 = db.query(Entity).filter(
            Entity.user_id == user_id,
            Entity.name == "Priya Sharma"
        ).first()
        
        if not entity2:
            entity2 = Entity(
                user_id=user_id,
                name="Priya Sharma",
                entity_metadata={"type": "individual", "source": "aadhaar"}
            )
            db.add(entity2)
            db.flush()
            print(f"[INFO] Created entity: Priya Sharma (id={entity2.id})")
        else:
            print(f"[INFO] Entity already exists: Priya Sharma (id={entity2.id})")
        
        # Create or update extracted data for entity2
        extracted2 = db.query(ExtractedData).filter(
            ExtractedData.entity_id == entity2.id
        ).first()
        
        if not extracted2:
            extracted2 = ExtractedData(
                user_id=user_id,
                entity_id=entity2.id,
                status=1,
                processed_file_hashes=["dummy_hash_aadhaar_002"],
                extracted_toon_object=DUMMY_EXTRACTED_DATA_2
            )
            db.add(extracted2)
            print(f"[INFO] Created extracted data for entity: Priya Sharma")
        else:
            extracted2.extracted_toon_object = DUMMY_EXTRACTED_DATA_2
            extracted2.status = 1
            extracted2.processed_file_hashes = ["dummy_hash_aadhaar_002"]
            print(f"[INFO] Updated extracted data for entity: Priya Sharma")
        
        # Commit all changes
        db.commit()
        
        print("\n" + "="*50)
        print("[SUCCESS] Test data seeded successfully!")
        print("="*50)
        print(f"\nCreated/Updated entities for user_id={user_id}:")
        print(f"  1. Rajesh Kumar (entity_id={entity1.id})")
        print(f"  2. Priya Sharma (entity_id={entity2.id})")
        print("\nYou can now test form-filling with these entities.")
        
        return True
        
    except Exception as e:
        db.rollback()
        print(f"[ERROR] Failed to seed data: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()


def show_current_data():
    """Display current entities and extracted data."""
    db = SessionLocal()
    
    try:
        print("\n" + "="*50)
        print("Current Database State")
        print("="*50)
        
        entities = db.query(Entity).all()
        print(f"\nEntities ({len(entities)} total):")
        for e in entities:
            print(f"  - id={e.id}, user_id={e.user_id}, name='{e.name}'")
        
        extracted = db.query(ExtractedData).all()
        print(f"\nExtracted Data ({len(extracted)} total):")
        for ed in extracted:
            data_keys = list(ed.extracted_toon_object.keys()) if ed.extracted_toon_object else []
            print(f"  - id={ed.id}, entity_id={ed.entity_id}, status={ed.status}, fields={len(data_keys)}")
            if data_keys:
                print(f"    Keys: {', '.join(data_keys[:5])}{'...' if len(data_keys) > 5 else ''}")
        
    finally:
        db.close()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Seed test data for the form-filling application")
    parser.add_argument("--show", action="store_true", help="Show current database state")
    args = parser.parse_args()
    
    if args.show:
        show_current_data()
    else:
        seed_test_data()
        show_current_data()
