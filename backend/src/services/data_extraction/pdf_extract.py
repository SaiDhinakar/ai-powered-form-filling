import fitz  # PyMuPDF
from pathlib import Path
from typing import Optional
import requests
import json
import io
import os
from dotenv import load_dotenv

load_dotenv()

def extract_text_from_pdf_with_metadata(pdf_path: str, lang: str) -> dict:
    """
    Extract text and metadata from a PDF file.
    
    Args:
        pdf_path: Path to the PDF file
        lang: Language code for extraction
        
    Returns:
        Dictionary containing text and metadata
    """
    pdf_file = Path(pdf_path)
    
    if not pdf_file.exists():
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")
    
    result = {
        'text': '',
        'num_pages': 0,
        'metadata': {}
    }
    
    try:
        doc = fitz.open(pdf_path)
        result['num_pages'] = len(doc)
        text_content = []

        if lang == 'en':
            result['metadata'] = doc.metadata
            for page in doc:
                text = page.get_text()
                if text:
                    text_content.append(text)
            
            result['text'] = '\n'.join(text_content)
            doc.close()
        else:            
            ocr_url = os.getenv("OCR_ENDPOINT", "http://localhost:3105/extract_text/")
            
            # Extract each page as an image and send to OCR service
            for page_num in range(len(doc)):
                page = doc[page_num]
                
                # Convert page to image (PNG format)
                pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))  # 2x zoom for better quality
                img_bytes = pix.tobytes("png")
                
                # Prepare the file for upload
                files = {
                    'file': (f'page_{page_num}.png', io.BytesIO(img_bytes), 'image/png')
                }
                
                params = {
                    'lang': lang,
                    'min_confidence': 0.7
                }
                
                try:
                    # Call OCR service
                    response = requests.post(ocr_url, files=files, params=params, timeout=30)
                    
                    if response.status_code == 200:
                        ocr_result = response.json()
                        # The OCR endpoint returns: {"extracted_text": str, "details": list, "metadata": dict}
                        if 'extracted_text' in ocr_result and ocr_result['extracted_text']:
                            text_content.append(ocr_result['extracted_text'])
                            print(f"Page {page_num + 1}: Extracted {ocr_result.get('metadata', {}).get('total_detections', 0)} text blocks")
                    else:
                        print(f"Warning: OCR failed for page {page_num + 1} with status {response.status_code}")
                        
                except requests.exceptions.RequestException as e:
                    print(f"Warning: Failed to connect to OCR service for page {page_num + 1}: {str(e)}")
            
            result['text'] = '\n'.join(text_content)
            doc.close()
            
        return result
    
    except Exception as e:
        raise Exception(f"Error extracting text from PDF: {str(e)}")


if __name__ == "__main__":
    # Example usage
    pdf_path = "/home/spidey/Downloads/ta-2.pdf"
    lang = "ta"  # Change to 'hi', 'ta', etc. for other languages
    
    try:
        result = extract_text_from_pdf_with_metadata(pdf_path, lang)
        print("Extracted Text:")
        print(result['text'])
        print(f"\nNumber of pages: {result['num_pages']}")
        print(f"Metadata: {result['metadata']}")
    except Exception as e:
        print(f"Error: {e}")