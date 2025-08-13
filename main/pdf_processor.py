"""
PDF processing utilities for text extraction and OCR.
"""

import os
import PyPDF2
import pytesseract
from PIL import Image
import io
import re
from typing import Dict, List, Optional
import logging
from pdf2image import convert_from_path
import tempfile

logger = logging.getLogger(__name__)

class PDFProcessor:
    """Handles PDF text extraction and OCR processing."""
    
    def __init__(self, pdf_path: str):
        self.pdf_path = pdf_path
        self.doc = None
        self.page_count = 0
        self.file_handle = None
        
    def open_pdf(self) -> bool:
        """Open and validate PDF file."""
        try:
            self.file_handle = open(self.pdf_path, 'rb')
            self.doc = PyPDF2.PdfReader(self.file_handle)
            self.page_count = len(self.doc.pages)
            return True
        except Exception as e:
            logger.error(f"Error opening PDF {self.pdf_path}: {e}")
            return False
    
    def close_pdf(self):
        """Close the PDF file handle."""
        if self.file_handle:
            self.file_handle.close()
            self.file_handle = None
    
    def extract_text_from_page(self, page_num: int) -> str:
        """Extract text from a specific page."""
        try:
            if not self.doc or page_num >= self.page_count:
                return ""
            page = self.doc.pages[page_num]
            text = page.extract_text()
            return text.strip() if text else ""
        except Exception as e:
            logger.error(f"Error extracting text from page {page_num}: {e}")
            return ""
    
    def is_page_scanned(self, page_num: int) -> bool:
        """Check if a page is scanned (image-based)."""
        try:
            text = self.extract_text_from_page(page_num)
            # If very little text is extracted, it's likely scanned
            # Also check for common patterns that indicate scanned documents
            if len(text) < 50:
                return True
            
            # Check if text contains mostly whitespace or special characters
            clean_text = re.sub(r'\s+', ' ', text).strip()
            if len(clean_text) < 30:
                return True
            
            # Check for common scanned document indicators
            scanned_indicators = ['image', 'scan', 'photograph', 'picture']
            text_lower = text.lower()
            if any(indicator in text_lower for indicator in scanned_indicators):
                return True
                
            return False
            
        except Exception as e:
            logger.error(f"Error checking if page {page_num} is scanned: {e}")
            return True
    
    def extract_text_with_ocr(self, page_num: int) -> str:
        """Extract text from scanned page using OCR."""
        try:
            # Convert PDF page to image
            images = convert_from_path(
                self.pdf_path, 
                first_page=page_num + 1, 
                last_page=page_num + 1,
                dpi=300  # Higher DPI for better OCR accuracy
            )
            
            if not images:
                logger.warning(f"No image extracted for page {page_num + 1}")
                return ""
            
            # Get the first (and only) image
            image = images[0]
            
            # Perform OCR using pytesseract
            text = pytesseract.image_to_string(image, lang='eng')
            
            # Clean up the extracted text
            text = text.strip()
            
            if not text:
                logger.warning(f"No text extracted via OCR for page {page_num + 1}")
                return f"[OCR completed for page {page_num + 1} - no text detected]"
            
            return text
            
        except Exception as e:
            logger.error(f"Error performing OCR on page {page_num}: {e}")
            return f"[OCR failed for page {page_num + 1} - {str(e)}]"
    
    def process_document(self) -> Dict:
        """Process entire document and extract text from all pages."""
        try:
            if not self.open_pdf():
                return {"error": "Could not open PDF file"}
            
            result = {
                "page_count": self.page_count,
                "pages": [],
                "full_text": "",
                "extraction_method": "text",
                "processing_errors": []
            }
            
            full_text_parts = []
            
            for page_num in range(self.page_count):
                page_info = {
                    "page_number": page_num + 1,
                    "text": "",
                    "is_scanned": False,
                    "extraction_method": "text"
                }
                
                # Check if page is scanned
                if self.is_page_scanned(page_num):
                    page_info["is_scanned"] = True
                    page_info["extraction_method"] = "ocr"
                    text = self.extract_text_with_ocr(page_num)
                else:
                    text = self.extract_text_from_page(page_num)
                
                page_info["text"] = text
                result["pages"].append(page_info)
                full_text_parts.append(text)
                
                # Update overall extraction method
                if page_info["is_scanned"]:
                    result["extraction_method"] = "mixed"
            
            result["full_text"] = "\n\n".join(full_text_parts)
            
            return result
            
        finally:
            # Always close the file handle
            self.close_pdf()

def process_pdf_file(file_path: str) -> Dict:
    """Main function to process a PDF file."""
    try:
        processor = PDFProcessor(file_path)
        result = processor.process_document()
        return result
    except Exception as e:
        logger.error(f"Error processing PDF {file_path}: {e}")
        return {"error": str(e)}
