"""PDF extraction service for extracting text, images, and metadata from PDF files."""

import logging
from typing import Dict, List, Optional, Any
from pathlib import Path
import io

import pdfplumber
from PIL import Image
from paddleocr import PaddleOCR

logger = logging.getLogger(__name__)

# Initialize PaddleOCR (will be lazy-loaded)
_ocr_instance = None

def get_ocr():
    """Get or initialize OCR instance (lazy loading)."""
    global _ocr_instance
    if _ocr_instance is None:
        logger.info("Initializing PaddleOCR for image text extraction")
        _ocr_instance = PaddleOCR(use_angle_cls=True, lang='en', show_log=False)
    return _ocr_instance


class PDFExtractionResult:
    """Container for PDF extraction results."""
    
    def __init__(self):
        self.text: str = ""
        self.pages: List[Dict[str, Any]] = []
        self.metadata: Dict[str, Any] = {}
        self.images: List[Dict[str, Any]] = []
        self.tables: List[Dict[str, Any]] = []
        self.total_pages: int = 0
        self.success: bool = False
        self.error_message: Optional[str] = None


class PDFExtractor:
    """Service for extracting content from PDF files."""
    
    @staticmethod
    def extract_from_file(file_path: str) -> PDFExtractionResult:
        """
        Extract all content from a PDF file.
        
        Args:
            file_path: Path to the PDF file
            
        Returns:
            PDFExtractionResult: Extraction results
        """
        result = PDFExtractionResult()
        
        try:
            with pdfplumber.open(file_path) as pdf:
                # Extract metadata
                result.metadata = PDFExtractor._extract_metadata(pdf)
                result.total_pages = len(pdf.pages)
                
                # Extract content from each page
                all_text_parts = []
                
                for page_num, page in enumerate(pdf.pages, start=1):
                    page_data = {
                        "page_number": page_num,
                        "text": "",
                        "tables": [],
                        "images": []
                    }
                    
                    # Extract text
                    page_text = page.extract_text()
                    if page_text:
                        page_data["text"] = page_text
                        all_text_parts.append(page_text)
                    
                    # Extract tables
                    tables = page.extract_tables()
                    if tables:
                        for table_idx, table in enumerate(tables):
                            table_data = {
                                "page": page_num,
                                "table_index": table_idx,
                                "data": table
                            }
                            page_data["tables"].append(table_data)
                            result.tables.append(table_data)
                    
                    # Extract images
                    images = PDFExtractor._extract_images_from_page(page, page_num)
                    if images:
                        page_data["images"] = images
                        result.images.extend(images)
                    
                    result.pages.append(page_data)
                
                # Combine all text
                result.text = "\n\n".join(all_text_parts)
                result.success = True
                
                logger.info(f"Successfully extracted PDF: {result.total_pages} pages, {len(result.text)} chars")
                
        except Exception as e:
            logger.error(f"Failed to extract PDF {file_path}: {e}")
            result.success = False
            result.error_message = str(e)
        
        return result
    
    @staticmethod
    def extract_from_bytes(file_bytes: bytes) -> PDFExtractionResult:
        """
        Extract content from PDF bytes.
        
        Args:
            file_bytes: PDF file as bytes
            
        Returns:
            PDFExtractionResult: Extraction results
        """
        result = PDFExtractionResult()
        
        try:
            with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
                # Extract metadata
                result.metadata = PDFExtractor._extract_metadata(pdf)
                result.total_pages = len(pdf.pages)
                
                # Extract content from each page
                all_text_parts = []
                
                for page_num, page in enumerate(pdf.pages, start=1):
                    page_data = {
                        "page_number": page_num,
                        "text": "",
                        "tables": [],
                        "images": []
                    }
                    
                    # Extract text
                    page_text = page.extract_text()
                    if page_text:
                        page_data["text"] = page_text
                        all_text_parts.append(page_text)
                    
                    # Extract tables
                    tables = page.extract_tables()
                    if tables:
                        for table_idx, table in enumerate(tables):
                            table_data = {
                                "page": page_num,
                                "table_index": table_idx,
                                "data": table
                            }
                            page_data["tables"].append(table_data)
                            result.tables.append(table_data)
                    
                    # Extract images (metadata only for bytes input)
                    if hasattr(page, 'images'):
                        page_data["images"] = [
                            {
                                "page": page_num,
                                "index": idx,
                                "x0": img.get("x0"),
                                "y0": img.get("y0"),
                                "x1": img.get("x1"),
                                "y1": img.get("y1"),
                            }
                            for idx, img in enumerate(page.images)
                        ]
                        result.images.extend(page_data["images"])
                    
                    result.pages.append(page_data)
                
                # Combine all text
                result.text = "\n\n".join(all_text_parts)
                
                # If no text was extracted, try OCR on page images
                if not result.text or len(result.text.strip()) < 50:
                    logger.info("No text extracted, attempting OCR on page images")
                    ocr_text_parts = []
                    
                    try:
                        ocr = get_ocr()
                        # Convert each page to image and OCR it
                        for page_num, page in enumerate(pdf.pages, start=1):
                            try:
                                # Convert page to image
                                img = page.to_image(resolution=150)
                                img_bytes = io.BytesIO()
                                img.original.save(img_bytes, format='PNG')
                                img_bytes.seek(0)
                                
                                # Perform OCR
                                result_ocr = ocr.ocr(img_bytes.getvalue(), cls=True)
                                
                                if result_ocr and result_ocr[0]:
                                    page_text = " ".join([line[1][0] for line in result_ocr[0] if line[1][0]])
                                    if page_text:
                                        ocr_text_parts.append(f"[Page {page_num}]\n{page_text}")
                                        # Update page data
                                        result.pages[page_num - 1]["text"] = page_text
                                        
                            except Exception as page_error:
                                logger.warning(f"OCR failed for page {page_num}: {page_error}")
                        
                        if ocr_text_parts:
                            result.text = "\n\n".join(ocr_text_parts)
                            logger.info(f"OCR extracted {len(result.text)} characters from {len(ocr_text_parts)} pages")
                        
                    except Exception as ocr_error:
                        logger.error(f"OCR processing failed: {ocr_error}")
                
                result.success = True
                logger.info(f"Successfully extracted PDF from bytes: {result.total_pages} pages, {len(result.text)} chars")
                
        except Exception as e:
            logger.error(f"Failed to extract PDF from bytes: {e}")
            result.success = False
            result.error_message = str(e)
        
        return result
    
    @staticmethod
    def _extract_metadata(pdf) -> Dict[str, Any]:
        """Extract metadata from PDF."""
        metadata = {}
        
        try:
            if hasattr(pdf, 'metadata') and pdf.metadata:
                # Extract common metadata fields
                for key in ['Author', 'Title', 'Subject', 'Creator', 'Producer', 'CreationDate', 'ModDate']:
                    if key in pdf.metadata:
                        metadata[key.lower()] = pdf.metadata[key]
        except Exception as e:
            logger.warning(f"Failed to extract metadata: {e}")
        
        return metadata
    
    @staticmethod
    def _extract_images_from_page(page, page_num: int) -> List[Dict[str, Any]]:
        """Extract images from a PDF page."""
        images = []
        
        try:
            if hasattr(page, 'images'):
                for idx, img in enumerate(page.images):
                    image_data = {
                        "page": page_num,
                        "index": idx,
                        "x0": img.get("x0"),
                        "y0": img.get("y0"),
                        "x1": img.get("x1"),
                        "y1": img.get("y1"),
                        "width": img.get("width"),
                        "height": img.get("height"),
                    }
                    images.append(image_data)
        except Exception as e:
            logger.warning(f"Failed to extract images from page {page_num}: {e}")
        
        return images
    
    @staticmethod
    def extract_text_only(file_path: str) -> Optional[str]:
        """
        Quick extraction of text only (no tables/images).
        
        Args:
            file_path: Path to the PDF file
            
        Returns:
            Optional[str]: Extracted text or None if failed
        """
        try:
            with pdfplumber.open(file_path) as pdf:
                text_parts = []
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text_parts.append(page_text)
                
                return "\n\n".join(text_parts)
        except Exception as e:
            logger.error(f"Failed to extract text from {file_path}: {e}")
            return None


# Global PDF extractor instance
pdf_extractor = PDFExtractor()
