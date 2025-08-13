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

logger = logging.getLogger(__name__)

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
                
                # Create document chunks
                for i, chunk_text in enumerate(chunks):
                    DocumentChunk.objects.create(
                        document=document,
                        chunk_index=i,
                        chunk_text=chunk_text,
                        page_number=0  # Default page number
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
