"""
Advanced Semantic Search Engine for Document Q&A
Enhanced with advanced algorithms, better ranking, and improved performance
Week 12: Advanced Features Implementation
"""

import numpy as np
import logging
import time
from typing import List, Dict, Any, Optional, Tuple
from sentence_transformers import SentenceTransformer, CrossEncoder
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
import faiss
import json
import pickle
from pathlib import Path
from collections import defaultdict
import re

from django.conf import settings
from django.core.cache import cache
from .models import Document, DocumentChunk, Question, Answer, Citation
from .performance_monitor import monitor_performance

logger = logging.getLogger(__name__)

class AdvancedSemanticSearchEngine:
    """Advanced semantic search engine with multiple algorithms and ranking methods."""
    
    def __init__(self, 
                 bi_encoder_model: str = 'all-MiniLM-L6-v2',
                 cross_encoder_model: str = 'cross-encoder/ms-marco-MiniLM-L-6-v2',
                 use_cache: bool = True):
        """Initialize the advanced semantic search engine."""
        self.bi_encoder_model = bi_encoder_model
        self.cross_encoder_model = cross_encoder_model
        self.use_cache = use_cache
        
        # Models
        self.bi_encoder = None
        self.cross_encoder = None
        self.tfidf_vectorizer = None
        
        # Indexes
        self.faiss_index = None
        self.chunk_mapping = {}
        self.document_indexes = {}
        
        # Performance tracking
        self.search_stats = defaultdict(int)
        self.cache_hits = 0
        self.cache_misses = 0
        
        # Initialize models
        self._initialize_models()
    
    def _initialize_models(self):
        """Initialize all search models."""
        try:
            logger.info("Initializing advanced semantic search models...")
            
            # Initialize bi-encoder for initial retrieval
            logger.info(f"Loading bi-encoder model: {self.bi_encoder_model}")
            self.bi_encoder = SentenceTransformer(self.bi_encoder_model)
            
            # Initialize cross-encoder for re-ranking
            logger.info(f"Loading cross-encoder model: {self.cross_encoder_model}")
            self.cross_encoder = CrossEncoder(self.cross_encoder_model)
            
            # Initialize TF-IDF for keyword matching
            self.tfidf_vectorizer = TfidfVectorizer(
                max_features=10000,
                ngram_range=(1, 2),
                stop_words='english',
                min_df=1  # Changed from 2 to 1 to handle single documents
            )
            
            logger.info("Advanced semantic search models initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing advanced search models: {e}")
            raise
    
    @monitor_performance("advanced_embedding_generation")
    def create_advanced_embeddings(self, texts: List[str], 
                                 include_tfidf: bool = True) -> Dict[str, Any]:
        """Create advanced embeddings with multiple representations."""
        try:
            start_time = time.time()
            
            # Generate bi-encoder embeddings
            bi_embeddings = self.bi_encoder.encode(
                texts, 
                show_progress_bar=True, 
                convert_to_numpy=True,
                batch_size=32
            )
            
            embeddings_data = {
                'bi_encoder': bi_embeddings,
                'tfidf': None,
                'metadata': {
                    'text_count': len(texts),
                    'bi_encoder_dim': bi_embeddings.shape[1],
                    'generation_time': time.time() - start_time
                }
            }
            
            # Generate TF-IDF embeddings if requested
            if include_tfidf:
                tfidf_matrix = self.tfidf_vectorizer.fit_transform(texts)
                embeddings_data['tfidf'] = tfidf_matrix.toarray()
                embeddings_data['metadata']['tfidf_dim'] = tfidf_matrix.shape[1]
            
            logger.info(f"Generated advanced embeddings for {len(texts)} texts in {time.time() - start_time:.3f}s")
            return embeddings_data
            
        except Exception as e:
            logger.error(f"Error creating advanced embeddings: {e}")
            raise
    
    def build_advanced_index(self, document: Document) -> bool:
        """Build advanced search index with multiple algorithms."""
        try:
            logger.info(f"Building advanced search index for document: {document.title}")
            
            # Check cache first
            cache_key = f"advanced_index_{str(document.id)}"
            if self.use_cache and cache.get(cache_key):
                logger.info(f"Using cached advanced index for document: {document.title}")
                cached_data = cache.get(cache_key)
                self.document_indexes[str(document.id)] = cached_data
                return True
            
            # Get document chunks
            chunks = DocumentChunk.objects.filter(document=document)
            if not chunks.exists():
                logger.warning(f"No chunks found for document: {document.title}")
                return False
            
            # Extract texts and metadata
            texts = []
            chunk_metadata = []
            
            for chunk in chunks:
                texts.append(chunk.chunk_text)
                chunk_metadata.append({
                    'id': str(chunk.id),
                    'page_number': chunk.page_number,
                    'chunk_index': chunk.chunk_index,
                    'word_count': len(chunk.chunk_text.split())
                })
            
            # Create advanced embeddings
            embeddings_data = self.create_advanced_embeddings(texts, include_tfidf=True)
            
            # Build FAISS index for bi-encoder embeddings
            bi_embeddings = embeddings_data['bi_encoder']
            dimension = bi_embeddings.shape[1]
            
            # Use IndexFlatIP for inner product (cosine similarity)
            faiss_index = faiss.IndexFlatIP(dimension)
            faiss_index.add(bi_embeddings.astype(np.float32))
            
            # Create index data structure
            index_data = {
                'faiss_index': faiss_index,
                'chunk_metadata': chunk_metadata,
                'tfidf_matrix': embeddings_data['tfidf'],
                'tfidf_vectorizer': self.tfidf_vectorizer,
                'document_id': str(document.id),
                'chunk_count': len(chunks),
                'created_at': time.time()
            }
            
            # Store in memory and cache
            self.document_indexes[str(document.id)] = index_data
            
            if self.use_cache:
                # Cache the index data (without FAISS index as it's not serializable)
                cache_data = {
                    'chunk_metadata': chunk_metadata,
                    'tfidf_matrix': embeddings_data['tfidf'],
                    'document_id': document.id,
                    'chunk_count': len(chunks),
                    'created_at': time.time()
                }
                cache.set(cache_key, cache_data, timeout=3600)  # Cache for 1 hour
            
            logger.info(f"Built advanced search index with {len(chunks)} chunks for document: {document.title}")
            return True
            
        except Exception as e:
            logger.error(f"Error building advanced search index: {e}")
            return False
    
    @monitor_performance("advanced_semantic_search")
    def advanced_search(self, query: str, document: Document, 
                       top_k: int = 10, 
                       use_reranking: bool = True,
                       use_hybrid: bool = True) -> List[Dict[str, Any]]:
        """Perform advanced semantic search with multiple algorithms."""
        try:
            start_time = time.time()
            
            # Check cache for query results
            cache_key = f"search_results_{str(document.id)}_{hash(query)}_{top_k}"
            if self.use_cache:
                cached_results = cache.get(cache_key)
                if cached_results:
                    self.cache_hits += 1
                    logger.info(f"Cache hit for query: {query[:50]}...")
                    return cached_results
                self.cache_misses += 1
            
            # Build index if not exists
            if str(document.id) not in self.document_indexes:
                if not self.build_advanced_index(document):
                    return []
            
            index_data = self.document_indexes[str(document.id)]
            
            # Step 1: Initial retrieval with bi-encoder
            initial_results = self._bi_encoder_search(query, index_data, top_k * 2)
            
            if not initial_results:
                return []
            
            # Step 2: Hybrid search with TF-IDF if enabled
            if use_hybrid and index_data['tfidf_matrix'] is not None:
                hybrid_results = self._hybrid_search(query, initial_results, index_data, top_k * 2)
                initial_results = hybrid_results
            
            # Step 3: Re-ranking with cross-encoder if enabled
            if use_reranking and len(initial_results) > 1:
                final_results = self._cross_encoder_rerank(query, initial_results, top_k)
            else:
                final_results = initial_results[:top_k]
            
            # Step 4: Post-process and enhance results
            enhanced_results = self._enhance_search_results(final_results, query, document)
            
            # Cache results
            if self.use_cache:
                cache.set(cache_key, enhanced_results, timeout=1800)  # Cache for 30 minutes
            
            # Update search statistics
            self.search_stats['total_searches'] += 1
            self.search_stats['avg_search_time'] = (
                (self.search_stats['avg_search_time'] * (self.search_stats['total_searches'] - 1) + 
                 (time.time() - start_time)) / self.search_stats['total_searches']
            )
            
            logger.info(f"Advanced search completed in {time.time() - start_time:.3f}s, found {len(enhanced_results)} results")
            return enhanced_results
            
        except Exception as e:
            logger.error(f"Error in advanced search: {e}")
            return []
    
    def _bi_encoder_search(self, query: str, index_data: Dict[str, Any], top_k: int) -> List[Dict[str, Any]]:
        """Perform bi-encoder search."""
        try:
            # Create query embedding
            query_embedding = self.bi_encoder.encode([query], convert_to_numpy=True)
            
            # Search in FAISS index
            scores, indices = index_data['faiss_index'].search(
                query_embedding.astype(np.float32), 
                min(top_k, index_data['faiss_index'].ntotal)
            )
            
            # Create results
            results = []
            for score, idx in zip(scores[0], indices[0]):
                if idx < len(index_data['chunk_metadata']):
                    metadata = index_data['chunk_metadata'][idx]
                    results.append({
                        'chunk_id': metadata['id'],
                        'chunk_text': self._get_chunk_text(metadata['id']),
                        'page_number': metadata['page_number'],
                        'similarity_score': float(score),
                        'chunk_index': metadata['chunk_index'],
                        'search_method': 'bi_encoder',
                        'word_count': metadata['word_count']
                    })
            
            return results
            
        except Exception as e:
            logger.error(f"Error in bi-encoder search: {e}")
            return []
    
    def _hybrid_search(self, query: str, initial_results: List[Dict[str, Any]], 
                      index_data: Dict[str, Any], top_k: int) -> List[Dict[str, Any]]:
        """Perform hybrid search combining bi-encoder and TF-IDF."""
        try:
            # Get TF-IDF scores for query
            query_tfidf = self.tfidf_vectorizer.transform([query]).toarray()[0]
            
            # Calculate TF-IDF similarity for initial results
            for result in initial_results:
                chunk_idx = int(result['chunk_index'])
                if chunk_idx < len(index_data['tfidf_matrix']):
                    chunk_tfidf = index_data['tfidf_matrix'][chunk_idx]
                    tfidf_similarity = np.dot(query_tfidf, chunk_tfidf) / (
                        np.linalg.norm(query_tfidf) * np.linalg.norm(chunk_tfidf) + 1e-8
                    )
                    
                    # Combine scores (weighted average)
                    bi_encoder_score = result['similarity_score']
                    combined_score = 0.7 * bi_encoder_score + 0.3 * tfidf_similarity
                    result['similarity_score'] = combined_score
                    result['search_method'] = 'hybrid'
                    result['tfidf_score'] = tfidf_similarity
                    result['bi_encoder_score'] = bi_encoder_score
            
            # Re-sort by combined score
            initial_results.sort(key=lambda x: x['similarity_score'], reverse=True)
            return initial_results[:top_k]
            
        except Exception as e:
            logger.error(f"Error in hybrid search: {e}")
            return initial_results
    
    def _cross_encoder_rerank(self, query: str, initial_results: List[Dict[str, Any]], 
                             top_k: int) -> List[Dict[str, Any]]:
        """Re-rank results using cross-encoder."""
        try:
            # Prepare query-document pairs for cross-encoder
            pairs = []
            for result in initial_results:
                pairs.append([query, result['chunk_text']])
            
            # Get cross-encoder scores
            cross_scores = self.cross_encoder.predict(pairs)
            
            # Update results with cross-encoder scores
            for i, result in enumerate(initial_results):
                result['cross_encoder_score'] = float(cross_scores[i])
                result['search_method'] = 'cross_encoder_reranked'
                
                # Combine scores (cross-encoder gets higher weight)
                original_score = result['similarity_score']
                cross_score = float(cross_scores[i])
                final_score = 0.3 * original_score + 0.7 * cross_score
                result['similarity_score'] = final_score
            
            # Re-sort by final score
            initial_results.sort(key=lambda x: x['similarity_score'], reverse=True)
            return initial_results[:top_k]
            
        except Exception as e:
            logger.error(f"Error in cross-encoder re-ranking: {e}")
            return initial_results
    
    def _enhance_search_results(self, results: List[Dict[str, Any]], 
                               query: str, document: Document) -> List[Dict[str, Any]]:
        """Enhance search results with additional metadata and analysis."""
        try:
            enhanced_results = []
            
            for result in results:
                # Get full chunk text
                chunk_text = result['chunk_text']
                
                # Calculate additional metrics
                enhanced_result = {
                    **result,
                    'relevance_indicators': self._calculate_relevance_indicators(query, chunk_text),
                    'key_phrases': self._extract_key_phrases(chunk_text),
                    'semantic_coherence': self._calculate_semantic_coherence(chunk_text),
                    'context_window': self._get_context_window(result['chunk_id'], document),
                    'confidence_factors': self._calculate_confidence_factors(result, query, chunk_text)
                }
                
                enhanced_results.append(enhanced_result)
            
            return enhanced_results
            
        except Exception as e:
            logger.error(f"Error enhancing search results: {e}")
            return results
    
    def _calculate_relevance_indicators(self, query: str, text: str) -> Dict[str, Any]:
        """Calculate various relevance indicators."""
        try:
            query_words = set(query.lower().split())
            text_words = set(text.lower().split())
            
            # Word overlap
            overlap = len(query_words.intersection(text_words))
            overlap_ratio = overlap / len(query_words) if query_words else 0
            
            # Exact phrase matching
            exact_matches = text.lower().count(query.lower())
            
            # Semantic similarity (using bi-encoder)
            query_emb = self.bi_encoder.encode([query], convert_to_numpy=True)
            text_emb = self.bi_encoder.encode([text], convert_to_numpy=True)
            semantic_similarity = np.dot(query_emb[0], text_emb[0]) / (
                np.linalg.norm(query_emb[0]) * np.linalg.norm(text_emb[0]) + 1e-8
            )
            
            return {
                'word_overlap': overlap,
                'overlap_ratio': overlap_ratio,
                'exact_matches': exact_matches,
                'semantic_similarity': float(semantic_similarity),
                'query_length': len(query_words),
                'text_length': len(text_words)
            }
            
        except Exception as e:
            logger.error(f"Error calculating relevance indicators: {e}")
            return {}
    
    def _extract_key_phrases(self, text: str) -> List[str]:
        """Extract key phrases from text."""
        try:
            # Simple key phrase extraction using TF-IDF
            if not hasattr(self, '_phrase_vectorizer'):
                self._phrase_vectorizer = TfidfVectorizer(
                    max_features=100,
                    ngram_range=(1, 3),
                    stop_words='english',
                    min_df=1
                )
            
            # Extract phrases
            phrases = []
            words = text.split()
            
            # Extract bigrams and trigrams
            for i in range(len(words) - 1):
                bigram = f"{words[i]} {words[i+1]}"
                phrases.append(bigram)
                
                if i < len(words) - 2:
                    trigram = f"{words[i]} {words[i+1]} {words[i+2]}"
                    phrases.append(trigram)
            
            # Return top phrases (simple approach)
            return phrases[:10]
            
        except Exception as e:
            logger.error(f"Error extracting key phrases: {e}")
            return []
    
    def _calculate_semantic_coherence(self, text: str) -> float:
        """Calculate semantic coherence of text."""
        try:
            # Simple coherence calculation based on sentence similarity
            sentences = text.split('. ')
            if len(sentences) < 2:
                return 1.0
            
            # Calculate average similarity between consecutive sentences
            similarities = []
            for i in range(len(sentences) - 1):
                sent1_emb = self.bi_encoder.encode([sentences[i]], convert_to_numpy=True)
                sent2_emb = self.bi_encoder.encode([sentences[i+1]], convert_to_numpy=True)
                
                similarity = np.dot(sent1_emb[0], sent2_emb[0]) / (
                    np.linalg.norm(sent1_emb[0]) * np.linalg.norm(sent2_emb[0]) + 1e-8
                )
                similarities.append(float(similarity))
            
            return np.mean(similarities) if similarities else 0.0
            
        except Exception as e:
            logger.error(f"Error calculating semantic coherence: {e}")
            return 0.0
    
    def _get_context_window(self, chunk_id: str, document: Document) -> Dict[str, Any]:
        """Get context window around the chunk."""
        try:
            chunk = DocumentChunk.objects.get(id=chunk_id)
            
            # Get surrounding chunks
            surrounding_chunks = DocumentChunk.objects.filter(
                document=document,
                chunk_index__in=[chunk.chunk_index - 1, chunk.chunk_index + 1]
            ).order_by('chunk_index')
            
            context = {
                'current_chunk': chunk.chunk_text[:200] + "..." if len(chunk.chunk_text) > 200 else chunk.chunk_text,
                'previous_chunk': None,
                'next_chunk': None,
                'context_size': 0
            }
            
            for surrounding in surrounding_chunks:
                if surrounding.chunk_index == chunk.chunk_index - 1:
                    context['previous_chunk'] = surrounding.chunk_text[-100:] + "..." if len(surrounding.chunk_text) > 100 else surrounding.chunk_text
                elif surrounding.chunk_index == chunk.chunk_index + 1:
                    context['next_chunk'] = surrounding.chunk_text[:100] + "..." if len(surrounding.chunk_text) > 100 else surrounding.chunk_text
            
            context['context_size'] = len(context['previous_chunk'] or "") + len(context['next_chunk'] or "")
            
            return context
            
        except Exception as e:
            logger.error(f"Error getting context window: {e}")
            return {}
    
    def _calculate_confidence_factors(self, result: Dict[str, Any], 
                                    query: str, text: str) -> Dict[str, Any]:
        """Calculate confidence factors for the result."""
        try:
            factors = {
                'similarity_confidence': result['similarity_score'],
                'text_quality': min(len(text) / 1000, 1.0),  # Normalize by expected length
                'query_specificity': len(query.split()) / 10,  # Normalize by expected query length
                'result_diversity': 1.0,  # Will be updated by caller
                'semantic_alignment': result.get('relevance_indicators', {}).get('semantic_similarity', 0.0)
            }
            
            # Calculate overall confidence
            weights = [0.4, 0.2, 0.1, 0.1, 0.2]
            overall_confidence = sum(factor * weight for factor, weight in zip(factors.values(), weights))
            
            factors['overall_confidence'] = min(overall_confidence, 1.0)
            
            return factors
            
        except Exception as e:
            logger.error(f"Error calculating confidence factors: {e}")
            return {'overall_confidence': 0.0}
    
    def _get_chunk_text(self, chunk_id: str) -> str:
        """Get chunk text from database."""
        try:
            chunk = DocumentChunk.objects.get(id=chunk_id)
            return chunk.chunk_text
        except DocumentChunk.DoesNotExist:
            return ""
    
    def get_search_statistics(self) -> Dict[str, Any]:
        """Get search performance statistics."""
        return {
            'total_searches': self.search_stats['total_searches'],
            'avg_search_time': self.search_stats['avg_search_time'],
            'cache_hits': self.cache_hits,
            'cache_misses': self.cache_misses,
            'cache_hit_rate': self.cache_hits / (self.cache_hits + self.cache_misses) if (self.cache_hits + self.cache_misses) > 0 else 0,
            'indexed_documents': len(self.document_indexes),
            'total_chunks_indexed': sum(index_data['chunk_count'] for index_data in self.document_indexes.values())
        }
    
    def clear_cache(self):
        """Clear all cached data."""
        try:
            cache.clear()
            self.cache_hits = 0
            self.cache_misses = 0
            logger.info("Advanced search cache cleared")
        except Exception as e:
            logger.error(f"Error clearing cache: {e}")
    
    def optimize_index(self, document: Document) -> bool:
        """Optimize search index for better performance."""
        try:
            logger.info(f"Optimizing search index for document: {document.title}")
            
            # Rebuild index with optimized parameters
            if str(document.id) in self.document_indexes:
                del self.document_indexes[str(document.id)]
            
            # Clear cache for this document
            cache_key = f"advanced_index_{str(document.id)}"
            cache.delete(cache_key)
            
            # Rebuild with optimized settings
            success = self.build_advanced_index(document)
            
            if success:
                logger.info(f"Successfully optimized index for document: {document.title}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error optimizing index: {e}")
            return False

# Global advanced semantic search engine instance
advanced_semantic_search_engine = AdvancedSemanticSearchEngine()
