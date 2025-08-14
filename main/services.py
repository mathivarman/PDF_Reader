"""
Service layer for PDF processing and analysis.
Integrates PDF processing with Django models.
"""

import os
import logging
from typing import Dict, List, Optional
from django.conf import settings
from django.core.files.storage import default_storage
from django.db import transaction

from .models import Document, Analysis, DocumentChunk, UserSession, Clause, RedFlag
from .pdf_processor import PDFProcessor
from .text_processor import TextProcessor, DocumentAnalyzer
from .clause_detector import ClauseDetector, ClauseType, ImportanceLevel
from .red_flag_detector import RedFlagDetector, RedFlagCategory, RiskLevel
from .cache_manager import CacheManager
from .performance_monitor import monitor_performance, track_performance
from .semantic_search import semantic_search_engine

logger = logging.getLogger(__name__)

def generate_simple_summary(document_text: str, clauses: List, red_flags: List, analysis_data: Dict) -> str:
    """
    Generate a simple, easy-to-understand summary of the legal document.
    
    Args:
        document_text: The full text of the document
        clauses: List of detected clauses
        red_flags: List of detected red flags
        analysis_data: Document analysis data
        
    Returns:
        Simple summary in plain English
    """
    try:
        # Extract key information
        word_count = analysis_data.get('total_words', 0)
        page_count = analysis_data.get('page_count', 0)
        complexity = analysis_data.get('estimated_complexity', 'medium')
        
        # Count important clauses - handle both DetectedClause objects and dict-like objects
        critical_clauses = []
        high_clauses = []
        
        for clause in clauses:
            # Handle DetectedClause objects
            if hasattr(clause, 'importance'):
                if clause.importance == 'critical' or clause.importance == ImportanceLevel.CRITICAL:
                    critical_clauses.append(clause)
                elif clause.importance == 'high' or clause.importance == ImportanceLevel.HIGH:
                    high_clauses.append(clause)
            # Handle dict-like objects
            elif isinstance(clause, dict):
                if clause.get('importance') == 'critical':
                    critical_clauses.append(clause)
                elif clause.get('importance') == 'high':
                    high_clauses.append(clause)
        
        # Count red flags by severity
        critical_flags = []
        high_flags = []
        
        for red_flag in red_flags:
            # Handle DetectedRedFlag objects
            if hasattr(red_flag, 'risk_level'):
                if red_flag.risk_level == 'critical' or red_flag.risk_level == RiskLevel.CRITICAL:
                    critical_flags.append(red_flag)
                elif red_flag.risk_level == 'high' or red_flag.risk_level == RiskLevel.HIGH:
                    high_flags.append(red_flag)
            # Handle dict-like objects
            elif isinstance(red_flag, dict):
                if red_flag.get('risk_level') == 'critical':
                    critical_flags.append(red_flag)
                elif red_flag.get('risk_level') == 'high':
                    high_flags.append(red_flag)
        
        # Generate content summary from document text
        content_summary = generate_content_summary(document_text, clauses)
        
        # Generate condensed document summary
        document_summary = generate_document_summary(document_text, target_words=300)
        
        # Generate simple summary
        summary_parts = []
        
        # Document overview
        summary_parts.append(f"This is a {complexity}-complexity legal document with {word_count:,} words across {page_count} pages.")
        
        # Condensed document summary
        if document_summary:
            summary_parts.append(f"<p>📄 <strong>Document Summary ({len(document_summary.split())} words):</strong> {document_summary}</p>")
        
        # Content summary
        if content_summary:
            summary_parts.append(f"<p>📝 <strong>Key Information:</strong> {content_summary}</p>")
        
        # Key findings
        if critical_clauses:
            summary_parts.append(f"<p>⚠️ {len(critical_clauses)} critical clauses require immediate attention.</p>")
        if high_clauses:
            summary_parts.append(f"<p>📋 {len(high_clauses)} important clauses should be reviewed carefully.</p>")
        
        if critical_flags:
            summary_parts.append(f"<p>🚨 {len(critical_flags)} critical risks identified - legal consultation recommended.</p>")
        elif high_flags:
            summary_parts.append(f"<p>⚠️ {len(high_flags)} high-risk issues found - review recommended.</p>")
        else:
            summary_parts.append("<p>✅ No significant risks detected in this document.</p>")
        
        # Document type identification
        clause_types = []
        for clause in clauses:
            if hasattr(clause, 'clause_type'):
                clause_types.append(str(clause.clause_type).lower())
            elif isinstance(clause, dict):
                clause_types.append(str(clause.get('clause_type', '')).lower())
        
        if any('lease' in ct for ct in clause_types):
            summary_parts.append("<p>📄 This appears to be a lease agreement.</p>")
        elif any('employment' in ct for ct in clause_types):
            summary_parts.append("<p>📄 This appears to be an employment contract.</p>")
        elif any('service' in ct for ct in clause_types):
            summary_parts.append("<p>📄 This appears to be a service agreement.</p>")
        else:
            summary_parts.append("<p>📄 This is a legal contract or agreement.</p>")
        
        # Key recommendations
        if critical_clauses or critical_flags:
            summary_parts.append("<p>💡 <strong>Recommendation:</strong> Consider consulting with a legal professional before signing.</p>")
        elif high_clauses or high_flags:
            summary_parts.append("<p>💡 <strong>Recommendation:</strong> Review carefully and consider legal advice for complex terms.</p>")
        else:
            summary_parts.append("<p>💡 <strong>Recommendation:</strong> Document appears standard, but always read carefully.</p>")
        
        return "".join(summary_parts)
        
    except Exception as e:
        logger.error(f"Error generating simple summary: {e}")
        return "Summary generation failed. Please review the document manually."

def generate_content_summary(document_text: str, clauses: List) -> str:
    """
    Generate a brief content summary of the document based on text analysis and detected clauses.
    
    Args:
        document_text: The full text of the document
        clauses: List of detected clauses
        
    Returns:
        Brief content summary in plain English
    """
    try:
        # Extract key information from document text
        text_lower = document_text.lower()
        
        # Identify document type and purpose
        document_type = "legal agreement"
        document_purpose = ""
        
        # Look for specific document types
        if any(word in text_lower for word in ['lease', 'rental', 'tenancy']):
            document_type = "lease agreement"
            document_purpose = "This document establishes the terms for renting or leasing property."
        elif any(word in text_lower for word in ['employment', 'employee', 'worker']):
            document_type = "employment contract"
            document_purpose = "This document defines the employment relationship and job terms."
        elif any(word in text_lower for word in ['service', 'consulting', 'professional']):
            document_type = "service agreement"
            document_purpose = "This document outlines the terms for providing or receiving services."
        elif any(word in text_lower for word in ['purchase', 'sale', 'buy', 'sell']):
            document_type = "purchase agreement"
            document_purpose = "This document governs the purchase or sale of goods or services."
        elif any(word in text_lower for word in ['partnership', 'joint venture', 'collaboration']):
            document_type = "partnership agreement"
            document_purpose = "This document establishes a business partnership or collaboration."
        elif any(word in text_lower for word in ['nda', 'non-disclosure', 'confidentiality']):
            document_type = "non-disclosure agreement"
            document_purpose = "This document protects confidential information and trade secrets."
        
        # Identify document parties
        parties = []
        if 'between' in text_lower:
            # Look for party names after "between"
            between_index = text_lower.find('between')
            if between_index != -1:
                # Extract text around "between"
                start = max(0, between_index - 100)
                end = min(len(document_text), between_index + 200)
                context = document_text[start:end]
                
                # Look for common party indicators
                party_indicators = ['company', 'corporation', 'inc.', 'llc', 'ltd', 'partnership', 'individual', 'person']
                for indicator in party_indicators:
                    if indicator in context.lower():
                        parties.append(indicator)
        
        # Identify key topics based on clause types
        topics = []
        clause_types = []
        for clause in clauses:
            if hasattr(clause, 'clause_type'):
                clause_types.append(str(clause.clause_type).lower())
            elif isinstance(clause, dict):
                clause_types.append(str(clause.get('clause_type', '')).lower())
        
        # Map clause types to user-friendly topics
        topic_mapping = {
            'termination': 'how the agreement can be ended',
            'auto_renewal': 'automatic renewal terms',
            'penalties': 'penalties and consequences',
            'confidentiality': 'confidentiality requirements',
            'liability': 'responsibility and liability limits',
            'payment': 'payment terms and schedules',
            'delivery': 'delivery and service requirements',
            'warranty': 'warranties and guarantees',
            'indemnification': 'protection and indemnification',
            'non_compete': 'non-compete restrictions',
            'intellectual_property': 'intellectual property rights',
            'dispute_resolution': 'how disputes will be resolved',
            'notice': 'notification requirements',
            'governing_law': 'which laws apply',
            'force_majeure': 'unforeseen circumstances'
        }
        
        for clause_type in clause_types:
            if clause_type in topic_mapping:
                topics.append(topic_mapping[clause_type])
        
        # Remove duplicates and limit to top topics
        topics = list(set(topics))[:4]
        
        # Generate content summary
        summary_parts = []
        
        # Document type and purpose
        if document_purpose:
            summary_parts.append(document_purpose)
        else:
            summary_parts.append(f"This is a {document_type} that establishes legal terms and conditions.")
        
        # Parties involved
        if parties:
            party_text = " and ".join(parties[:2])
            summary_parts.append(f"It involves {party_text}.")
        
        # Key topics covered
        if topics:
            if len(topics) == 1:
                summary_parts.append(f"The document specifically addresses {topics[0]}.")
            elif len(topics) == 2:
                summary_parts.append(f"The document covers {topics[0]} and {topics[1]}.")
            else:
                topics_text = ", ".join(topics[:-1]) + f", and {topics[-1]}"
                summary_parts.append(f"The document addresses {topics_text}.")
        
        # Document scope and complexity
        if len(document_text) > 15000:
            summary_parts.append("This is a very detailed and comprehensive legal document.")
        elif len(document_text) > 10000:
            summary_parts.append("This is a comprehensive legal agreement with extensive terms.")
        elif len(document_text) > 5000:
            summary_parts.append("This is a standard legal contract with typical business terms.")
        else:
            summary_parts.append("This is a relatively concise legal document.")
        
        return " ".join(summary_parts)
        
    except Exception as e:
        logger.error(f"Error generating content summary: {e}")
        return "This document contains legal terms and conditions that establish an agreement between parties."

def generate_document_summary(document_text: str, target_words: int = 300) -> str:
    """
    Generate a condensed summary of the document content in simple English.
    
    Args:
        document_text: The full text of the document
        target_words: Target number of words for the summary (default: 300)
        
    Returns:
        Condensed document summary in plain English
    """
    try:
        # Clean and prepare text
        import re
        from collections import Counter
        
        # Remove extra whitespace and normalize
        text = re.sub(r'\s+', ' ', document_text.strip())
        text_lower = text.lower()
        
        # Split into sentences
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if len(s.strip()) > 20]  # Filter short sentences
        
        # Extract key information patterns
        key_patterns = {
            'parties': r'(?:between|by and between|agreement between)\s+([A-Z][A-Z\s]+?)(?:\s+and\s+|\s*,\s*)([A-Z][A-Z\s]+?)(?:\s|$)',
            'effective_date': r'(?:effective|commencement|start)\s+(?:date|as of)\s*:?\s*([^,\n]{5,50})',
            'term': r'(?:term|duration|period)\s+(?:of|for)\s+([^,\n]{5,50})',
            'payment': r'(?:payment|fee|price|cost)\s+(?:of|is|amounts? to)\s+([^,\n]{5,50})',
            'termination': r'(?:terminate|termination|end|expire)\s+(?:may|can|will|upon)\s+([^,\n]{5,50})',
            'obligations': r'(?:shall|will|must|agree to)\s+([^,\n]{10,80})',
            'rights': r'(?:right|entitled|may|can)\s+(?:to|for)\s+([^,\n]{10,80})'
        }
        
        extracted_info = {}
        for key, pattern in key_patterns.items():
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                # Clean and format matches
                cleaned_matches = []
                for match in matches[:3]:  # Limit to top 3 matches
                    if isinstance(match, tuple):
                        # Handle tuple matches (like parties)
                        cleaned_match = tuple(re.sub(r'\s+', ' ', m.strip()) for m in match)
                    else:
                        # Handle single string matches
                        cleaned_match = re.sub(r'\s+', ' ', match.strip())
                    cleaned_matches.append(cleaned_match)
                extracted_info[key] = cleaned_matches
        
        # Identify document structure
        sections = []
        section_keywords = [
            'recitals', 'definitions', 'scope', 'services', 'payment', 'term', 
            'termination', 'confidentiality', 'liability', 'indemnification',
            'dispute resolution', 'governing law', 'notices', 'miscellaneous'
        ]
        
        for keyword in section_keywords:
            if keyword in text_lower:
                sections.append(keyword.replace('_', ' ').title())
        
        # Generate summary parts
        summary_parts = []
        
        # Document overview
        word_count = len(text.split())
        summary_parts.append(f"This {word_count}-word legal document")
        
        # Document type identification
        if any(word in text_lower for word in ['lease', 'rental', 'tenancy']):
            summary_parts.append("is a lease agreement")
        elif any(word in text_lower for word in ['employment', 'employee', 'worker']):
            summary_parts.append("is an employment contract")
        elif any(word in text_lower for word in ['service', 'consulting', 'saas', 'software']):
            summary_parts.append("is a service agreement")
        elif any(word in text_lower for word in ['purchase', 'sale', 'buy', 'sell']):
            summary_parts.append("is a purchase agreement")
        elif any(word in text_lower for word in ['nda', 'non-disclosure', 'confidentiality']):
            summary_parts.append("is a non-disclosure agreement")
        elif any(word in text_lower for word in ['partnership', 'joint venture']):
            summary_parts.append("is a partnership agreement")
        else:
            summary_parts.append("is a legal contract")
        
        # Parties involved
        if 'parties' in extracted_info:
            parties = extracted_info['parties'][0]
            if len(parties) >= 2:
                party1 = parties[0].strip()
                party2 = parties[1].strip()
                summary_parts.append(f"between {party1} and {party2}")
        
        # Key terms and conditions
        key_points = []
        
        if 'effective_date' in extracted_info:
            date_info = extracted_info['effective_date'][0]
            if len(date_info) > 5:  # Only add if meaningful
                key_points.append(f"Effective date: {date_info}")
        
        if 'term' in extracted_info:
            term_info = extracted_info['term'][0]
            if len(term_info) > 5:  # Only add if meaningful
                key_points.append(f"Contract term: {term_info}")
        
        if 'payment' in extracted_info:
            payment_info = extracted_info['payment'][0]
            if len(payment_info) > 5:  # Only add if meaningful
                key_points.append(f"Payment: {payment_info}")
        
        # Add key obligations and rights (limit length)
        if 'obligations' in extracted_info:
            obligations = extracted_info['obligations'][:1]  # Top 1 obligation
            for obligation in obligations:
                if len(obligation) > 10 and len(obligation) < 80:
                    key_points.append(f"Key obligation: {obligation}")
        
        if 'rights' in extracted_info:
            rights = extracted_info['rights'][:1]  # Top 1 right
            for right in rights:
                if len(right) > 10 and len(right) < 80:
                    key_points.append(f"Key right: {right}")
        
        # Add termination information
        if 'termination' in extracted_info:
            termination_info = extracted_info['termination'][0]
            if len(termination_info) > 5:  # Only add if meaningful
                key_points.append(f"Termination: {termination_info}")
        
        # Document structure
        if sections:
            summary_parts.append(f"covering {', '.join(sections[:5])}")
        
        # Combine summary
        full_summary = " ".join(summary_parts) + "."
        
        # Add key points if space allows
        if key_points and len(full_summary.split()) < target_words * 0.7:
            # Clean and format key points
            cleaned_points = []
            for point in key_points[:3]:
                # Clean up the point text
                point = re.sub(r'\s+', ' ', point.strip())
                # Limit point length
                if len(point) > 100:
                    point = point[:100] + "..."
                cleaned_points.append(point)
            
            key_points_text = " Key points include: " + "; ".join(cleaned_points)
            full_summary += key_points_text
        
        # Truncate if too long
        words = full_summary.split()
        if len(words) > target_words:
            words = words[:target_words]
            full_summary = " ".join(words) + "..."
        
        return full_summary
        
    except Exception as e:
        logger.error(f"Error generating document summary: {e}")
        return "This document contains legal terms and conditions that establish an agreement between parties."

class DocumentProcessingService:
    """Service for processing uploaded documents."""
    
    @staticmethod
    @monitor_performance("document_processing")
    def process_document(document_id) -> Dict:
        """
        Process a document and create analysis records.
        
        Args:
            document_id: ID of the document to process
            
        Returns:
            Dict containing processing results
        """
        try:
            # Get document
            document = Document.objects.get(id=document_id)
            
            # Get file path
            file_path = default_storage.path(document.file.name)
            
            # Process PDF
            processor = PDFProcessor(file_path)
            result = processor.process_document()
            
            if "error" in result:
                return {"error": result["error"]}
            
            # Clean and analyze text
            cleaned_text = TextProcessor.clean_text(result["full_text"])
            analyzer = DocumentAnalyzer()
            analysis_data = analyzer.analyze_document_structure(cleaned_text)
            key_info = analyzer.extract_key_information(cleaned_text)
            
            # Create chunks
            chunks = TextProcessor.split_into_chunks(cleaned_text)
            
            # Initialize clause and red flag detectors
            clause_detector = ClauseDetector()
            red_flag_detector = RedFlagDetector()
            
            # Detect clauses and red flags
            all_clauses = []
            all_red_flags = []
            
            # Process each page for clauses and red flags
            for page_num, page_info in enumerate(result["pages"]):
                page_text = page_info["text"]
                if page_text and not page_text.startswith("[OCR"):
                    # Detect clauses
                    detected_clauses = clause_detector.detect_clauses(page_text, page_num + 1)
                    all_clauses.extend(detected_clauses)
                    
                    # Detect red flags
                    detected_red_flags = red_flag_detector.detect_red_flags(page_text, page_num + 1)
                    all_red_flags.extend(detected_red_flags)
            
            # Save to database
            with transaction.atomic():
                # Update document with page count
                document.pages = result["page_count"]
                document.status = "processed"
                document.save()
                
                # Create analysis record
                analysis = Analysis.objects.create(
                    document=document,
                    extraction_method=result["extraction_method"],
                    total_words=analysis_data["total_words"],
                    total_sentences=analysis_data["total_sentences"],
                    complexity_level=analysis_data["estimated_complexity"],
                    legal_terms_found=", ".join(analysis_data["legal_terms_found"]),
                    processing_notes=f"Processed {result['page_count']} pages using {result['extraction_method']} method"
                )
                
                # Create document chunks with embeddings
                from .semantic_search import semantic_search_engine
                
                # Generate embeddings for chunks
                embeddings = semantic_search_engine.create_embeddings(chunks)
                
                for i, (chunk_text, embedding) in enumerate(zip(chunks, embeddings)):
                    DocumentChunk.objects.create(
                        document=document,
                        chunk_index=i,
                        chunk_text=chunk_text,
                        page_number=0,  # Default page number
                        embedding=embedding.tolist()
                    )
                
                # Save detected clauses
                for detected_clause in all_clauses:
                    Clause.objects.create(
                        document=document,
                        analysis=analysis,
                        clause_type=detected_clause.clause_type.value,
                        importance=detected_clause.importance.value,
                        title=detected_clause.clause_type.value.replace('_', ' ').title(),
                        snippet=detected_clause.text,
                        page_number=detected_clause.page_number,
                        start_position=detected_clause.start_pos,
                        end_position=detected_clause.end_pos,
                        confidence_score=detected_clause.confidence
                    )
                
                # Save detected red flags
                for detected_red_flag in all_red_flags:
                    RedFlag.objects.create(
                        document=document,
                        analysis=analysis,
                        category=detected_red_flag.category.value,
                        risk_level=detected_red_flag.risk_level.value,
                        title=detected_red_flag.title,
                        description=detected_red_flag.description,
                        reason=detected_red_flag.reasoning,
                        recommendations=detected_red_flag.recommendations,
                        page_number=detected_red_flag.page_number,
                        start_position=detected_red_flag.start_pos,
                        end_position=detected_red_flag.end_pos,
                        snippet=detected_red_flag.text,
                        confidence_score=detected_red_flag.confidence
                    )
                
                # Create analysis summary
                clause_summary = clause_detector.get_clause_summary(all_clauses)
                red_flag_summary = red_flag_detector.get_red_flag_summary(all_red_flags)
                
                # Generate simple summary for users
                simple_summary = generate_simple_summary(
                    cleaned_text, 
                    all_clauses, 
                    all_red_flags, 
                    {
                        'total_words': analysis_data['total_words'],
                        'page_count': result['page_count'],
                        'estimated_complexity': analysis_data['estimated_complexity']
                    }
                )
                
                analysis.summary = f"""
                Document Analysis Complete:
                - Pages: {result['page_count']}
                - Words: {analysis_data['total_words']}
                - Sentences: {analysis_data['total_sentences']}
                - Complexity: {analysis_data['estimated_complexity']}
                - Legal Terms: {len(analysis_data['legal_terms_found'])}
                - Extraction Method: {result['extraction_method']}
                - Clauses Detected: {clause_summary['total_clauses']}
                - Red Flags: {red_flag_summary['total_red_flags']}
                - Critical Red Flags: {red_flag_summary['critical_flags']}
                """
                
                # Store simple summary in processing notes
                analysis.processing_notes = f"Processed {result['page_count']} pages using {result['extraction_method']} method\n\nSimple Summary:\n{simple_summary}"
                analysis.save()
            
            return {
                "success": True,
                "document_id": document.id,
                "analysis_id": analysis.id,
                "page_count": result["page_count"],
                "word_count": analysis_data["total_words"],
                "complexity": analysis_data["estimated_complexity"],
                "extraction_method": result["extraction_method"]
            }
            
        except Document.DoesNotExist:
            return {"error": "Document not found"}
        except Exception as e:
            logger.error(f"Error processing document {document_id}: {e}")
            return {"error": str(e)}
    
    @staticmethod
    @monitor_performance("document_analysis_retrieval")
    def get_document_analysis(document_id) -> Dict:
        """
        Get analysis results for a document.
        
        Args:
            document_id: ID of the document
            
        Returns:
            Dict containing analysis data
        """
        try:
            # Check cache first
            cached_analysis = CacheManager.get_cached_analysis(str(document_id))
            if cached_analysis:
                logger.info(f"Retrieved cached analysis for document {document_id}")
                return cached_analysis
            
            # If not in cache, fetch from database
            document = Document.objects.get(id=document_id)
            analysis = Analysis.objects.filter(document=document).first()
            chunks = DocumentChunk.objects.filter(document=document).order_by('chunk_index')
            clauses = Clause.objects.filter(document=document).order_by('-confidence_score')
            red_flags = RedFlag.objects.filter(document=document).order_by('-confidence_score')
            
            if not analysis:
                return {"error": "No analysis found for document"}
            
            analysis_data = {
                "document": {
                    "id": document.id,
                    "title": document.title,
                    "original_filename": document.original_filename,
                    "pages": document.pages,
                    "file_size": document.file_size,
                    "status": document.status,
                    "uploaded_at": document.uploaded_at
                },
                "analysis": {
                    "id": analysis.id,
                    "extraction_method": analysis.extraction_method,
                    "total_words": analysis.total_words,
                    "total_sentences": analysis.total_sentences,
                    "complexity_level": analysis.complexity_level,
                    "legal_terms_found": analysis.legal_terms_found.split(", ") if analysis.legal_terms_found else [],
                    "summary": analysis.summary,
                    "created_at": analysis.created_at,
                    "processing_notes": analysis.processing_notes
                },
                "chunks": [
                    {
                        "index": chunk.chunk_index,
                        "content": chunk.chunk_text,
                        "word_count": len(chunk.chunk_text.split())
                    }
                    for chunk in chunks
                ],
                "clauses": [
                    {
                        "id": clause.id,
                        "type": clause.clause_type,
                        "importance": clause.importance,
                        "title": clause.title,
                        "snippet": clause.snippet,
                        "page_number": clause.page_number,
                        "confidence_score": clause.confidence_score
                    }
                    for clause in clauses
                ],
                "red_flags": [
                    {
                        "id": red_flag.id,
                        "category": red_flag.category,
                        "risk_level": red_flag.risk_level,
                        "title": red_flag.title,
                        "description": red_flag.description,
                        "reason": red_flag.reason,
                        "recommendations": red_flag.recommendations,
                        "snippet": red_flag.snippet,
                        "page_number": red_flag.page_number,
                        "confidence_score": red_flag.confidence_score
                    }
                    for red_flag in red_flags
                ]
            }
            
            # Process document for semantic search
            try:
                semantic_search_engine.process_document_chunks(document)
                logger.info(f"Semantic search processing completed for document {document_id}")
            except Exception as e:
                logger.warning(f"Semantic search processing failed for document {document_id}: {e}")
            
            # Cache the analysis results
            CacheManager.cache_document_analysis(str(document_id), analysis_data)
            
            return analysis_data
            
        except Document.DoesNotExist:
            return {"error": "Document not found"}
        except Exception as e:
            logger.error(f"Error getting analysis for document {document_id}: {e}")
            return {"error": str(e)}

class UserSessionService:
    """Service for managing user sessions."""
    
    @staticmethod
    def get_or_create_session(session_id: str) -> UserSession:
        """
        Get or create a user session.
        
        Args:
            session_id: Django session ID
            
        Returns:
            UserSession instance
        """
        session, created = UserSession.objects.get_or_create(
            session_id=session_id,
            defaults={
                "is_active": True
            }
        )
        
        if not created:
            session.is_active = True
            session.save()
        
        return session
    
    @staticmethod
    def get_user_documents(session_id: str) -> List[Document]:
        """
        Get all documents for a user session.
        
        Args:
            session_id: Django session ID
            
        Returns:
            List of Document instances
        """
        try:
            session = UserSession.objects.get(session_id=session_id, is_active=True)
            return Document.objects.filter(user_session=session).order_by('-uploaded_at')
        except UserSession.DoesNotExist:
            return []

class DocumentManagementService:
    """Service for document management operations."""
    
    @staticmethod
    def delete_document(document_id, session_id: str) -> Dict:
        """
        Delete a document and its associated data.
        
        Args:
            document_id: ID of the document to delete
            session_id: Session ID for verification
            
        Returns:
            Dict containing operation result
        """
        try:
            # Verify ownership
            session = UserSession.objects.get(session_id=session_id, is_active=True)
            document = Document.objects.get(id=document_id, user_session=session)
            
            # Delete associated data
            Analysis.objects.filter(document=document).delete()
            DocumentChunk.objects.filter(document=document).delete()
            
            # Delete file
            if document.file:
                default_storage.delete(document.file.name)
            
            # Delete document
            document.delete()
            
            return {"success": True, "message": "Document deleted successfully"}
            
        except (UserSession.DoesNotExist, Document.DoesNotExist):
            return {"error": "Document not found or access denied"}
        except Exception as e:
            logger.error(f"Error deleting document {document_id}: {e}")
            return {"error": str(e)}
    
    @staticmethod
    def get_document_stats(session_id: str) -> Dict:
        """
        Get statistics for user's documents.
        
        Args:
            session_id: Django session ID
            
        Returns:
            Dict containing statistics
        """
        try:
            session = UserSession.objects.get(session_id=session_id, is_active=True)
            documents = Document.objects.filter(user_session=session)
            
            total_documents = documents.count()
            processed_documents = documents.filter(status="processed").count()
            total_pages = sum(doc.pages or 0 for doc in documents)
            total_size = sum(doc.file_size or 0 for doc in documents)
            
            return {
                "total_documents": total_documents,
                "processed_documents": processed_documents,
                "pending_documents": total_documents - processed_documents,
                "total_pages": total_pages,
                "total_size_mb": round(total_size / (1024 * 1024), 2),
                "average_pages": round(total_pages / total_documents, 1) if total_documents > 0 else 0
            }
            
        except UserSession.DoesNotExist:
            return {
                "total_documents": 0,
                "processed_documents": 0,
                "pending_documents": 0,
                "total_pages": 0,
                "total_size_mb": 0,
                "average_pages": 0
            }
