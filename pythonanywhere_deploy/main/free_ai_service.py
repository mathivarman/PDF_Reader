"""
Free AI Service for Q&A using multiple free APIs
Completely free up to 30,000 requests/month
"""

import requests
import json
import logging
import re
import hashlib
from typing import Dict, List, Optional
from django.conf import settings

logger = logging.getLogger(__name__)

class FreeAIService:
    """
    Free AI service using multiple free APIs
    No credit card required, up to 30,000 requests/month free
    """
    
    # Simple cache for consistent answers
    _answer_cache = {}
    
    # Multiple free models for better reliability
    QA_MODELS = {
        'huggingface_squad': 'deepset/roberta-base-squad2',  # Question-Answering model
        'huggingface_legal': 'nlpaueb/legal-bert-base-uncased',  # Legal domain model
        'huggingface_general': 'microsoft/DialoGPT-medium',  # General conversation
        'openai_free': 'gpt-3.5-turbo',  # OpenAI free tier
        'google_free': 'gemini-pro',  # Google's free model
    }
    
    @classmethod
    def get_huggingface_token(cls) -> Optional[str]:
        """Get Hugging Face token from environment variables"""
        return getattr(settings, 'HUGGINGFACE_TOKEN', None)
    
    @classmethod
    def get_openai_token(cls) -> Optional[str]:
        """Get OpenAI token from environment variables"""
        return getattr(settings, 'OPENAI_API_KEY', None)
    
    @classmethod
    def get_google_token(cls) -> Optional[str]:
        """Get Google API token from environment variables"""
        return getattr(settings, 'GOOGLE_API_KEY', None)
    
    @classmethod
    def answer_question(cls, question: str, context: str, model_type: str = 'default') -> Dict:
        """
        Answer a question using multiple free AI services with fallback
        
        Args:
            question: The question to answer
            context: The document context to search in
            model_type: Type of model to use
            
        Returns:
            Dict with answer, confidence, and metadata
        """
        # Create cache key
        cache_key = cls._create_cache_key(question, context)
        
        # Check cache first
        if cache_key in cls._answer_cache:
            logger.info(f"Cache hit for question: {question[:50]}...")
            return cls._answer_cache[cache_key]
        
        # Try multiple AI services in order of preference
        ai_services = [
            ('huggingface_squad', cls._try_huggingface_squad),
            ('huggingface_legal', cls._try_huggingface_legal),
            ('openai_free', cls._try_openai_free),
            ('google_free', cls._try_google_free),
            ('fallback', cls._fallback_answer)
        ]
        
        for service_name, service_func in ai_services:
            try:
                logger.info(f"Trying {service_name} for question: {question[:50]}...")
                result = service_func(question, context)
                
                if result.get('success') and result.get('answer'):
                    logger.info(f"Success with {service_name}")
                    # Cache the result
                    cls._answer_cache[cache_key] = result
                    return result
                    
            except Exception as e:
                logger.warning(f"Error with {service_name}: {e}")
                continue
        
        # If all services fail, use fallback
        fallback_result = cls._fallback_answer(question, context)
        cls._answer_cache[cache_key] = fallback_result
        return fallback_result
    
    @classmethod
    def _create_cache_key(cls, question: str, context: str) -> str:
        """Create a cache key for the question and context."""
        # Create a hash of question + first 1000 chars of context
        content = f"{question.lower().strip()}:{context[:1000].lower().strip()}"
        return hashlib.md5(content.encode()).hexdigest()
    
    @classmethod
    def _try_huggingface_squad(cls, question: str, context: str) -> Dict:
        """Try Hugging Face SQuAD model for Q&A."""
        try:
            api_url = "https://api-inference.huggingface.co/models/deepset/roberta-base-squad2"
            
            headers = {
                "Authorization": f"Bearer {cls.get_huggingface_token()}" if cls.get_huggingface_token() else None,
                "Content-Type": "application/json"
            }
            
            payload = {
                "inputs": {
                    "question": question,
                    "context": context[:4000]
                }
            }
            
            response = requests.post(api_url, headers=headers, json=payload, timeout=15)
            
            if response.status_code == 200:
                result = response.json()
                if isinstance(result, list) and len(result) > 0:
                    answer_data = result[0]
                    answer = answer_data.get('answer', '')
                    confidence = answer_data.get('score', 0.0)
                    
                    if answer and len(answer.strip()) > 10:  # Ensure meaningful answer
                        return {
                            'success': True,
                            'answer': answer,
                            'confidence': confidence,
                            'model': 'Hugging Face SQuAD',
                            'source': 'Hugging Face Free API'
                        }
            
            return {'success': False}
            
        except Exception as e:
            logger.error(f"Error with Hugging Face SQuAD: {e}")
            return {'success': False}
    
    @classmethod
    def _try_huggingface_legal(cls, question: str, context: str) -> Dict:
        """Try Hugging Face Legal BERT model."""
        try:
            api_url = "https://api-inference.huggingface.co/models/nlpaueb/legal-bert-base-uncased"
            
            headers = {
                "Authorization": f"Bearer {cls.get_huggingface_token()}" if cls.get_huggingface_token() else None,
                "Content-Type": "application/json"
            }
            
            # Create a prompt for legal document Q&A
            prompt = f"Based on this legal document: {context[:2000]}\n\nQuestion: {question}\n\nAnswer from the document:"
            payload = {"inputs": prompt}
            
            response = requests.post(api_url, headers=headers, json=payload, timeout=15)
            
            if response.status_code == 200:
                result = response.json()
                if isinstance(result, list) and len(result) > 0:
                    answer = str(result[0])
                    if len(answer.strip()) > 20:  # Ensure meaningful answer
                        return {
                            'success': True,
                            'answer': answer,
                            'confidence': 0.6,
                            'model': 'Hugging Face Legal BERT',
                            'source': 'Hugging Face Free API'
                        }
            
            return {'success': False}
            
        except Exception as e:
            logger.error(f"Error with Hugging Face Legal: {e}")
            return {'success': False}
    
    @classmethod
    def _try_openai_free(cls, question: str, context: str) -> Dict:
        """Try OpenAI free tier (if API key is available)."""
        try:
            api_key = cls.get_openai_token()
            if not api_key:
                return {'success': False}
            
            api_url = "https://api.openai.com/v1/chat/completions"
            
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            
            prompt = f"""Based on this document content, answer the question. Only use information from the document.

Document: {context[:3000]}

Question: {question}

Answer from the document:"""
            
            payload = {
                "model": "gpt-3.5-turbo",
                "messages": [
                    {"role": "system", "content": "You are a helpful assistant that answers questions based only on the provided document content. Always start your answer with 'According to the document:' or 'Based on the document:'"},
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": 300,
                "temperature": 0.3
            }
            
            response = requests.post(api_url, headers=headers, json=payload, timeout=15)
            
            if response.status_code == 200:
                result = response.json()
                answer = result['choices'][0]['message']['content'].strip()
                
                if answer and len(answer) > 20:
                    return {
                        'success': True,
                        'answer': answer,
                        'confidence': 0.8,
                        'model': 'OpenAI GPT-3.5',
                        'source': 'OpenAI Free API'
                    }
            
            return {'success': False}
            
        except Exception as e:
            logger.error(f"Error with OpenAI: {e}")
            return {'success': False}
    
    @classmethod
    def _try_google_free(cls, question: str, context: str) -> Dict:
        """Try Google's free Gemini model."""
        try:
            api_key = cls.get_google_token()
            if not api_key:
                return {'success': False}
            
            api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={api_key}"
            
            prompt = f"""Based on this document content, answer the question. Only use information from the document.

Document: {context[:3000]}

Question: {question}

Answer from the document:"""
            
            payload = {
                "contents": [
                    {
                        "parts": [
                            {"text": prompt}
                        ]
                    }
                ],
                "generationConfig": {
                    "maxOutputTokens": 300,
                    "temperature": 0.3
                }
            }
            
            response = requests.post(api_url, json=payload, timeout=15)
            
            if response.status_code == 200:
                result = response.json()
                answer = result['candidates'][0]['content']['parts'][0]['text'].strip()
                
                if answer and len(answer) > 20:
                    return {
                        'success': True,
                        'answer': answer,
                        'confidence': 0.7,
                        'model': 'Google Gemini',
                        'source': 'Google Free API'
                    }
            
            return {'success': False}
            
        except Exception as e:
            logger.error(f"Error with Google Gemini: {e}")
            return {'success': False}
    
    @classmethod
    def _fallback_answer(cls, question: str, context: str) -> Dict:
        """
        Fallback answer when AI service is unavailable
        Uses advanced text matching and NLTK to extract answers from document
        """
        try:
            import nltk
            from nltk.tokenize import sent_tokenize, word_tokenize
            from nltk.corpus import stopwords
            
            # Download required NLTK data (only once)
            try:
                nltk.data.find('tokenizers/punkt')
            except LookupError:
                nltk.download('punkt', quiet=True)
            
            try:
                nltk.data.find('corpora/stopwords')
            except LookupError:
                nltk.download('stopwords', quiet=True)
            
            # Advanced question analysis
            question_analysis = cls._analyze_question(question)
            
            # Extract relevant content from document
            relevant_content = cls._extract_relevant_content(question, context, question_analysis)
            
            if relevant_content:
                # Format the answer based on question type
                answer = cls._format_answer(question, relevant_content, question_analysis)
                confidence = 0.6  # Higher confidence for document-based answers
            else:
                # If no relevant content found, provide a helpful response
                answer = cls._generate_helpful_response(question, context)
                confidence = 0.2
            
            return {
                'success': True,
                'answer': answer,
                'confidence': confidence,
                'model': 'Advanced NLTK Document Analysis',
                'source': 'Document Content Extraction'
            }
            
        except Exception as e:
            logger.error(f"Error in fallback answer: {e}")
            return {
                'success': False,
                'answer': "I'm sorry, I'm unable to process your question at the moment. Please try again later.",
                'confidence': 0.0,
                'model': 'Error',
                'source': 'Error'
            }
    
    @classmethod
    def _analyze_question(cls, question: str) -> Dict:
        """Analyze question to understand what type of information is needed."""
        question_lower = question.lower()
        
        # Question type detection
        question_types = {
            'what': 'definition' if 'what is' in question_lower or 'what does' in question_lower else 'factual',
            'when': 'temporal',
            'where': 'location',
            'who': 'person',
            'how': 'procedural',
            'why': 'reasoning',
            'which': 'choice',
            'how much': 'quantity',
            'how many': 'quantity'
        }
        
        # Determine question type
        question_type = 'factual'  # default
        for key, q_type in question_types.items():
            if key in question_lower:
                question_type = q_type
                break
        
        # Extract key terms
        stop_words = set(stopwords.words('english'))
        words = word_tokenize(question_lower)
        key_terms = [word for word in words if word.lower() not in stop_words and len(word) > 2]
        
        return {
            'type': question_type,
            'key_terms': key_terms,
            'original': question
        }
    
    @classmethod
    def _extract_relevant_content(cls, question: str, context: str, question_analysis: Dict) -> List[str]:
        """Extract relevant sentences from the document context."""
        try:
            import nltk
            from nltk.tokenize import sent_tokenize, word_tokenize
            from nltk.corpus import stopwords
            
            # Tokenize context into sentences
            sentences = sent_tokenize(context)
            key_terms = question_analysis['key_terms']
            
            # Score sentences based on relevance
            scored_sentences = []
            for sentence in sentences:
                sentence_lower = sentence.lower()
                sentence_words = set(word_tokenize(sentence_lower))
                
                # Calculate relevance score
                score = 0
                
                # Exact keyword matches
                for term in key_terms:
                    if term in sentence_lower:
                        score += 2
                
                # Partial matches
                for term in key_terms:
                    if any(term in word for word in sentence_words):
                        score += 1
                
                # Question type specific scoring
                question_type = question_analysis['type']
                if question_type == 'temporal' and any(word in sentence_lower for word in ['date', 'time', 'when', 'period', 'duration']):
                    score += 1
                elif question_type == 'quantity' and any(word in sentence_lower for word in ['amount', 'number', 'total', 'sum', 'cost', 'price']):
                    score += 1
                elif question_type == 'person' and any(word in sentence_lower for word in ['person', 'individual', 'party', 'company', 'organization']):
                    score += 1
                
                if score > 0:
                    scored_sentences.append((sentence, score))
            
            # Sort by relevance score and return top sentences
            scored_sentences.sort(key=lambda x: x[1], reverse=True)
            relevant_sentences = [sentence for sentence, score in scored_sentences[:3]]
            
            return relevant_sentences
            
        except Exception as e:
            logger.error(f"Error extracting relevant content: {e}")
            return []
    
    @classmethod
    def _format_answer(cls, question: str, relevant_content: List[str], question_analysis: Dict) -> str:
        """Format the answer based on question type and relevant content."""
        if not relevant_content:
            return "I couldn't find specific information about this in the document."
        
        question_type = question_analysis['type']
        
        if question_type == 'definition':
            # For definition questions, provide a clear explanation
            return f"Based on the document: {relevant_content[0]}"
        
        elif question_type == 'temporal':
            # For time-related questions, extract and format dates/times
            time_info = cls._extract_time_info(relevant_content)
            if time_info:
                return f"According to the document: {time_info}"
            else:
                return f"The document states: {relevant_content[0]}"
        
        elif question_type == 'quantity':
            # For quantity questions, extract numbers
            quantity_info = cls._extract_quantity_info(relevant_content)
            if quantity_info:
                return f"The document indicates: {quantity_info}"
            else:
                return f"Based on the document: {relevant_content[0]}"
        
        elif question_type == 'procedural':
            # For how-to questions, provide step-by-step information
            return f"The document outlines the following process: {' '.join(relevant_content)}"
        
        else:
            # For other question types, provide the most relevant information
            return f"According to the document: {' '.join(relevant_content)}"
    
    @classmethod
    def _extract_time_info(cls, sentences: List[str]) -> Optional[str]:
        """Extract time-related information from sentences."""
        time_patterns = [
            r'\b\d{1,2}/\d{1,2}/\d{2,4}\b',  # Dates like 12/25/2023
            r'\b\d{4}-\d{2}-\d{2}\b',  # ISO dates like 2023-12-25
            r'\b(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4}\b',
            r'\b\d{1,2}\s+(days|weeks|months|years)\b',
            r'\b(immediately|within|before|after|during)\b'
        ]
        
        for sentence in sentences:
            for pattern in time_patterns:
                matches = re.findall(pattern, sentence, re.IGNORECASE)
                if matches:
                    return sentence
        
        return None
    
    @classmethod
    def _extract_quantity_info(cls, sentences: List[str]) -> Optional[str]:
        """Extract quantity-related information from sentences."""
        quantity_patterns = [
            r'\$\d+(?:,\d{3})*(?:\.\d{2})?',  # Currency amounts
            r'\b\d+(?:,\d{3})*(?:\.\d+)?\s*(dollars?|USD|euros?|pounds?)\b',
            r'\b\d+(?:,\d{3})*(?:\.\d+)?\s*(percent|%)\b',
            r'\b\d+(?:,\d{3})*(?:\.\d+)?\s*(units?|items?|pieces?)\b'
        ]
        
        for sentence in sentences:
            for pattern in quantity_patterns:
                matches = re.findall(pattern, sentence, re.IGNORECASE)
                if matches:
                    return sentence
        
        return None
    
    @classmethod
    def _generate_helpful_response(cls, question: str, context: str) -> str:
        """Generate a helpful response when no specific answer is found."""
        # Provide suggestions based on document content
        context_lower = context.lower()
        
        if 'contract' in context_lower or 'agreement' in context_lower:
            return "This appears to be a legal document. You might want to ask about specific terms, obligations, or clauses mentioned in the document."
        elif 'payment' in context_lower or 'cost' in context_lower:
            return "The document contains payment-related information. Try asking about specific amounts, payment terms, or financial obligations."
        elif 'termination' in context_lower or 'end' in context_lower:
            return "The document discusses termination or ending conditions. Ask about specific termination terms or procedures."
        else:
            return "I couldn't find specific information about your question in the document. Try rephrasing your question or ask about a different aspect of the document."
    
    @classmethod
    def generate_summary(cls, text: str) -> Dict:
        """
        Generate a summary using free AI service
        """
        try:
            # Use a summarization model
            api_url = "https://api-inference.huggingface.co/models/facebook/bart-large-cnn"
            
            headers = {
                "Authorization": f"Bearer {cls.get_huggingface_token()}" if cls.get_huggingface_token() else None,
                "Content-Type": "application/json"
            }
            
            payload = {
                "inputs": text[:1000],  # Limit input length
                "parameters": {
                    "max_length": 150,
                    "min_length": 50
                }
            }
            
            response = requests.post(api_url, headers=headers, json=payload, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                summary = result[0].get('summary_text', '') if isinstance(result, list) else str(result)
                
                return {
                    'success': True,
                    'summary': summary,
                    'source': 'Hugging Face Free API'
                }
            else:
                return cls._fallback_summary(text)
                
        except Exception as e:
            logger.error(f"Error in generate_summary: {e}")
            return cls._fallback_summary(text)
    
    @classmethod
    def _fallback_summary(cls, text: str) -> Dict:
        """
        Fallback summary generation
        """
        try:
            import nltk
            from nltk.tokenize import sent_tokenize
            
            sentences = sent_tokenize(text)
            summary = ' '.join(sentences[:3])  # First 3 sentences
            
            return {
                'success': True,
                'summary': summary,
                'source': 'NLTK Fallback'
            }
        except Exception as e:
            logger.error(f"Error in fallback summary: {e}")
            return {
                'success': False,
                'summary': "Unable to generate summary at this time.",
                'source': 'Error'
            }
