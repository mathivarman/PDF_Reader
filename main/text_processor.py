"""
Text processing utilities for cleaning and analyzing extracted text.
"""

import re
from typing import Dict, List, Tuple
import logging

logger = logging.getLogger(__name__)

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
