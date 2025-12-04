"""PDF extraction service for extracting text, images, and metadata from PDF files."""

import logging
from typing import Dict, List, Optional, Any
from pathlib import Path
import io

import pdfplumber
from PIL import Image

logger = logging.getLogger(__name__)


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
                result.success = True
                
                logger.info(f"Successfully extracted PDF from bytes: {result.total_pages} pages")
                
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
