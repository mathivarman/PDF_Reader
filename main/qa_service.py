"""
Q&A Service for Document Question Answering
Handles question processing, answer generation, and confidence scoring
Enhanced for Week 10: Advanced Q&A Engine
"""

import logging
import time
import re
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from enum import Enum

from django.db import transaction, models
from .models import Document, Question, Answer, Citation, DocumentChunk
from .semantic_search import semantic_search_engine
from .performance_monitor import monitor_performance
from .confidence_engine import confidence_analyzer, ConfidenceFactors
from .recommendation_engine import recommendation_manager

logger = logging.getLogger(__name__)

class QuestionType(Enum):
    """Question classification types."""
    FACTUAL = "factual"
    COMPARISON = "comparison"
    PROCEDURAL = "procedural"
    INTERPRETATION = "interpretation"
    YES_NO = "yes_no"
    UNKNOWN = "unknown"

class QuestionProcessor:
    """Advanced question processing and classification."""
    
    def __init__(self):
        """Initialize question processor."""
        # Question type patterns
        self.question_patterns = {
            QuestionType.YES_NO: [
                r'\b(is|are|was|were|does|do|did|has|have|had|can|could|will|would|should)\b.*\?',
                r'\b(yes|no)\b.*\?',
                r'\?$'
            ],
            QuestionType.COMPARISON: [
                r'\b(compare|difference|similar|versus|vs|between|among)\b',
                r'\b(which|what).*\b(better|worse|more|less|higher|lower)\b'
            ],
            QuestionType.PROCEDURAL: [
                r'\b(how|what.*steps|procedure|process|method)\b',
                r'\b(what.*do|what.*should|instructions|guide)\b'
            ],
            QuestionType.INTERPRETATION: [
                r'\b(what.*mean|interpret|explain|understand|imply)\b',
                r'\b(why|reason|cause|purpose|intent)\b'
            ],
            QuestionType.FACTUAL: [
                r'\b(what|when|where|who|which)\b',
                r'\b(amount|number|date|time|location|person)\b'
            ]
        }
    
    def preprocess_question(self, question_text: str) -> Dict[str, Any]:
        """Preprocess and analyze question."""
        try:
            # Clean question text
            cleaned_text = self._clean_question_text(question_text)
            
            # Classify question type
            question_type = self._classify_question(cleaned_text)
            
            # Extract key terms
            key_terms = self._extract_key_terms(cleaned_text)
            
            # Determine complexity
            complexity = self._assess_complexity(cleaned_text)
            
            return {
                'original_text': question_text,
                'cleaned_text': cleaned_text,
                'question_type': question_type.value,
                'key_terms': key_terms,
                'complexity': complexity,
                'word_count': len(cleaned_text.split()),
                'has_legal_terms': self._has_legal_terms(cleaned_text)
            }
            
        except Exception as e:
            logger.error(f"Error preprocessing question: {e}")
            return {
                'original_text': question_text,
                'cleaned_text': question_text,
                'question_type': QuestionType.UNKNOWN.value,
                'key_terms': [],
                'complexity': 'medium',
                'word_count': len(question_text.split()),
                'has_legal_terms': False
            }
    
    def _clean_question_text(self, text: str) -> str:
        """Clean and normalize question text."""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text.strip())
        
        # Remove special characters but keep punctuation
        text = re.sub(r'[^\w\s\?\.\,\;\:\!\-\'\"\(\)]', '', text)
        
        # Normalize case
        text = text.lower()
        
        return text
    
    def _classify_question(self, text: str) -> QuestionType:
        """Classify question type based on patterns."""
        for question_type, patterns in self.question_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    return question_type
        
        return QuestionType.UNKNOWN
    
    def _extract_key_terms(self, text: str) -> List[str]:
        """Extract key terms from question."""
        # Remove common stop words
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
            'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
            'should', 'may', 'might', 'can', 'this', 'that', 'these', 'those'
        }
        
        words = text.split()
        key_terms = [word for word in words if word.lower() not in stop_words and len(word) > 2]
        
        return key_terms[:10]  # Limit to top 10 terms
    
    def _assess_complexity(self, text: str) -> str:
        """Assess question complexity."""
        word_count = len(text.split())
        
        if word_count <= 5:
            return 'simple'
        elif word_count <= 15:
            return 'medium'
        else:
            return 'complex'
    
    def _has_legal_terms(self, text: str) -> bool:
        """Check if question contains legal terms."""
        legal_terms = {
            'contract', 'agreement', 'clause', 'section', 'article', 'party',
            'obligation', 'liability', 'damages', 'breach', 'termination',
            'amendment', 'waiver', 'indemnification', 'governing law',
            'jurisdiction', 'arbitration', 'mediation', 'force majeure',
            'confidentiality', 'non-compete', 'intellectual property'
        }
        
        text_words = set(text.lower().split())
        return bool(text_words.intersection(legal_terms))

class AnswerGenerator:
    """Advanced answer generation with grounding and citations."""
    
    def __init__(self):
        """Initialize answer generator."""
        self.not_found_responses = [
            "I could not find specific information about this in the document.",
            "This information is not explicitly mentioned in the document.",
            "The document does not contain details about this topic.",
            "I cannot provide a definitive answer based on the available information."
        ]
    
    def generate_grounded_answer(self, question: str, search_results: List[Dict[str, Any]], 
                               question_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate grounded answer with citations."""
        try:
            if not search_results:
                return self._generate_not_found_response(question_analysis)
            
            # Generate answer based on question type
            question_type = question_analysis.get('question_type', 'unknown')
            
            if question_type == QuestionType.YES_NO.value:
                answer = self._generate_yes_no_answer(question, search_results)
            elif question_type == QuestionType.COMPARISON.value:
                answer = self._generate_comparison_answer(question, search_results)
            elif question_type == QuestionType.PROCEDURAL.value:
                answer = self._generate_procedural_answer(question, search_results)
            elif question_type == QuestionType.INTERPRETATION.value:
                answer = self._generate_interpretation_answer(question, search_results)
            else:
                answer = self._generate_factual_answer(question, search_results)
            
            # Calculate confidence and create citations
            confidence_score = self._calculate_enhanced_confidence(search_results, question_analysis)
            citations = self._create_enhanced_citations(search_results)
            
            return {
                'answer': answer,
                'confidence_score': confidence_score,
                'citations': citations,
                'source_chunks': [result['chunk_id'] for result in search_results],
                'source_pages': list(set([result['page_number'] for result in search_results])),
                'answer_type': question_type,
                'grounded': True
            }
            
        except Exception as e:
            logger.error(f"Error generating grounded answer: {e}")
            return self._generate_error_response()
    
    def _generate_yes_no_answer(self, question: str, search_results: List[Dict[str, Any]]) -> str:
        """Generate yes/no answer."""
        # Look for positive/negative indicators
        positive_indicators = ['yes', 'true', 'correct', 'affirmative', 'agreed', 'approved']
        negative_indicators = ['no', 'false', 'incorrect', 'negative', 'disagreed', 'rejected']
        
        context = " ".join([result['chunk_text'] for result in search_results])
        context_lower = context.lower()
        
        # Count indicators
        positive_count = sum(1 for indicator in positive_indicators if indicator in context_lower)
        negative_count = sum(1 for indicator in negative_indicators if indicator in context_lower)
        
        if positive_count > negative_count:
            return f"Yes, based on the document: {context[:200]}..."
        elif negative_count > positive_count:
            return f"No, based on the document: {context[:200]}..."
        else:
            return f"The document states: {context[:200]}..."
    
    def _generate_comparison_answer(self, question: str, search_results: List[Dict[str, Any]]) -> str:
        """Generate comparison answer."""
        # Extract comparison elements
        context = " ".join([result['chunk_text'] for result in search_results])
        
        # Look for comparison words
        comparison_words = ['however', 'but', 'while', 'whereas', 'on the other hand', 'in contrast']
        
        for word in comparison_words:
            if word in context.lower():
                # Find the comparison section
                parts = context.split(word)
                if len(parts) >= 2:
                    return f"Comparison found: {parts[0][:100]}... {word} {parts[1][:100]}..."
        
        return f"The document provides the following information for comparison: {context[:300]}..."
    
    def _generate_procedural_answer(self, question: str, search_results: List[Dict[str, Any]]) -> str:
        """Generate procedural answer."""
        # Look for procedural indicators
        procedural_indicators = ['step', 'procedure', 'process', 'method', 'first', 'then', 'finally']
        
        context = " ".join([result['chunk_text'] for result in search_results])
        
        # Find procedural content
        for indicator in procedural_indicators:
            if indicator in context.lower():
                # Extract the procedural section
                start_idx = context.lower().find(indicator)
                if start_idx != -1:
                    return f"Procedure: {context[start_idx:start_idx+300]}..."
        
        return f"The document outlines the following process: {context[:300]}..."
    
    def _generate_interpretation_answer(self, question: str, search_results: List[Dict[str, Any]]) -> str:
        """Generate interpretation answer."""
        context = " ".join([result['chunk_text'] for result in search_results])
        
        # Look for explanatory content
        explanatory_indicators = ['means', 'refers to', 'defined as', 'indicates', 'implies']
        
        for indicator in explanatory_indicators:
            if indicator in context.lower():
                start_idx = context.lower().find(indicator)
                if start_idx != -1:
                    return f"Interpretation: {context[start_idx:start_idx+300]}..."
        
        return f"Based on the document context: {context[:300]}..."
    
    def _generate_factual_answer(self, question: str, search_results: List[Dict[str, Any]]) -> str:
        """Generate factual answer."""
        # Extract the most relevant information
        best_result = max(search_results, key=lambda x: x['similarity_score'])
        
        return f"According to the document: {best_result['chunk_text'][:300]}..."
    
    def _generate_not_found_response(self, question_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate response when information is not found."""
        import random
        response = random.choice(self.not_found_responses)
        
        return {
            'answer': response,
            'confidence_score': 0.0,
            'citations': [],
            'source_chunks': [],
            'source_pages': [],
            'answer_type': 'not_found',
            'grounded': False
        }
    
    def _generate_error_response(self) -> Dict[str, Any]:
        """Generate error response."""
        return {
            'answer': 'Sorry, I encountered an error while generating the answer. Please try again.',
            'confidence_score': 0.0,
            'citations': [],
            'source_chunks': [],
            'source_pages': [],
            'answer_type': 'error',
            'grounded': False
        }
    
    def _calculate_enhanced_confidence(self, search_results: List[Dict[str, Any]], 
                                     question_analysis: Dict[str, Any]) -> float:
        """Calculate enhanced confidence score using Week 11 confidence engine."""
        if not search_results:
            return 0.0
        
        try:
            # Create confidence factors
            factors = ConfidenceFactors(
                similarity_score=sum(result['similarity_score'] for result in search_results) / len(search_results),
                result_count=len(search_results),
                question_complexity=question_analysis.get('complexity', 'medium'),
                has_legal_terms=question_analysis.get('has_legal_terms', False),
                answer_length=len(" ".join([result['chunk_text'] for result in search_results])),
                citation_quality=sum(result['similarity_score'] for result in search_results) / len(search_results),
                source_diversity=len(set(result['page_number'] for result in search_results)) / len(search_results),
                semantic_coherence=0.8,  # Default value
                keyword_overlap=0.7  # Default value
            )
            
            # Use confidence analyzer
            confidence_analysis = confidence_analyzer.analyze_confidence_factors(factors)
            return confidence_analysis['overall_confidence']
            
        except Exception as e:
            logger.error(f"Error calculating enhanced confidence: {e}")
            # Fallback to simple calculation
            similarity_scores = [result['similarity_score'] for result in search_results]
            base_confidence = sum(similarity_scores) / len(similarity_scores) * 100
            return min(round(base_confidence, 2), 100.0)
    
    def _create_enhanced_citations(self, search_results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Create enhanced citations with better formatting."""
        citations = []
        
        for result in search_results:
            # Clean and format citation text
            citation_text = result['chunk_text'].strip()
            if len(citation_text) > 200:
                citation_text = citation_text[:200] + "..."
            
            citations.append({
                'text': citation_text,
                'page_number': result['page_number'],
                'similarity_score': result['similarity_score'],
                'confidence': min(result['similarity_score'] * 100, 100.0)
            })
        
        # Sort by relevance
        citations.sort(key=lambda x: x['similarity_score'], reverse=True)
        
        return citations

class QAService:
    """Enhanced Q&A service for Week 10."""
    
    def __init__(self):
        """Initialize the enhanced Q&A service."""
        self.search_engine = semantic_search_engine
        self.question_processor = QuestionProcessor()
        self.answer_generator = AnswerGenerator()
    
    @monitor_performance("enhanced_question_processing")
    def process_question(self, question_text: str, document_id: str) -> Dict[str, Any]:
        """Process a question with enhanced preprocessing and classification."""
        try:
            logger.info(f"Processing enhanced question: {question_text}")
            start_time = time.time()
            
            # Get document
            try:
                document = Document.objects.get(id=document_id)
            except Document.DoesNotExist:
                return {
                    'success': False,
                    'error': 'Document not found',
                    'answer': None,
                    'confidence_score': 0.0
                }
            
            # Check if document is processed
            if document.status != 'processed':
                return {
                    'success': False,
                    'error': 'Document is not yet processed',
                    'answer': None,
                    'confidence_score': 0.0
                }
            
            # Preprocess and classify question
            question_analysis = self.question_processor.preprocess_question(question_text)
            
            # Create question record
            question = Question.objects.create(
                document=document,
                question_text=question_text,
                question_type=question_analysis['question_type'],
                complexity_level=question_analysis['complexity']
            )
            
            # Generate enhanced answer
            answer_result = self._generate_enhanced_answer(question_text, document, question_analysis)
            
            # Calculate processing time
            processing_time = time.time() - start_time
            
            # Update question with answer
            question.answer = answer_result['answer']
            question.confidence_score = answer_result['confidence_score']
            question.processing_time = processing_time
            question.citations = answer_result['citations']
            question.save()
            
            # Create detailed answer record
            answer = Answer.objects.create(
                question=question,
                answer_text=answer_result['answer'],
                answer_type=answer_result.get('answer_type', 'generated'),
                confidence_score=answer_result['confidence_score'],
                relevance_score=answer_result.get('relevance_score', 0.0),
                source_chunks=answer_result['source_chunks'],
                source_pages=answer_result.get('source_pages', []),
                generation_time=processing_time,
                model_used='enhanced-sentence-transformers',
                grounded=answer_result.get('grounded', False)
            )
            
            # Create enhanced citations
            self._create_enhanced_citations(answer, answer_result['citations'])
            
            logger.info(f"Enhanced question processed successfully. Confidence: {answer_result['confidence_score']:.2f}")
            
            # Generate legal recommendations (Week 11 enhancement)
            recommendations = self._generate_recommendations(
                document, question_text, answer_result['answer']
            )
            
            return {
                'success': True,
                'question_id': str(question.id),
                'answer_id': str(answer.id),
                'answer': answer_result['answer'],
                'confidence_score': answer_result['confidence_score'],
                'citations': answer_result['citations'],
                'processing_time': processing_time,
                'question_analysis': question_analysis,
                'answer_type': answer_result.get('answer_type', 'generated'),
                'grounded': answer_result.get('grounded', False),
                'recommendations': recommendations
            }
            
        except Exception as e:
            logger.error(f"Error processing enhanced question: {e}")
            return {
                'success': False,
                'error': str(e),
                'answer': None,
                'confidence_score': 0.0
            }
    
    def _generate_enhanced_answer(self, question_text: str, document: Document, 
                                question_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate enhanced answer using advanced processing."""
        try:
            # Use semantic search engine to find relevant chunks
            search_results = self.search_engine.search_similar_chunks(question_text, document, top_k=5)
            
            # Generate grounded answer
            return self.answer_generator.generate_grounded_answer(
                question_text, search_results, question_analysis
            )
            
        except Exception as e:
            logger.error(f"Error generating enhanced answer: {e}")
            return self.answer_generator._generate_error_response()
    
    def _create_enhanced_citations(self, answer: Answer, citations_data: List[Dict[str, Any]]):
        """Create enhanced citation records."""
        try:
            for citation_data in citations_data:
                # Find the source chunk
                chunk_text = citation_data['text']
                chunks = DocumentChunk.objects.filter(
                    document=answer.question.document,
                    chunk_text__icontains=chunk_text[:100]
                )
                
                if chunks.exists():
                    source_chunk = chunks.first()
                    
                    Citation.objects.create(
                        answer=answer,
                        citation_text=citation_data['text'],
                        source_chunk=source_chunk,
                        page_number=citation_data.get('page_number', 0),
                        start_position=0,
                        end_position=len(citation_data['text']),
                        relevance_score=citation_data.get('similarity_score', 0.0),
                        confidence_score=citation_data.get('confidence', 0.0)
                    )
            
        except Exception as e:
            logger.error(f"Error creating enhanced citations: {e}")
    
    def _generate_recommendations(self, document: Document, question: str, answer: str) -> Dict[str, Any]:
        """Generate legal recommendations for the question and answer."""
        try:
            # Get document text for analysis
            document_text = document.extracted_text or ""
            
            # Get red flags and clauses if available
            red_flags = []
            clauses = []
            
            try:
                # Get red flags from document
                from .models import RedFlag
                red_flags_data = RedFlag.objects.filter(document=document)
                for rf in red_flags_data:
                    red_flags.append({
                        'title': rf.title,
                        'risk_level': rf.risk_level,
                        'confidence_score': rf.confidence_score
                    })
                
                # Get clauses from document
                from .models import Clause
                clauses_data = Clause.objects.filter(document=document)
                for clause in clauses_data:
                    clauses.append({
                        'clause_type': clause.clause_type,
                        'importance': clause.importance,
                        'confidence_score': clause.confidence_score
                    })
                    
            except Exception as e:
                logger.warning(f"Could not retrieve red flags or clauses: {e}")
            
            # Generate comprehensive recommendations
            recommendations = recommendation_manager.generate_comprehensive_recommendations(
                document_text=document_text,
                question=question,
                red_flags=red_flags,
                clauses=clauses
            )
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error generating recommendations: {e}")
            return {
                'recommendations': {},
                'total_count': 0,
                'critical_count': 0,
                'high_count': 0,
                'summary': 'Error generating recommendations'
            }
    
    def get_question_history(self, document_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get question history for a document."""
        try:
            questions = Question.objects.filter(
                document_id=document_id
            ).order_by('-created_at')[:limit]
            
            history = []
            for question in questions:
                history.append({
                    'id': str(question.id),
                    'question_text': question.question_text,
                    'answer': question.answer,
                    'confidence_score': question.confidence_score,
                    'processing_time': question.processing_time,
                    'created_at': question.created_at.isoformat(),
                    'citations_count': len(question.citations) if question.citations else 0,
                    'question_type': question.question_type,
                    'complexity_level': question.complexity_level
                })
            
            return history
            
        except Exception as e:
            logger.error(f"Error getting question history: {e}")
            return []
    
    def get_document_qa_summary(self, document_id: str) -> Dict[str, Any]:
        """Get Q&A summary for a document."""
        try:
            questions = Question.objects.filter(document_id=document_id)
            
            if not questions.exists():
                return {
                    'total_questions': 0,
                    'avg_confidence': 0.0,
                    'avg_processing_time': 0.0,
                    'recent_questions': []
                }
            
            # Calculate statistics
            total_questions = questions.count()
            avg_confidence = questions.aggregate(avg=models.Avg('confidence_score'))['avg'] or 0.0
            avg_processing_time = questions.aggregate(avg=models.Avg('processing_time'))['avg'] or 0.0
            
            # Get recent questions
            recent_questions = questions.order_by('-created_at')[:5]
            recent_data = []
            for q in recent_questions:
                recent_data.append({
                    'question': q.question_text[:100] + "..." if len(q.question_text) > 100 else q.question_text,
                    'confidence': q.confidence_score,
                    'created_at': q.created_at.strftime('%Y-%m-%d %H:%M')
                })
            
            return {
                'total_questions': total_questions,
                'avg_confidence': round(avg_confidence, 2),
                'avg_processing_time': round(avg_processing_time, 2),
                'recent_questions': recent_data
            }
            
        except Exception as e:
            logger.error(f"Error getting document Q&A summary: {e}")
            return {
                'total_questions': 0,
                'avg_confidence': 0.0,
                'avg_processing_time': 0.0,
                'recent_questions': []
            }

# Global Q&A service instance
qa_service = QAService()
