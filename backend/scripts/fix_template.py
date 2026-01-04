#!/usr/bin/env python3
"""Script to add name attributes to template input fields."""

from bs4 import BeautifulSoup
import re
import sys
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from database.session import SessionLocal
from database.repository import TemplateRepository
from src.services.template_processing.html_parser import parse_html_template
import json

template_path = "uploads/templates/1/3d7f23bcb3ad84cf56c6d1f880a6ee1770aa82333a00fdaf49e1fe4d95dc6126.html"

with open(template_path, 'r') as f:
    html = f.read()

soup = BeautifulSoup(html, 'html.parser')

# Field mappings based on labels/context
field_mappings = {
    "Pre Enrolment ID": "pre_enrolment_id",
    "Aadhaar Number": "aadhaar_number",
    "Full Name": "full_name",
    "Age": "age",
    "Address": "address_care_of",
    "House No": "house_number",
    "Street": "street_road",
    "Landmark": "landmark",
    "Area": "area_locality",
    "Village": "village_town_city",
    "Post Office": "post_office",
    "District": "district",
    "Sub-District": "sub_district",
    "State": "state",
    "E-Mail": "email_field",
    "Mobile": "mobile_number",
    "PIN": "pin_code",
    "Introducer": "introducer_name",
    "HoF": "hof_name",
    "POI": "poi_document",
    "POA": "poa_document",
    "DOB": "dob_document",
    "POR": "por_document",
    "Name:": "parent_guardian_name",
    "Date & time": "enrolment_datetime",
}

# Find all text inputs without name attribute
count = 0
used_names = set()

for inp in soup.find_all('input'):
    input_type = inp.get('type', 'text')
    if input_type in ['text', 'email'] and not inp.get('name'):
        # Try to find label from previous siblings or parent
        parent = inp.find_parent(['div', 'td'])
        if parent:
            label_text = parent.get_text()
            
            # Try to match with field mappings
            matched = False
            for key, name in field_mappings.items():
                if key.lower() in label_text.lower() and name not in used_names:
                    inp['name'] = name
                    used_names.add(name)
                    count += 1
                    print(f"Added name='{name}' for label containing '{key}'")
                    matched = True
                    break
            
            if not matched:
                # Generate a name from nearby text
                clean_text = re.sub(r'[^a-zA-Z0-9\s]', '', label_text)
                words = [w for w in clean_text.split() if len(w) > 2][:3]
                if words:
                    name = '_'.join(words).lower()
                    # Ensure uniqueness
                    base_name = name
                    suffix = 1
                    while name in used_names:
                        name = f"{base_name}_{suffix}"
                        suffix += 1
                    inp['name'] = name
                    used_names.add(name)
                    count += 1
                    print(f"Generated name='{name}' from text")

# Handle date fields
date_fields = soup.find_all('input', {'placeholder': ['DD', 'MM', 'YYYY']})
date_names = ['dob_day', 'dob_month', 'dob_year']
for i, inp in enumerate(date_fields[:3]):
    if not inp.get('name') and i < len(date_names):
        inp['name'] = date_names[i]
        print(f"Added date field: {date_names[i]}")
        count += 1

# Save updated template
with open(template_path, 'w') as f:
    f.write(str(soup))

print(f"\nTotal fields updated: {count}")

# Now update the database with parsed form fields
db = SessionLocal()
try:
    parsed = parse_html_template(str(soup))
    form_fields = parsed.get('form_fields', {})
    html_structure = parsed.get('html_structure', {})
    
    template = TemplateRepository.get_by_id(db, 1)
    if template:
        template.form_fields = json.dumps(form_fields)
        template.html_structure = json.dumps(html_structure)
        db.commit()
        print(f"\nUpdated database with {len(form_fields)} form fields")
        print("Form field names:", list(form_fields.keys()))
finally:
    db.close()
