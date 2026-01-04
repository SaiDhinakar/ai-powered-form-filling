import google.generativeai as genai
from dotenv import load_dotenv
import json
import os

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY", None)
MODEL = os.getenv("MODEL", "gemini-2.5-flash")

if not API_KEY or not MODEL:
    raise ValueError("GEMINI_API_KEY and MODEL must be set in environment variables.")

extraction_context = """
You are a comprehensive document data extraction agent.

TASK: Extract ALL information from documents into a flat JSON object.

EXTRACT THESE CATEGORIES:
- Personal: name, date_of_birth, gender, age, nationality, photo
- Family: father_name, mother_name, guardian_name, spouse_name, husband_name, wife_name
- Address: address_line_1, house_number, street, landmark, village_town_city, post_office, sub_district, district, state, country, pincode
- Contact: mobile_number, phone_number, email, alternate_email
- IDs: aadhaar_number, pan_number, passport_number, voter_id, driving_license_number, enrollment_number
- Organization: company, employer, institution, college, university, school, department, designation
- Financial: bank_name, branch_name, account_number, ifsc_code
- Dates: date_of_birth, issue_date, expiry_date, joining_date, graduation_date
- Authority: issuing_authority, government_body, office_name

RULES:
- Use snake_case keys (e.g., father_name, date_of_birth)
- Return FLAT JSON only - no nested objects, no arrays
- Extract ALL data present - don't skip anything
- Don't fabricate data - only extract what exists
- No markdown, no explanations - just JSON
"""

form_fill_context = """
You are a strict form-filling agent.

TASK: Map entity data to form fields using semantic matching.

MATCHING RULES:
- name/recipient_name/cardholder_name → full_name
- father_name → parent_guardian_name (when parent type is father)
- email → email_field
- mobile_number → mobile_number
- aadhaar_number → aadhaar_number
- date_of_birth → dob fields
- village_town_city → village_town_city
- pincode → pin_code
- gender → gender (use: male/female/transgender)

STRICT RULES:
- ONLY fill with data that EXISTS in entity_data
- NEVER fabricate, guess, or make up data
- NEVER use placeholders like "N/A" or "Unknown"
- Leave field as empty string "" if no matching data
- Return JSON with exact form field names as keys

OUTPUT: Valid JSON object only - no markdown, no explanations.
"""

genai.configure(api_key=API_KEY)
extraction_model = genai.GenerativeModel(
    model_name=MODEL,
    system_instruction=(
        extraction_context
    ),
    generation_config={
        "temperature": 0.4,
        "top_p": 0.9,
    }
)

genai.configure(api_key=API_KEY)
form_fill_model = genai.GenerativeModel(
    model_name=MODEL,
    system_instruction=(
        form_fill_context
    ),
    generation_config={
        "temperature": 0.4,
        "top_p": 0.9,
    }
)


def extract_data(document_text: str, lang: str) -> dict:
    """
    Extract data from document text and return as JSON dict.
    
    Args:
        document_text (str): The text content of the document to process.
        lang (str): Language code of the original document text.
    Returns:
        dict: Extracted data as a dictionary.
    """
    prompt = f"""Language: {lang}

Document:
{document_text}

Extract all data as flat JSON."""
    
    try:
        response = extraction_model.generate_content(prompt)    
        response_text = response.text.strip()
        
        # Remove markdown code blocks if present
        if response_text.startswith("```"):
            first_newline = response_text.find("\n")
            if first_newline != -1:
                response_text = response_text[first_newline + 1:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]
            response_text = response_text.strip()
        
        # Remove "json" language identifier if present
        if response_text.lower().startswith("json"):
            response_text = response_text[4:].strip()
        
        # Try to fix incomplete JSON by adding closing braces
        open_braces = response_text.count('{') - response_text.count('}')
        open_brackets = response_text.count('[') - response_text.count(']')
        
        if open_braces > 0 or open_brackets > 0:
            print(f"Warning: Incomplete JSON detected. Attempting to fix...")
            response_text = response_text.rstrip().rstrip(',')
            response_text += '}' * open_braces
            response_text += ']' * open_brackets
        
        # Parse JSON
        data: dict = json.loads(response_text)
        return data
    
    except json.JSONDecodeError as e:
        print(f"JSON decode error: {e}")
        print(f"Response text: {response_text}")
        raise ValueError(f"Failed to parse LLM response as JSON: {str(e)}")
    except Exception as e:
        print(f"Error in extract_data: {e}")
        raise


def fill_html_form(
    form_fields_map: dict,
    template_lang: str,
    entity_data: dict
) -> dict:
    """
    Fill HTML form fields based on entity data.
    
    Args:
        form_fields_map (dict): HTML form fields with metadata
        template_lang (str): Language code of the template
        entity_data (dict): Extracted entity data in English
    Returns:
        dict: Filled form fields
    """
    prompt = f"""Template Language: {template_lang}

Form Fields:
{json.dumps(form_fields_map, indent=2)}

Entity Data:
{json.dumps(entity_data, indent=2)}

Fill form fields using entity data. Return JSON only."""
    
    try:
        response = form_fill_model.generate_content(prompt)
        response_text = response.text.strip()
        
        # Remove markdown code blocks if present
        if response_text.startswith("```"):
            first_newline = response_text.find("\n")
            if first_newline != -1:
                response_text = response_text[first_newline + 1:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]
            response_text = response_text.strip()
        
        # Remove "json" language identifier if present
        if response_text.lower().startswith("json"):
            response_text = response_text[4:].strip()
        
        # Parse JSON
        filled_form: dict = json.loads(response_text)
        print(f"[DEBUG] Entity data received: {entity_data}")
        print(f"[DEBUG] Form fields to fill: {list(form_fields_map.keys())}")
        print(f"[DEBUG] Filled form result: {filled_form}")
        
        # Validate field names
        for field_name in filled_form.keys():
            if field_name not in form_fields_map:
                print(f"Warning: Field '{field_name}' not in form fields map")
        
        return filled_form
    
    except json.JSONDecodeError as e:
        print(f"JSON decode error: {e}")
        print(f"Response text: {response_text}")
        raise ValueError(f"Failed to parse LLM response as JSON: {str(e)}")
    except Exception as e:
        print(f"Error in fill_html_form: {e}")
        raise


# Keep backward compatibility alias
def fill_form(
    pdf_form_map: dict,
    pdf_text: str,
    template_lang: str,
    entity_data: dict
) -> dict:
    """
    Legacy function for PDF form filling.
    Now redirects to HTML form filling using entity_data.
    """
    return fill_html_form(pdf_form_map, template_lang, entity_data)