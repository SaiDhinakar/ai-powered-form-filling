# Data Processor Module

This module contains the data processing pipeline for extracting, mapping, and post-processing document data.

## Structure

```
data_processor/
├── __init__.py          # Module initialization
├── extractor.py         # Document data extraction (OCR)
├── mapper.py            # Field mapping to form templates
├── postprocessor.py     # Data validation and cleaning
└── README.md            # This file
```

## Overview

This module is designed as a separate, standalone component that can be developed independently by the data processing team. It provides a clean interface for the main API to interact with document processing capabilities.

## Components

### 1. Extractor (`extractor.py`)

Handles document data extraction using OCR technologies.

**Current Status:** Placeholder with dummy data

**TODO - Implement:**
- PaddleOCR integration for text extraction
- PDF to image conversion
- Multi-page document processing
- Language detection using fastText
- Confidence scoring for extracted fields

**Interface:**
```python
def extract_document_data(file_path: str, file_type: str) -> Dict[str, Any]:
    """Extract structured data from uploaded documents."""
    pass
```

**Expected Output:**
```python
{
    "name": "Rajesh Kumar",
    "date_of_birth": "1985-06-15",
    "document_type": "Aadhaar Card",
    "document_number": "1234-5678-9012",
    "address": "...",
    "phone": "+91-9876543210",
    "email": "rajesh.kumar@example.com",
    "confidence_score": 0.92,
    "language_detected": "en"
}
```

### 2. Mapper (`mapper.py`)

Maps extracted document data to government form templates.

**Current Status:** Basic placeholder with form template definitions

**TODO - Implement:**
- Complete form template definitions for all government forms
- Intelligent field mapping using NLP
- Handle missing or ambiguous fields
- Support multiple document inputs per form
- Form-specific validation rules

**Interface:**
```python
def map_to_form(extracted_data: Dict[str, Any], form_type: str) -> Dict[str, Any]:
    """Map extracted data to specific form template."""
    pass
```

**Supported Forms:**
- Passport Application
- Aadhaar Card
- PAN Card
- Voter ID
- Driver License
- Income Certificate
- Marriage Certificate
- And more...

### 3. Post-Processor (`postprocessor.py`)

Validates, cleans, and formats the extracted and mapped data.

**Current Status:** Basic validation placeholders

**TODO - Implement:**
- Comprehensive validation rules for Indian government IDs
- Date format standardization
- Phone number normalization (Indian formats)
- Address parsing and normalization
- Cross-field validation
- Data quality scoring

**Interface:**
```python
def validate_and_clean(data: Dict[str, Any]) -> Dict[str, Any]:
    """Validate and clean extracted data."""
    pass
```

## Integration with Main API

The main FastAPI application integrates this module through:

1. **File Upload** → Triggers processing job
2. **Processing Job** → Calls `extract_document_data()`
3. **Form Mapping** → Calls `map_to_form()`
4. **Validation** → Calls `validate_and_clean()`
5. **Return Results** → Stores in database for frontend

## Development Workflow

### For Data Processing Team:

1. **Focus on these files:**
   - `extractor.py` - OCR implementation
   - `mapper.py` - Form mapping logic
   - `postprocessor.py` - Validation rules

2. **Dependencies already available:**
   - PaddleOCR (for OCR)
   - fastText (for language detection)
   - All utilities in `pyproject.toml`

3. **Testing:**
   - Add test files to `backend/tests/`
   - Use sample government documents
   - Test with various image qualities and formats

4. **Data Flow:**
   ```
   Document Upload → MinIO Storage → Extract Data → Map to Form → Validate → Return JSON
   ```

## Testing the Dummy Implementation

The current placeholder returns mock data for testing the API:

```bash
# Upload a file (any image/PDF)
curl -X POST "http://localhost:8000/files/upload" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@sample.pdf"

# The processing job will use dummy data from extractor.py
```

## Environment Variables

No additional environment variables needed for this module. All OCR processing happens in-memory.

## Performance Considerations

- OCR processing can be CPU-intensive
- Consider implementing background task queue (Celery/RQ)
- Cache extracted results to avoid reprocessing
- Optimize image preprocessing for better OCR accuracy

## Future Enhancements

1. **ML Model Integration:**
   - Train custom models for Indian government forms
   - Fine-tune PaddleOCR for Devanagari and regional languages
   - Entity recognition for key fields

2. **Accuracy Improvements:**
   - Image preprocessing (deskew, denoise, contrast)
   - Multi-model ensemble for better accuracy
   - Human-in-the-loop validation for low-confidence extractions

3. **Performance:**
   - Async processing with background workers
   - GPU acceleration for OCR
   - Batch processing for multiple documents

## Questions or Issues?

Contact the backend team for API integration questions or modify the interfaces as needed.
