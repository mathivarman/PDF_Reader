"""
Utility functions for PDF processing and text extraction.
Handles both text-based PDFs and scanned documents using OCR.
"""

import os
import fitz  # PyMuPDF
import pytesseract
from PIL import Image
import io
import re
from typing import Dict, List, Tuple, Optional
import logging

logger = logging.getLogger(__name__)

class PDFProcessor:
    """Handles PDF text extraction and OCR processing."""
    
    def __init__(self, pdf_path: str):
        self.pdf_path = pdf_path
        self.doc = None
        self.page_count = 0
        
    def open_pdf(self) -> bool:
        """Open and validate PDF file."""
        try:
            self.doc = fitz.open(self.pdf_path)
            self.page_count = len(self.doc)
            return True
        except Exception as e:
            logger.error(f"Error opening PDF {self.pdf_path}: {e}")
            return False
    
    def extract_text_from_page(self, page_num: int) -> str:
        """Extract text from a specific page."""
        try:
            page = self.doc[page_num]
            text = page.get_text()
            return text.strip()
        except Exception as e:
            logger.error(f"Error extracting text from page {page_num}: {e}")
            return ""
    
    def is_page_scanned(self, page_num: int) -> bool:
        """Check if a page is scanned (image-based)."""
        try:
            page = self.doc[page_num]
            text = page.get_text().strip()
            # If very little text is extracted, it's likely scanned
            return len(text) < 50
        except Exception as e:
            logger.error(f"Error checking if page {page_num} is scanned: {e}")
            return True
    
    def extract_text_with_ocr(self, page_num: int) -> str:
        """Extract text from scanned page using OCR."""
        try:
            page = self.doc[page_num]
            # Convert page to image
            mat = fitz.Matrix(2.0, 2.0)  # Higher resolution for better OCR
            pix = page.get_pixmap(matrix=mat)
            img_data = pix.tobytes("png")
            
            # Convert to PIL Image
            img = Image.open(io.BytesIO(img_data))
            
            # Perform OCR
            text = pytesseract.image_to_string(img)
            return text.strip()
        except Exception as e:
            logger.error(f"Error performing OCR on page {page_num}: {e}")
            return ""
    
    def process_document(self) -> Dict:
        """Process entire document and extract text from all pages."""
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
        
        if self.doc:
            self.doc.close()
        
        return result

class TextProcessor:
    """Handles text cleaning and chunking for analysis."""
    
    @staticmethod
    def clean_text(text: str) -> str:
        """Clean and normalize extracted text."""
        if not text:
            return ""
        
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters but keep legal terms
        text = re.sub(r'[^\w\s\.\,\;\:\!\?\-\(\)\[\]\{\}\"\']', ' ', text)
        
        # Normalize quotes and dashes
        text = text.replace('"', '"').replace('"', '"')
        text = text.replace('–', '-').replace('—', '-')
        
        return text.strip()
    
    @staticmethod
    def split_into_chunks(text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
        """Split text into overlapping chunks for processing."""
        if not text:
            return []
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + chunk_size
            
            # Try to break at sentence boundary
            if end < len(text):
                # Look for sentence endings
                sentence_end = text.rfind('.', start, end)
                if sentence_end > start + chunk_size // 2:
                    end = sentence_end + 1
            
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            
            start = end - overlap
            if start >= len(text):
                break
        
        return chunks
    
    @staticmethod
    def extract_sentences(text: str) -> List[str]:
        """Extract individual sentences from text."""
        if not text:
            return []
        
        # Split on sentence endings
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        return sentences
    
    @staticmethod
    def find_legal_terms(text: str) -> List[str]:
        """Find common legal terms in text."""
        legal_terms = [
            'whereas', 'hereby', 'hereinafter', 'herein', 'hereof', 'hereto',
            'termination', 'liability', 'indemnification', 'confidentiality',
            'arbitration', 'jurisdiction', 'force majeure', 'breach',
            'damages', 'penalty', 'remedy', 'waiver', 'amendment',
            'assignment', 'governing law', 'entire agreement'
        ]
        
        found_terms = []
        text_lower = text.lower()
        
        for term in legal_terms:
            if term in text_lower:
                found_terms.append(term)
        
        return found_terms

class DocumentAnalyzer:
    """Analyzes document structure and content."""
    
    @staticmethod
    def analyze_document_structure(text: str) -> Dict:
        """Analyze document structure and identify sections."""
        analysis = {
            "total_words": len(text.split()),
            "total_sentences": len(TextProcessor.extract_sentences(text)),
            "legal_terms_found": TextProcessor.find_legal_terms(text),
            "estimated_complexity": "medium",
            "sections": []
        }
        
        # Estimate complexity based on text length and legal terms
        word_count = analysis["total_words"]
        legal_terms = len(analysis["legal_terms_found"])
        
        if word_count > 5000 or legal_terms > 10:
            analysis["estimated_complexity"] = "high"
        elif word_count < 1000 or legal_terms < 3:
            analysis["estimated_complexity"] = "low"
        
        # Identify potential sections (basic implementation)
        lines = text.split('\n')
        current_section = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Look for section headers (numbered or capitalized)
            if re.match(r'^\d+\.', line) or (line.isupper() and len(line) < 100):
                if current_section:
                    analysis["sections"].append(current_section)
                
                current_section = {
                    "title": line,
                    "content": "",
                    "start_line": len(analysis["sections"]) + 1
                }
            elif current_section:
                current_section["content"] += line + " "
        
        if current_section:
            analysis["sections"].append(current_section)
        
        return analysis
    
    @staticmethod
    def extract_key_information(text: str) -> Dict:
        """Extract key information from document."""
        info = {
            "parties": [],
            "dates": [],
            "amounts": [],
            "locations": [],
            "key_clauses": []
        }
        
        # Extract dates
        date_patterns = [
            r'\d{1,2}/\d{1,2}/\d{4}',
            r'\d{1,2}-\d{1,2}-\d{4}',
            r'\d{4}-\d{1,2}-\d{1,2}',
            r'\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4}\b'
        ]
        
        for pattern in date_patterns:
            dates = re.findall(pattern, text, re.IGNORECASE)
            info["dates"].extend(dates)
        
        # Extract monetary amounts
        amount_pattern = r'\$[\d,]+(?:\.\d{2})?'
        info["amounts"] = re.findall(amount_pattern, text)
        
        # Extract potential party names (simple heuristic)
        lines = text.split('\n')
        for line in lines:
            line = line.strip()
            if 'between' in line.lower() or 'and' in line.lower():
                # Look for capitalized words that might be party names
                words = line.split()
                for i, word in enumerate(words):
                    if word.isupper() and len(word) > 2:
                        if i < len(words) - 1 and words[i + 1].isupper():
                            party = f"{word} {words[i + 1]}"
                            if party not in info["parties"]:
                                info["parties"].append(party)
        
        return info

def process_pdf_file(file_path: str) -> Dict:
    """Main function to process a PDF file."""
    try:
        # Initialize processor
        processor = PDFProcessor(file_path)
        
        # Process document
        result = processor.process_document()
        
        if "error" in result:
            return result
        
        # Clean text
        cleaned_text = TextProcessor.clean_text(result["full_text"])
        result["cleaned_text"] = cleaned_text
        
        # Analyze document
        analyzer = DocumentAnalyzer()
        result["analysis"] = analyzer.analyze_document_structure(cleaned_text)
        result["key_info"] = analyzer.extract_key_information(cleaned_text)
        
        # Create chunks for processing
        result["chunks"] = TextProcessor.split_into_chunks(cleaned_text)
        
        return result
        
    except Exception as e:
        logger.error(f"Error processing PDF {file_path}: {e}")
        return {"error": str(e)}
