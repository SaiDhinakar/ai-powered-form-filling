"""Post-processing module for data validation and cleaning (placeholder).

This module handles validation, cleaning, and formatting of extracted and mapped data.
"""

from typing import Dict, Any, List, Optional
import logging
import re

logger = logging.getLogger(__name__)


def validate_and_clean(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate and clean extracted data.
    
    This is a placeholder function. Implement actual validation and cleaning logic.
    
    Args:
        data: Extracted data to validate and clean
        
    Returns:
        Dict[str, Any]: Cleaned and validated data with validation report
        
    Example:
        {
            "cleaned_data": {...},
            "validation_report": {
                "is_valid": True,
                "errors": [],
                "warnings": [],
                "corrections_made": []
            }
        }
    """
    logger.info("Validating and cleaning extracted data")
    
    cleaned_data = data.copy()
    errors = []
    warnings = []
    corrections = []
    
    # Placeholder validation logic
    
    # Validate name
    if "name" in data:
        name = data["name"].strip()
        if not name:
            errors.append("Name is empty")
        elif len(name) < 2:
            warnings.append("Name is very short")
        cleaned_data["name"] = name.title()
    
    # Validate date of birth
    if "date_of_birth" in data:
        dob = data["date_of_birth"]
        if not validate_date_format(dob):
            errors.append(f"Invalid date of birth format: {dob}")
    
    # Validate phone number
    if "phone" in data:
        phone = data["phone"]
        cleaned_phone = clean_phone_number(phone)
        if cleaned_phone != phone:
            corrections.append(f"Cleaned phone number: {phone} -> {cleaned_phone}")
            cleaned_data["phone"] = cleaned_phone
    
    # Validate email
    if "email" in data:
        email = data["email"]
        if not validate_email(email):
            errors.append(f"Invalid email format: {email}")
    
    return {
        "cleaned_data": cleaned_data,
        "validation_report": {
            "is_valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "corrections_made": corrections
        }
    }


def validate_date_format(date_str: str) -> bool:
    """
    Validate date string format.
    
    Args:
        date_str: Date string to validate
        
    Returns:
        bool: True if valid date format
    """
    # Placeholder: Accept YYYY-MM-DD format
    pattern = r'^\d{4}-\d{2}-\d{2}$'
    return bool(re.match(pattern, date_str))


def clean_phone_number(phone: str) -> str:
    """
    Clean and format phone number.
    
    Args:
        phone: Phone number to clean
        
    Returns:
        str: Cleaned phone number
    """
    # Remove all non-digit characters except +
    cleaned = re.sub(r'[^\d+]', '', phone)
    
    # Ensure +91 prefix for Indian numbers
    if not cleaned.startswith('+'):
        if cleaned.startswith('91'):
            cleaned = '+' + cleaned
        else:
            cleaned = '+91' + cleaned
    
    return cleaned


def validate_email(email: str) -> bool:
    """
    Validate email format.
    
    Args:
        email: Email to validate
        
    Returns:
        bool: True if valid email
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def normalize_address(address: str) -> str:
    """
    Normalize address formatting.
    
    TODO: Implement proper address normalization
    
    Args:
        address: Address to normalize
        
    Returns:
        str: Normalized address
    """
    # Placeholder: Basic cleanup
    return ' '.join(address.split())


def check_data_completeness(data: Dict[str, Any], required_fields: List[str]) -> Dict[str, Any]:
    """
    Check if all required fields are present and non-empty.
    
    Args:
        data: Data to check
        required_fields: List of required field names
        
    Returns:
        Dict[str, Any]: Completeness report
    """
    missing_fields = []
    empty_fields = []
    
    for field in required_fields:
        if field not in data:
            missing_fields.append(field)
        elif not data[field] or str(data[field]).strip() == "":
            empty_fields.append(field)
    
    is_complete = len(missing_fields) == 0 and len(empty_fields) == 0
    
    return {
        "is_complete": is_complete,
        "missing_fields": missing_fields,
        "empty_fields": empty_fields,
        "completeness_score": 1.0 - (len(missing_fields) + len(empty_fields)) / len(required_fields)
    }
