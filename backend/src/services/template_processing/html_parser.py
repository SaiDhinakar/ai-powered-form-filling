"""
HTML Template Parser and Form Filler

This module provides utilities for parsing HTML templates to extract form fields
and filling them with data.
"""

from bs4 import BeautifulSoup
from typing import Dict, List, Optional, Any, Tuple
import json
import re


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
