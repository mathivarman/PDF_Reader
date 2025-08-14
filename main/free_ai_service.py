"""
Free AI Service for Q&A using Hugging Face Inference API
Completely free up to 30,000 requests/month
"""

import requests
import json
import logging
from typing import Dict, List, Optional
from django.conf import settings

logger = logging.getLogger(__name__)

class FreeAIService:
    """
    Free AI service using Hugging Face Inference API
    No credit card required, up to 30,000 requests/month free
    """
    
    # Free Hugging Face models for Q&A
    QA_MODELS = {
        'default': 'deepset/roberta-base-squad2',  # Question-Answering model
        'legal': 'nlpaueb/legal-bert-base-uncased',  # Legal domain model
        'general': 'microsoft/DialoGPT-medium',  # General conversation
    }
    
    @classmethod
    def get_huggingface_token(cls) -> Optional[str]:
        """Get Hugging Face token from environment variables"""
        return getattr(settings, 'HUGGINGFACE_TOKEN', None)
    
    @classmethod
    def answer_question(cls, question: str, context: str, model_type: str = 'default') -> Dict:
        """
        Answer a question using free Hugging Face API
        
        Args:
            question: The question to answer
            context: The document context to search in
            model_type: Type of model to use ('default', 'legal', 'general')
            
        Returns:
            Dict with answer, confidence, and metadata
        """
        try:
            model_name = cls.QA_MODELS.get(model_type, cls.QA_MODELS['default'])
            
            # Prepare the API request
            api_url = f"https://api-inference.huggingface.co/models/{model_name}"
            
            headers = {
                "Authorization": f"Bearer {cls.get_huggingface_token()}" if cls.get_huggingface_token() else None,
                "Content-Type": "application/json"
            }
            
            # For question-answering models
            if 'squad' in model_name.lower():
                payload = {
                    "inputs": {
                        "question": question,
                        "context": context[:4000]  # Limit context length
                    }
                }
            else:
                # For general models, create a prompt
                prompt = f"Context: {context[:2000]}\n\nQuestion: {question}\n\nAnswer:"
                payload = {"inputs": prompt}
            
            # Make the API request
            response = requests.post(api_url, headers=headers, json=payload, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                
                # Parse different response formats
                if isinstance(result, list) and len(result) > 0:
                    answer_data = result[0]
                else:
                    answer_data = result
                
                # Extract answer based on model type
                if 'squad' in model_name.lower():
                    answer = answer_data.get('answer', '')
                    confidence = answer_data.get('score', 0.0)
                else:
                    # For general models, extract generated text
                    if isinstance(answer_data, dict) and 'generated_text' in answer_data:
                        answer = answer_data['generated_text']
                    else:
                        answer = str(answer_data)
                    confidence = 0.7  # Default confidence for general models
                
                return {
                    'success': True,
                    'answer': answer,
                    'confidence': confidence,
                    'model': model_name,
                    'source': 'Hugging Face Free API'
                }
            else:
                logger.warning(f"Hugging Face API error: {response.status_code} - {response.text}")
                return cls._fallback_answer(question, context)
                
        except Exception as e:
            logger.error(f"Error in FreeAIService.answer_question: {e}")
            return cls._fallback_answer(question, context)
    
    @classmethod
    def _fallback_answer(cls, question: str, context: str) -> Dict:
        """
        Fallback answer when AI service is unavailable
        Uses simple text matching and NLTK
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
            
            # Simple keyword-based answer
            question_words = set(word_tokenize(question.lower()))
            stop_words = set(stopwords.words('english'))
            question_keywords = question_words - stop_words
            
            # Find relevant sentences
            sentences = sent_tokenize(context)
            relevant_sentences = []
            
            for sentence in sentences:
                sentence_words = set(word_tokenize(sentence.lower()))
                if question_keywords & sentence_words:
                    relevant_sentences.append(sentence)
            
            if relevant_sentences:
                answer = ' '.join(relevant_sentences[:3])  # Top 3 relevant sentences
                confidence = 0.6
            else:
                # If no relevant sentences found, return a general response
                answer = "Based on the document content, I couldn't find a specific answer to your question. Please try rephrasing or ask about a different aspect of the document."
                confidence = 0.3
            
            return {
                'success': True,
                'answer': answer,
                'confidence': confidence,
                'model': 'NLTK Fallback',
                'source': 'Local Processing'
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
