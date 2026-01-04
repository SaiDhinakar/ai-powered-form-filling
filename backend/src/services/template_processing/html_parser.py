"""
HTML Template Parser and Form Filler

This module provides utilities for parsing HTML templates to extract form fields
and filling them with data.
"""

from bs4 import BeautifulSoup
from typing import Dict, List, Optional, Any, Tuple
import json
import re


# Semantic field mappings for common form fields
# Maps field name patterns to semantic descriptions and likely data source keys
SEMANTIC_FIELD_MAP = {
    # Name fields
    r'(full_?name|name|applicant_?name|resident_?name)': {
        'semantic_type': 'person_name',
        'description': 'Full name of the person/applicant',
        'likely_keys': ['full_name', 'name', 'applicant_name', 'resident_name']
    },
    r'(father_?name|fathers?_?name)': {
        'semantic_type': 'father_name',
        'description': 'Father\'s full name',
        'likely_keys': ['father_name', 'fathers_name', 'parent_name']
    },
    r'(mother_?name|mothers?_?name)': {
        'semantic_type': 'mother_name',
        'description': 'Mother\'s full name',
        'likely_keys': ['mother_name', 'mothers_name']
    },
    r'(spouse_?name|husband_?name|wife_?name)': {
        'semantic_type': 'spouse_name',
        'description': 'Spouse/Husband/Wife name',
        'likely_keys': ['spouse_name', 'husband_name', 'wife_name']
    },
    r'(guardian_?name|parent_?guardian)': {
        'semantic_type': 'guardian_name',
        'description': 'Guardian or parent name',
        'likely_keys': ['guardian_name', 'parent_guardian_name', 'father_name', 'mother_name']
    },
    
    # ID fields
    r'(aadhaar|aadhar|uid)': {
        'semantic_type': 'aadhaar_number',
        'description': 'Aadhaar/UID number (12 digits)',
        'likely_keys': ['aadhaar_number', 'aadhar_number', 'uid', 'aadhaar']
    },
    r'(pan_?(number|no)?)': {
        'semantic_type': 'pan_number',
        'description': 'PAN card number (10 alphanumeric)',
        'likely_keys': ['pan_number', 'pan', 'pan_no']
    },
    r'(passport)': {
        'semantic_type': 'passport_number',
        'description': 'Passport number',
        'likely_keys': ['passport_number', 'passport']
    },
    r'(voter_?id|epic)': {
        'semantic_type': 'voter_id',
        'description': 'Voter ID/EPIC number',
        'likely_keys': ['voter_id', 'epic_number', 'voter_id_number']
    },
    r'(driving_?license|dl_?(number|no)?)': {
        'semantic_type': 'driving_license',
        'description': 'Driving license number',
        'likely_keys': ['driving_license_number', 'dl_number', 'driving_license']
    },
    r'(enrol(l)?ment_?(id|no|number)?)': {
        'semantic_type': 'enrollment_id',
        'description': 'Enrollment/Registration ID',
        'likely_keys': ['enrollment_number', 'enrolment_id', 'registration_number']
    },
    
    # Contact fields
    r'(mobile|phone|contact)_?(number|no)?': {
        'semantic_type': 'mobile_number',
        'description': 'Mobile/Phone number (10 digits)',
        'likely_keys': ['mobile_number', 'phone_number', 'contact_number', 'mobile']
    },
    r'(email|e_?mail)': {
        'semantic_type': 'email',
        'description': 'Email address',
        'likely_keys': ['email', 'email_address', 'email_id']
    },
    
    # Address fields
    r'(house_?(no|number)?|building|flat)': {
        'semantic_type': 'house_number',
        'description': 'House/Building/Flat number',
        'likely_keys': ['house_number', 'building_number', 'flat_number', 'house_no']
    },
    r'(street|road|lane)': {
        'semantic_type': 'street',
        'description': 'Street/Road/Lane name',
        'likely_keys': ['street', 'road', 'lane', 'street_name']
    },
    r'(landmark)': {
        'semantic_type': 'landmark',
        'description': 'Nearby landmark',
        'likely_keys': ['landmark', 'near_landmark']
    },
    r'(village|town|city|vtc)': {
        'semantic_type': 'village_town_city',
        'description': 'Village/Town/City name',
        'likely_keys': ['village_town_city', 'city', 'town', 'village', 'vtc']
    },
    r'(post_?office|po)': {
        'semantic_type': 'post_office',
        'description': 'Post Office name',
        'likely_keys': ['post_office', 'po', 'post_office_name']
    },
    r'(sub_?district|taluk|tehsil|mandal)': {
        'semantic_type': 'sub_district',
        'description': 'Sub-district/Taluk/Tehsil/Mandal',
        'likely_keys': ['sub_district', 'taluk', 'tehsil', 'mandal']
    },
    r'(district)': {
        'semantic_type': 'district',
        'description': 'District name',
        'likely_keys': ['district', 'district_name']
    },
    r'(state|province)': {
        'semantic_type': 'state',
        'description': 'State/Province name',
        'likely_keys': ['state', 'province', 'state_name']
    },
    r'(country)': {
        'semantic_type': 'country',
        'description': 'Country name',
        'likely_keys': ['country', 'country_name']
    },
    r'(pin_?code|postal_?code|zip)': {
        'semantic_type': 'pincode',
        'description': 'PIN/Postal/ZIP code (6 digits for India)',
        'likely_keys': ['pincode', 'pin_code', 'postal_code', 'zip_code', 'pin']
    },
    r'(address_?line|address[_\s]?1|address1)': {
        'semantic_type': 'address_line_1',
        'description': 'Address line 1',
        'likely_keys': ['address_line_1', 'address1', 'address']
    },
    r'(address[_\s]?2|address2)': {
        'semantic_type': 'address_line_2',
        'description': 'Address line 2',
        'likely_keys': ['address_line_2', 'address2']
    },
    
    # Personal fields
    r'(gender|sex)': {
        'semantic_type': 'gender',
        'description': 'Gender (male/female/transgender)',
        'likely_keys': ['gender', 'sex']
    },
    r'(d[_\s]?o[_\s]?b|date_?of_?birth|birth_?date)': {
        'semantic_type': 'date_of_birth',
        'description': 'Date of birth (DD/MM/YYYY or YYYY-MM-DD)',
        'likely_keys': ['date_of_birth', 'dob', 'birth_date', 'birthdate']
    },
    r'(age)': {
        'semantic_type': 'age',
        'description': 'Age in years',
        'likely_keys': ['age', 'current_age']
    },
    r'(nationality)': {
        'semantic_type': 'nationality',
        'description': 'Nationality/Citizenship',
        'likely_keys': ['nationality', 'citizenship']
    },
    
    # Financial fields
    r'(bank_?name)': {
        'semantic_type': 'bank_name',
        'description': 'Bank name',
        'likely_keys': ['bank_name', 'bank']
    },
    r'(branch_?name|branch)': {
        'semantic_type': 'branch_name',
        'description': 'Bank branch name',
        'likely_keys': ['branch_name', 'branch', 'bank_branch']
    },
    r'(account_?(number|no)?|a\/?c)': {
        'semantic_type': 'account_number',
        'description': 'Bank account number',
        'likely_keys': ['account_number', 'account_no', 'bank_account']
    },
    r'(ifsc)': {
        'semantic_type': 'ifsc_code',
        'description': 'Bank IFSC code',
        'likely_keys': ['ifsc_code', 'ifsc', 'bank_ifsc']
    },
    
    # Date fields
    r'(issue_?date)': {
        'semantic_type': 'issue_date',
        'description': 'Issue/Start date',
        'likely_keys': ['issue_date', 'date_of_issue', 'start_date']
    },
    r'(expiry_?date|valid_?until|valid_?till)': {
        'semantic_type': 'expiry_date',
        'description': 'Expiry/End date',
        'likely_keys': ['expiry_date', 'date_of_expiry', 'valid_until', 'end_date']
    },
}


def _get_semantic_info(field_name: str, label: str = '') -> Dict[str, Any]:
    """
    Get semantic information for a form field based on its name and label.
    
    Args:
        field_name: The field's name attribute
        label: The field's label text
        
    Returns:
        Dictionary with semantic type, description, and likely data keys
    """
    combined_text = f"{field_name} {label}".lower()
    
    for pattern, info in SEMANTIC_FIELD_MAP.items():
        if re.search(pattern, combined_text, re.IGNORECASE):
            return info.copy()
    
    # Default fallback - try to infer from field name
    return {
        'semantic_type': 'unknown',
        'description': label if label else field_name.replace('_', ' ').title(),
        'likely_keys': [field_name.lower()]
    }


def parse_html_template(html_content: str) -> Dict[str, Any]:
    """
    Parse HTML template and extract form fields with their metadata.
    
    Args:
        html_content: Raw HTML content as string
        
    Returns:
        Dictionary containing:
        - form_fields: Dict of field names and their properties
        - html_structure: Parsed structure for rendering
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    
    form_fields = {}
    field_mappings = []
    
    # Find all input, select, and textarea elements
    for element in soup.find_all(['input', 'select', 'textarea']):
        field_name = element.get('name') or element.get('id')
        
        if not field_name:
            continue
            
        field_info = {
            'name': field_name,
            'type': element.get('type', element.name),
            'label': _extract_label(soup, element),
            'required': element.has_attr('required'),
            'placeholder': element.get('placeholder', ''),
            'default_value': element.get('value', ''),
        }
        
        # Add semantic information for better LLM matching
        semantic_info = _get_semantic_info(field_name, field_info['label'])
        field_info['semantic_type'] = semantic_info['semantic_type']
        field_info['description'] = semantic_info['description']
        field_info['likely_data_keys'] = semantic_info['likely_keys']
        
        # Handle select dropdowns
        if element.name == 'select':
            options = []
            for opt in element.find_all('option'):
                opt_value = opt.get('value', opt.text.strip())
                if opt_value:  # Skip empty options
                    options.append(opt_value)
            field_info['options'] = options
            field_info['type'] = 'select'
        
        # Handle checkboxes and radio buttons
        if element.get('type') in ['checkbox', 'radio']:
            field_info['checked'] = element.has_attr('checked')
            field_info['value'] = element.get('value', 'on')
        
        form_fields[field_name] = field_info
        
        # Add data attributes for mapping
        field_mappings.append({
            'field': field_name,
            'selector': _generate_selector(element),
            'type': field_info['type']
        })
    
    return {
        'form_fields': form_fields,
        'html_structure': {
            'field_mappings': field_mappings,
            'field_count': len(form_fields)
        }
    }


def _extract_label(soup: BeautifulSoup, element) -> str:
    """Extract label text for a form element."""
    # Try to find associated label by 'for' attribute
    element_id = element.get('id')
    if element_id:
        label = soup.find('label', {'for': element_id})
        if label:
            return label.get_text(strip=True)
    
    # Try to find parent label
    parent_label = element.find_parent('label')
    if parent_label:
        # Get text but exclude the input element's text
        label_text = parent_label.get_text(strip=True)
        return label_text
    
    # Try previous sibling label
    prev_sibling = element.find_previous_sibling('label')
    if prev_sibling:
        return prev_sibling.get_text(strip=True)
    
    # Fallback: use name/id with formatting
    name = element.get('name') or element.get('id', '')
    return name.replace('_', ' ').replace('-', ' ').title()


def _generate_selector(element) -> str:
    """Generate CSS selector for an element."""
    if element.get('id'):
        return f"#{element['id']}"
    elif element.get('name'):
        return f"[name='{element['name']}']"
    return ""


def fill_html_template(template_html: str, form_data: Dict[str, Any]) -> str:
    """
    Fill HTML template with provided data.
    
    Args:
        template_html: HTML template string
        form_data: Dictionary of field names to values
        
    Returns:
        Filled HTML string
    """
    soup = BeautifulSoup(template_html, 'html.parser')
    
    for field_name, value in form_data.items():
        if value is None:
            continue
            
        # Find elements by name or id
        elements = soup.find_all(['input', 'select', 'textarea'], 
                                 attrs={'name': field_name})
        if not elements:
            elements = soup.find_all(['input', 'select', 'textarea'], 
                                    attrs={'id': field_name})
        
        for element in elements:
            element_type = element.get('type', element.name)
            
            if element.name == 'textarea':
                element.string = str(value)
            elif element.name == 'select':
                # Select the option with matching value
                for option in element.find_all('option'):
                    option_value = option.get('value', option.text.strip())
                    if option_value == str(value) or option.text.strip() == str(value):
                        option['selected'] = 'selected'
                    else:
                        if 'selected' in option.attrs:
                            del option['selected']
            elif element_type in ['checkbox', 'radio']:
                element_value = element.get('value', 'on')
                str_value = str(value).lower()
                if str_value in ['true', 'yes', '1', 'on', element_value.lower()]:
                    element['checked'] = 'checked'
                else:
                    if 'checked' in element.attrs:
                        del element['checked']
            else:
                # Text input, email, number, date, etc.
                element['value'] = str(value)
    
    return str(soup)


def validate_field_data(field_info: Dict[str, Any], value: Any) -> Tuple[bool, Optional[str]]:
    """
    Validate field data against field constraints.
    
    Args:
        field_info: Field metadata from parse_html_template
        value: Value to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    field_label = field_info.get('label', field_info.get('name', 'Unknown'))
    
    # Check required fields
    if field_info.get('required') and not value:
        return False, f"Field '{field_label}' is required"
    
    if not value:
        return True, None
    
    field_type = field_info.get('type')
    
    # Validate email format
    if field_type == 'email':
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, str(value)):
            return False, f"Invalid email format for '{field_label}'"
    
    # Validate select options
    if field_type == 'select':
        options = field_info.get('options', [])
        if options and str(value) not in options:
            return False, f"Invalid option for '{field_label}'. Valid options: {options}"
    
    # Validate number fields
    if field_type == 'number':
        try:
            float(value)
        except (ValueError, TypeError):
            return False, f"Invalid number for '{field_label}'"
    
    return True, None


def extract_text_from_html(html_content: str) -> str:
    """
    Extract visible text content from HTML for context.
    
    Args:
        html_content: HTML content string
        
    Returns:
        Extracted text content
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Remove script and style elements
    for script in soup(["script", "style"]):
        script.decompose()
    
    # Get text
    text = soup.get_text(separator=' ', strip=True)
    
    # Clean up whitespace
    text = re.sub(r'\s+', ' ', text)
    
    return text


if __name__ == "__main__":
    # Example usage and testing
    sample_html = """
    <!DOCTYPE html>
    <html>
    <body>
        <form>
            <label for="name">Full Name:</label>
            <input type="text" id="name" name="full_name" required>
            
            <label for="email">Email:</label>
            <input type="email" id="email" name="email" required>
            
            <label for="country">Country:</label>
            <select id="country" name="country">
                <option value="">Select Country</option>
                <option value="US">United States</option>
                <option value="UK">United Kingdom</option>
                <option value="IN">India</option>
            </select>
            
            <label>
                <input type="checkbox" name="subscribe" value="yes">
                Subscribe to newsletter
            </label>
            
            <textarea name="comments" placeholder="Your comments"></textarea>
        </form>
    </body>
    </html>
    """
    
    # Parse template
    result = parse_html_template(sample_html)
    print("Form Fields:")
    print(json.dumps(result['form_fields'], indent=2))
    
    # Test filling
    filled = fill_html_template(sample_html, {
        'full_name': 'John Doe',
        'email': 'john@example.com',
        'country': 'US',
        'subscribe': 'yes',
        'comments': 'This is a test comment.'
    })
    print("\nFilled HTML preview:")
    print(filled[:500])
