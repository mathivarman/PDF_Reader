"""
Semantic Search Engine for Document Q&A
Uses sentence transformers and FAISS for efficient similarity search
"""

import numpy as np
import logging
from typing import List, Dict, Any, Optional, Tuple
from sentence_transformers import SentenceTransformer
import faiss
from sklearn.metrics.pairwise import cosine_similarity
import json
import pickle
from pathlib import Path

from django.conf import settings
from .models import Document, DocumentChunk, Question, Answer, Citation

logger = logging.getLogger(__name__)

class SemanticSearchEngine:
    """Semantic search engine using sentence transformers and FAISS."""
    
    def __init__(self, model_name: str = 'all-MiniLM-L6-v2'):
        """Initialize the semantic search engine."""
        self.model_name = model_name
        self.model = None
        self.index = None
        self.chunk_mapping = {}
        self.embedding_dim = 384  # Default for all-MiniLM-L6-v2
        
        # Initialize the model
        self._initialize_model()
    
    def _initialize_model(self):
        """Initialize the sentence transformer model."""
        try:
            logger.info(f"Loading sentence transformer model: {self.model_name}")
            self.model = SentenceTransformer(self.model_name)
            self.embedding_dim = self.model.get_sentence_embedding_dimension()
            logger.info(f"Model loaded successfully. Embedding dimension: {self.embedding_dim}")
        except Exception as e:
            logger.error(f"Error loading sentence transformer model: {e}")
            raise
    
    def create_embeddings(self, texts: List[str]) -> np.ndarray:
        """Create embeddings for a list of texts."""
        try:
            embeddings = self.model.encode(texts, show_progress_bar=True, convert_to_numpy=True)
            return embeddings
        except Exception as e:
            logger.error(f"Error creating embeddings: {e}")
            raise
    
    def chunk_text_semantic(self, text: str, max_chunk_size: int = 512, overlap: int = 50) -> List[str]:
        """Create semantic chunks from text with overlap."""
        try:
            # Split text into sentences first
            sentences = text.split('. ')
            chunks = []
            current_chunk = ""
            
            for sentence in sentences:
                # If adding this sentence would exceed max size, save current chunk
                if len(current_chunk) + len(sentence) > max_chunk_size and current_chunk:
                    chunks.append(current_chunk.strip())
                    # Start new chunk with overlap
                    overlap_text = current_chunk[-overlap:] if overlap > 0 else ""
                    current_chunk = overlap_text + sentence + ". "
                else:
                    current_chunk += sentence + ". "
            
            # Add the last chunk if it exists
            if current_chunk.strip():
                chunks.append(current_chunk.strip())
            
            return chunks
        except Exception as e:
            logger.error(f"Error chunking text semantically: {e}")
            raise
    
    def process_document_chunks(self, document: Document) -> List[DocumentChunk]:
        """Process document and create semantic chunks with embeddings."""
        try:
            logger.info(f"Processing document chunks for: {document.title}")
            
            # Get document text from chunks or analysis
            chunks = DocumentChunk.objects.filter(document=document)
            if chunks.exists():
                logger.info(f"Document already has {chunks.count()} chunks")
                return list(chunks)
            
            # Get text from analysis
            analysis = document.analyses.first()
            if not analysis:
                logger.warning(f"No analysis found for document: {document.title}")
                return []
            
            # Get text from document chunks (from text processing)
            text_chunks = analysis.documentchunk_set.all()
            if not text_chunks.exists():
                logger.warning(f"No text chunks found for document: {document.title}")
                return []
            
            # Create semantic chunks
            all_text = " ".join([chunk.chunk_text for chunk in text_chunks])
            semantic_chunks = self.chunk_text_semantic(all_text)
            
            # Create embeddings for chunks
            embeddings = self.create_embeddings(semantic_chunks)
            
            # Create DocumentChunk objects
            document_chunks = []
            for i, (chunk_text, embedding) in enumerate(zip(semantic_chunks, embeddings)):
                chunk = DocumentChunk.objects.create(
                    document=document,
                    chunk_text=chunk_text,
                    chunk_index=i,
                    page_number=0,  # We'll update this later
                    embedding=embedding.tolist()
                )
                document_chunks.append(chunk)
            
            logger.info(f"Created {len(document_chunks)} semantic chunks for document: {document.title}")
            return document_chunks
            
        except Exception as e:
            logger.error(f"Error processing document chunks: {e}")
            raise
    
    def build_search_index(self, document: Document) -> bool:
        """Build FAISS index for a document."""
        try:
            logger.info(f"Building search index for document: {document.title}")
            
            # Get document chunks
            chunks = DocumentChunk.objects.filter(document=document)
            if not chunks.exists():
                logger.warning(f"No chunks found for document: {document.title}")
                return False
            
            # Extract embeddings
            embeddings = []
            chunk_ids = []
            
            for chunk in chunks:
                if chunk.embedding:
                    embeddings.append(chunk.embedding)
                    chunk_ids.append(str(chunk.id))
            
            if not embeddings:
                logger.warning(f"No embeddings found for document: {document.title}")
                return False
            
            # Convert to numpy array
            embeddings_array = np.array(embeddings, dtype=np.float32)
            
            # Create FAISS index
            index = faiss.IndexFlatIP(self.embedding_dim)  # Inner product for cosine similarity
            index.add(embeddings_array)
            
            # Store index and mapping
            self.index = index
            self.chunk_mapping = {i: chunk_id for i, chunk_id in enumerate(chunk_ids)}
            
            logger.info(f"Built search index with {len(embeddings)} vectors for document: {document.title}")
            return True
            
        except Exception as e:
            logger.error(f"Error building search index: {e}")
            return False
    
    def search_similar_chunks(self, query: str, document: Document, top_k: int = 5) -> List[Dict[str, Any]]:
        """Search for similar chunks in a document."""
        try:
            # Build index if not exists
            if not self.index:
                if not self.build_search_index(document):
                    return []
            
            # Create query embedding
            query_embedding = self.create_embeddings([query])
            
            # Search in FAISS index
            scores, indices = self.index.search(query_embedding, min(top_k, self.index.ntotal))
            
            # Get results
            results = []
            for score, idx in zip(scores[0], indices[0]):
                if idx in self.chunk_mapping:
                    chunk_id = self.chunk_mapping[idx]
                    chunk = DocumentChunk.objects.get(id=chunk_id)
                    
                    results.append({
                        'chunk_id': str(chunk.id),
                        'chunk_text': chunk.chunk_text,
                        'page_number': chunk.page_number,
                        'similarity_score': float(score),
                        'chunk_index': chunk.chunk_index
                    })
            
            return results
            
        except Exception as e:
            logger.error(f"Error searching similar chunks: {e}")
            return []
    
    def answer_question(self, question_text: str, document: Document) -> Dict[str, Any]:
        """Answer a question using semantic search."""
        try:
            logger.info(f"Answering question: {question_text}")
            
            # Search for relevant chunks
            similar_chunks = self.search_similar_chunks(question_text, document, top_k=3)
            
            if not similar_chunks:
                return {
                    'answer': 'I could not find relevant information to answer your question.',
                    'confidence_score': 0.0,
                    'citations': [],
                    'source_chunks': []
                }
            
            # Generate answer from relevant chunks
            context_text = " ".join([chunk['chunk_text'] for chunk in similar_chunks])
            
            # Simple answer generation (in Phase 3 Week 10, we'll enhance this)
            answer = self._generate_simple_answer(question_text, context_text)
            
            # Calculate confidence based on similarity scores
            avg_similarity = np.mean([chunk['similarity_score'] for chunk in similar_chunks])
            confidence_score = min(avg_similarity * 100, 100.0)
            
            # Create citations
            citations = []
            for chunk in similar_chunks:
                citations.append({
                    'text': chunk['chunk_text'][:200] + "...",
                    'page_number': chunk['page_number'],
                    'similarity_score': chunk['similarity_score']
                })
            
            return {
                'answer': answer,
                'confidence_score': confidence_score,
                'citations': citations,
                'source_chunks': [chunk['chunk_id'] for chunk in similar_chunks]
            }
            
        except Exception as e:
            logger.error(f"Error answering question: {e}")
            return {
                'answer': 'Sorry, I encountered an error while processing your question.',
                'confidence_score': 0.0,
                'citations': [],
                'source_chunks': []
            }
    
    def _generate_simple_answer(self, question: str, context: str) -> str:
        """Generate a simple answer from context (placeholder for now)."""
        # This is a simple implementation - in Week 10 we'll enhance this
        # For now, return the most relevant context
        sentences = context.split('. ')
        if len(sentences) > 0:
            return sentences[0] + "."
        return context[:200] + "..."
    
    def get_document_summary(self, document: Document) -> Dict[str, Any]:
        """Get semantic summary of document chunks."""
        try:
            chunks = DocumentChunk.objects.filter(document=document)
            if not chunks.exists():
                return {'summary': '', 'key_topics': []}
            
            # Get chunk texts
            chunk_texts = [chunk.chunk_text for chunk in chunks]
            
            # Create embeddings for all chunks
            embeddings = self.create_embeddings(chunk_texts)
            
            # Calculate document embedding (mean of all chunk embeddings)
            doc_embedding = np.mean(embeddings, axis=0)
            
            # Find most representative chunks (closest to document center)
            similarities = cosine_similarity([doc_embedding], embeddings)[0]
            top_indices = np.argsort(similarities)[-3:]  # Top 3 most representative
            
            # Create summary from top chunks
            summary_chunks = [chunk_texts[i] for i in top_indices]
            summary = " ".join(summary_chunks)
            
            return {
                'summary': summary,
                'key_topics': [f"Topic {i+1}" for i in range(len(top_indices))],
                'embedding': doc_embedding.tolist()
            }
            
        except Exception as e:
            logger.error(f"Error getting document summary: {e}")
            return {'summary': '', 'key_topics': []}

# Global semantic search engine instance
semantic_search_engine = SemanticSearchEngine()
