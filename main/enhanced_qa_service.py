"""
Enhanced Q&A Service for Document Question Answering
Integrates advanced semantic search and performance optimization
Week 12: Advanced Features Implementation
"""

import logging
import time
from typing import Dict, Any, List, Optional
from datetime import datetime

from django.db import transaction
from .models import Document, Question, Answer, Citation, DocumentChunk
from .advanced_semantic_search import advanced_semantic_search_engine
from .performance_optimizer import performance_optimizer, optimize_qa
from .performance_monitor import monitor_performance
from .confidence_engine import confidence_analyzer, ConfidenceFactors
from .recommendation_engine import recommendation_manager

logger = logging.getLogger(__name__)

class EnhancedQAService:
    """Enhanced Q&A service with advanced features and optimization."""
    
    def __init__(self):
        """Initialize the enhanced Q&A service."""
        self.search_engine = advanced_semantic_search_engine
        self.optimizer = performance_optimizer
        
        # Performance tracking
        self.qa_stats = {
            'total_questions': 0,
            'avg_processing_time': 0.0,
            'avg_confidence': 0.0,
            'cache_hits': 0,
            'cache_misses': 0,
            'successful_answers': 0,
            'failed_answers': 0
        }
    
    @monitor_performance("enhanced_question_processing")
    @optimize_qa()
    def process_enhanced_question(self, question_text: str, document_id: str) -> Dict[str, Any]:
        """Process a question with enhanced features and optimization."""
        try:
            start_time = time.time()
            logger.info(f"Processing enhanced question: {question_text[:50]}...")
            
            # Get document
            try:
                document = Document.objects.get(id=document_id)
            except Document.DoesNotExist:
                return self._create_error_response('Document not found')
            
            # Check document status
            if document.status != 'processed':
                return self._create_error_response('Document is not yet processed')
            
            # Optimize document processing if needed
            self.optimizer.optimize_document_processing(document)
            
            # Process question with advanced features
            result = self._process_question_with_advanced_features(question_text, document)
            
            # Update statistics
            processing_time = time.time() - start_time
            self._update_qa_statistics(result['success'], processing_time, result.get('confidence_score', 0.0))
            
            # Add performance metrics to result
            result['processing_time'] = processing_time
            result['performance_metrics'] = self._get_performance_metrics()
            
            logger.info(f"Enhanced question processed successfully. Time: {processing_time:.3f}s, Confidence: {result.get('confidence_score', 0.0):.2f}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error processing enhanced question: {e}")
            return self._create_error_response(str(e))
    
    def _process_question_with_advanced_features(self, question_text: str, document: Document) -> Dict[str, Any]:
        """Process question with all advanced features."""
        try:
            # Step 1: Advanced semantic search
            search_results = self._perform_advanced_search(question_text, document)
            
            if not search_results:
                return self._create_not_found_response(question_text)
            
            # Step 2: Enhanced answer generation
            answer_result = self._generate_enhanced_answer(question_text, search_results, document)
            
            # Step 3: Advanced confidence analysis
            confidence_analysis = self._perform_advanced_confidence_analysis(
                question_text, search_results, answer_result
            )
            
            # Step 4: Generate comprehensive recommendations
            recommendations = self._generate_comprehensive_recommendations(
                document, question_text, answer_result['answer'], search_results
            )
            
            # Step 5: Create database records
            question_record, answer_record = self._create_database_records(
                question_text, document, answer_result, confidence_analysis
            )
            
            # Step 6: Create enhanced citations
            citations = self._create_enhanced_citations(answer_record, search_results)
            
            return {
                'success': True,
                'question_id': str(question_record.id),
                'answer_id': str(answer_record.id),
                'answer': answer_result['answer'],
                'confidence_score': confidence_analysis['overall_confidence'],
                'confidence_breakdown': confidence_analysis['factor_contributions'],
                'citations': citations,
                'search_results': self._format_search_results(search_results),
                'recommendations': recommendations,
                'answer_type': answer_result.get('answer_type', 'generated'),
                'grounded': answer_result.get('grounded', True),
                'search_metadata': {
                    'total_results': len(search_results),
                    'avg_similarity': sum(r['similarity_score'] for r in search_results) / len(search_results),
                    'search_method': search_results[0].get('search_method', 'unknown') if search_results else 'unknown'
                }
            }
            
        except Exception as e:
            logger.error(f"Error in advanced question processing: {e}")
            return self._create_error_response(str(e))
    
    def _perform_advanced_search(self, question_text: str, document: Document) -> List[Dict[str, Any]]:
        """Perform advanced semantic search with optimization."""
        try:
            # Use optimized search query
            search_results = self.optimizer.optimize_search_query(
                question_text, document, top_k=8
            )
            
            # Apply additional filtering and ranking
            filtered_results = self._filter_and_rank_results(search_results, question_text)
            
            return filtered_results[:5]  # Return top 5 results
            
        except Exception as e:
            logger.error(f"Error performing advanced search: {e}")
            return []
    
    def _filter_and_rank_results(self, search_results: List[Dict[str, Any]], question_text: str) -> List[Dict[str, Any]]:
        """Filter and rank search results based on quality metrics."""
        try:
            filtered_results = []
            
            for result in search_results:
                # Calculate quality score
                quality_score = self._calculate_result_quality(result, question_text)
                
                # Apply quality threshold
                if quality_score > 0.3:  # Minimum quality threshold
                    result['quality_score'] = quality_score
                    filtered_results.append(result)
            
            # Sort by quality score
            filtered_results.sort(key=lambda x: x['quality_score'], reverse=True)
            
            return filtered_results
            
        except Exception as e:
            logger.error(f"Error filtering and ranking results: {e}")
            return search_results
    
    def _calculate_result_quality(self, result: Dict[str, Any], question_text: str) -> float:
        """Calculate quality score for a search result."""
        try:
            # Base similarity score
            similarity_score = result.get('similarity_score', 0.0)
            
            # Text quality factors
            text_length = len(result.get('chunk_text', ''))
            text_quality = min(text_length / 500, 1.0)  # Normalize by expected length
            
            # Relevance indicators
            relevance_indicators = result.get('relevance_indicators', {})
            word_overlap_ratio = relevance_indicators.get('overlap_ratio', 0.0)
            semantic_similarity = relevance_indicators.get('semantic_similarity', 0.0)
            
            # Semantic coherence
            semantic_coherence = result.get('semantic_coherence', 0.5)
            
            # Calculate weighted quality score
            weights = [0.4, 0.2, 0.15, 0.15, 0.1]
            factors = [similarity_score, text_quality, word_overlap_ratio, semantic_similarity, semantic_coherence]
            
            quality_score = sum(factor * weight for factor, weight in zip(factors, weights))
            
            return min(quality_score, 1.0)
            
        except Exception as e:
            logger.error(f"Error calculating result quality: {e}")
            return 0.0
    
    def _generate_enhanced_answer(self, question_text: str, search_results: List[Dict[str, Any]], 
                                document: Document) -> Dict[str, Any]:
        """Generate enhanced answer with advanced processing."""
        try:
            if not search_results:
                return {
                    'answer': 'I could not find relevant information to answer your question.',
                    'answer_type': 'not_found',
                    'grounded': False
                }
            
            # Extract context from search results
            context_text = " ".join([result['chunk_text'] for result in search_results[:3]])
            
            # Generate answer based on search results
            answer = self._synthesize_answer_from_context(question_text, context_text, search_results)
            
            return {
                'answer': answer,
                'answer_type': 'generated',
                'grounded': True,
                'context_used': len(search_results)
            }
            
        except Exception as e:
            logger.error(f"Error generating enhanced answer: {e}")
            return {
                'answer': 'Sorry, I encountered an error while generating the answer.',
                'answer_type': 'error',
                'grounded': False
            }
    
    def _synthesize_answer_from_context(self, question_text: str, context_text: str, 
                                      search_results: List[Dict[str, Any]]) -> str:
        """Synthesize answer from context and search results."""
        try:
            # Simple answer synthesis (in production, you'd use a more sophisticated approach)
            best_result = max(search_results, key=lambda x: x.get('quality_score', 0.0))
            
            # Extract the most relevant sentence or paragraph
            chunk_text = best_result['chunk_text']
            
            # If the chunk is too long, extract the most relevant part
            if len(chunk_text) > 300:
                # Find the sentence that best matches the question
                sentences = chunk_text.split('. ')
                best_sentence = max(sentences, key=lambda s: self._calculate_sentence_relevance(s, question_text))
                answer = best_sentence + "."
            else:
                answer = chunk_text
            
            # Add context if available
            if len(search_results) > 1:
                answer += f" This information is supported by {len(search_results)} relevant sections in the document."
            
            return answer
            
        except Exception as e:
            logger.error(f"Error synthesizing answer: {e}")
            return context_text[:300] + "..." if len(context_text) > 300 else context_text
    
    def _calculate_sentence_relevance(self, sentence: str, question_text: str) -> float:
        """Calculate relevance between a sentence and question."""
        try:
            # Simple word overlap calculation
            question_words = set(question_text.lower().split())
            sentence_words = set(sentence.lower().split())
            
            overlap = len(question_words.intersection(sentence_words))
            return overlap / len(question_words) if question_words else 0.0
            
        except Exception as e:
            logger.error(f"Error calculating sentence relevance: {e}")
            return 0.0
    
    def _perform_advanced_confidence_analysis(self, question_text: str, search_results: List[Dict[str, Any]], 
                                            answer_result: Dict[str, Any]) -> Dict[str, Any]:
        """Perform advanced confidence analysis."""
        try:
            # Calculate confidence factors
            factors = ConfidenceFactors(
                similarity_score=sum(r['similarity_score'] for r in search_results) / len(search_results) if search_results else 0.0,
                result_count=len(search_results),
                question_complexity=self._assess_question_complexity(question_text),
                has_legal_terms=self._has_legal_terms(question_text),
                answer_length=len(answer_result.get('answer', '')),
                citation_quality=sum(r.get('quality_score', 0.0) for r in search_results) / len(search_results) if search_results else 0.0,
                source_diversity=len(set(r.get('page_number', 0) for r in search_results)) / len(search_results) if search_results else 0.0,
                semantic_coherence=sum(r.get('semantic_coherence', 0.5) for r in search_results) / len(search_results) if search_results else 0.5,
                keyword_overlap=self._calculate_keyword_overlap(question_text, search_results)
            )
            
            # Use confidence analyzer
            confidence_analysis = confidence_analyzer.analyze_confidence_factors(factors)
            
            return confidence_analysis
            
        except Exception as e:
            logger.error(f"Error performing confidence analysis: {e}")
            return {
                'overall_confidence': 0.5,
                'factor_contributions': {},
                'strengths': [],
                'weaknesses': ['Error in confidence analysis']
            }
    
    def _assess_question_complexity(self, question_text: str) -> str:
        """Assess question complexity."""
        word_count = len(question_text.split())
        if word_count <= 5:
            return 'simple'
        elif word_count <= 15:
            return 'medium'
        else:
            return 'complex'
    
    def _has_legal_terms(self, text: str) -> bool:
        """Check if text contains legal terms."""
        legal_terms = {
            'contract', 'agreement', 'clause', 'section', 'article', 'party',
            'obligation', 'liability', 'damages', 'breach', 'termination',
            'amendment', 'waiver', 'indemnification', 'governing law',
            'jurisdiction', 'arbitration', 'mediation', 'force majeure'
        }
        
        text_words = set(text.lower().split())
        return bool(text_words.intersection(legal_terms))
    
    def _calculate_keyword_overlap(self, question_text: str, search_results: List[Dict[str, Any]]) -> float:
        """Calculate keyword overlap between question and search results."""
        try:
            question_words = set(question_text.lower().split())
            all_result_words = set()
            
            for result in search_results:
                result_words = set(result.get('chunk_text', '').lower().split())
                all_result_words.update(result_words)
            
            overlap = len(question_words.intersection(all_result_words))
            return overlap / len(question_words) if question_words else 0.0
            
        except Exception as e:
            logger.error(f"Error calculating keyword overlap: {e}")
            return 0.0
    
    def _generate_comprehensive_recommendations(self, document: Document, question: str, 
                                              answer: str, search_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate comprehensive recommendations."""
        try:
            # Get document analysis data
            analysis = document.analysis_set.first()
            
            # Generate recommendations using recommendation engine
            recommendations = recommendation_manager.generate_comprehensive_recommendations(
                document_text=document.extracted_text or "",
                question=question,
                answer=answer,
                search_results=search_results,
                document_analysis=analysis
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
    
    @transaction.atomic
    def _create_database_records(self, question_text: str, document: Document, 
                               answer_result: Dict[str, Any], confidence_analysis: Dict[str, Any]) -> tuple:
        """Create database records for question and answer."""
        try:
            # Create question record
            question = Question.objects.create(
                document=document,
                question_text=question_text,
                question_type='enhanced',
                complexity_level=self._assess_question_complexity(question_text),
                processing_time=0.0  # Will be updated later
            )
            
            # Create answer record
            answer = Answer.objects.create(
                question=question,
                answer_text=answer_result['answer'],
                answer_type=answer_result.get('answer_type', 'generated'),
                confidence_score=confidence_analysis['overall_confidence'],
                relevance_score=confidence_analysis.get('factor_contributions', {}).get('similarity_score', 0.0),
                source_chunks=[],  # Will be populated with citations
                source_pages=[],
                generation_time=0.0,  # Will be updated later
                model_used='enhanced-semantic-search',
                grounded=answer_result.get('grounded', True)
            )
            
            return question, answer
            
        except Exception as e:
            logger.error(f"Error creating database records: {e}")
            raise
    
    def _create_enhanced_citations(self, answer: Answer, search_results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Create enhanced citations from search results."""
        try:
            citations = []
            
            for result in search_results:
                # Create citation record
                citation = Citation.objects.create(
                    answer=answer,
                    citation_text=result['chunk_text'][:500] + "..." if len(result['chunk_text']) > 500 else result['chunk_text'],
                    source_chunk_id=result['chunk_id'],
                    page_number=result.get('page_number', 0),
                    start_position=0,
                    end_position=len(result['chunk_text']),
                    relevance_score=result.get('similarity_score', 0.0),
                    confidence_score=result.get('quality_score', 0.0)
                )
                
                # Add to citations list
                citations.append({
                    'id': str(citation.id),
                    'text': citation.citation_text,
                    'page_number': citation.page_number,
                    'relevance_score': citation.relevance_score,
                    'confidence_score': citation.confidence_score
                })
            
            return citations
            
        except Exception as e:
            logger.error(f"Error creating enhanced citations: {e}")
            return []
    
    def _format_search_results(self, search_results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Format search results for response."""
        try:
            formatted_results = []
            
            for result in search_results:
                formatted_results.append({
                    'chunk_text': result['chunk_text'][:200] + "..." if len(result['chunk_text']) > 200 else result['chunk_text'],
                    'page_number': result.get('page_number', 0),
                    'similarity_score': result.get('similarity_score', 0.0),
                    'quality_score': result.get('quality_score', 0.0),
                    'search_method': result.get('search_method', 'unknown'),
                    'relevance_indicators': result.get('relevance_indicators', {})
                })
            
            return formatted_results
            
        except Exception as e:
            logger.error(f"Error formatting search results: {e}")
            return []
    
    def _create_error_response(self, error_message: str) -> Dict[str, Any]:
        """Create error response."""
        return {
            'success': False,
            'error': error_message,
            'answer': None,
            'confidence_score': 0.0,
            'processing_time': 0.0
        }
    
    def _create_not_found_response(self, question_text: str) -> Dict[str, Any]:
        """Create not found response."""
        return {
            'success': True,
            'answer': 'I could not find specific information to answer your question in the document.',
            'confidence_score': 0.0,
            'citations': [],
            'search_results': [],
            'recommendations': {
                'recommendations': {},
                'total_count': 0,
                'summary': 'No relevant information found'
            },
            'answer_type': 'not_found',
            'grounded': False
        }
    
    def _update_qa_statistics(self, success: bool, processing_time: float, confidence_score: float):
        """Update Q&A statistics."""
        try:
            self.qa_stats['total_questions'] += 1
            
            # Update average processing time
            current_avg = self.qa_stats['avg_processing_time']
            total_questions = self.qa_stats['total_questions']
            self.qa_stats['avg_processing_time'] = (
                (current_avg * (total_questions - 1) + processing_time) / total_questions
            )
            
            # Update average confidence
            current_avg_conf = self.qa_stats['avg_confidence']
            self.qa_stats['avg_confidence'] = (
                (current_avg_conf * (total_questions - 1) + confidence_score) / total_questions
            )
            
            # Update success/failure counts
            if success:
                self.qa_stats['successful_answers'] += 1
            else:
                self.qa_stats['failed_answers'] += 1
                
        except Exception as e:
            logger.error(f"Error updating Q&A statistics: {e}")
    
    def _get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics."""
        try:
            return {
                'qa_statistics': self.qa_stats,
                'search_statistics': self.search_engine.get_search_statistics(),
                'optimization_metrics': self.optimizer.get_performance_metrics()
            }
        except Exception as e:
            logger.error(f"Error getting performance metrics: {e}")
            return {}
    
    def get_enhanced_question_history(self, document_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get enhanced question history for a document."""
        try:
            questions = Question.objects.filter(
                document_id=document_id
            ).order_by('-created_at')[:limit]
            
            history = []
            for question in questions:
                answer = question.answer_set.first()
                
                history.append({
                    'id': str(question.id),
                    'question_text': question.question_text,
                    'answer': answer.answer_text if answer else None,
                    'confidence_score': answer.confidence_score if answer else 0.0,
                    'processing_time': question.processing_time,
                    'created_at': question.created_at.isoformat(),
                    'question_type': question.question_type,
                    'complexity_level': question.complexity_level,
                    'citations_count': answer.citation_set.count() if answer else 0
                })
            
            return history
            
        except Exception as e:
            logger.error(f"Error getting enhanced question history: {e}")
            return []
    
    def get_enhanced_qa_summary(self, document_id: str) -> Dict[str, Any]:
        """Get enhanced Q&A summary for a document."""
        try:
            questions = Question.objects.filter(document_id=document_id)
            
            if not questions.exists():
                return {
                    'total_questions': 0,
                    'avg_confidence': 0.0,
                    'avg_processing_time': 0.0,
                    'success_rate': 0.0,
                    'recent_questions': [],
                    'performance_metrics': self._get_performance_metrics()
                }
            
            # Calculate statistics
            total_questions = questions.count()
            successful_questions = questions.filter(answer__isnull=False).count()
            success_rate = successful_questions / total_questions if total_questions > 0 else 0.0
            
            # Get average confidence and processing time
            avg_confidence = questions.aggregate(
                avg=models.Avg('answer__confidence_score')
            )['avg'] or 0.0
            
            avg_processing_time = questions.aggregate(
                avg=models.Avg('processing_time')
            )['avg'] or 0.0
            
            # Get recent questions
            recent_questions = questions.order_by('-created_at')[:5]
            recent_data = []
            for q in recent_questions:
                answer = q.answer_set.first()
                recent_data.append({
                    'question': q.question_text[:100] + "..." if len(q.question_text) > 100 else q.question_text,
                    'confidence': answer.confidence_score if answer else 0.0,
                    'created_at': q.created_at.strftime('%Y-%m-%d %H:%M'),
                    'type': q.question_type
                })
            
            return {
                'total_questions': total_questions,
                'successful_questions': successful_questions,
                'success_rate': round(success_rate * 100, 2),
                'avg_confidence': round(avg_confidence, 2),
                'avg_processing_time': round(avg_processing_time, 3),
                'recent_questions': recent_data,
                'performance_metrics': self._get_performance_metrics()
            }
            
        except Exception as e:
            logger.error(f"Error getting enhanced Q&A summary: {e}")
            return {
                'total_questions': 0,
                'avg_confidence': 0.0,
                'avg_processing_time': 0.0,
                'success_rate': 0.0,
                'recent_questions': [],
                'performance_metrics': {}
            }

# Global enhanced Q&A service instance
enhanced_qa_service = EnhancedQAService()
