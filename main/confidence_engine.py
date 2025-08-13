"""
Confidence Engine for Week 11
Advanced confidence scoring with multiple algorithms and thresholds
"""

import logging
import math
import statistics
from typing import Dict, Any, List, Optional, Tuple
from enum import Enum
from dataclasses import dataclass

logger = logging.getLogger(__name__)

class ConfidenceLevel(Enum):
    """Confidence levels for answers."""
    VERY_LOW = "very_low"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"

@dataclass
class ConfidenceFactors:
    """Factors that influence confidence scoring."""
    similarity_score: float
    result_count: int
    question_complexity: str
    has_legal_terms: bool
    answer_length: int
    citation_quality: float
    source_diversity: float
    semantic_coherence: float
    keyword_overlap: float
    temporal_relevance: float = 1.0

class ConfidenceAlgorithm:
    """Base class for confidence algorithms."""
    
    def calculate_confidence(self, factors: ConfidenceFactors) -> float:
        """Calculate confidence score (0-100)."""
        raise NotImplementedError
    
    def get_confidence_level(self, score: float) -> ConfidenceLevel:
        """Get confidence level from score."""
        if score >= 90:
            return ConfidenceLevel.VERY_HIGH
        elif score >= 75:
            return ConfidenceLevel.HIGH
        elif score >= 60:
            return ConfidenceLevel.MEDIUM
        elif score >= 40:
            return ConfidenceLevel.LOW
        else:
            return ConfidenceLevel.VERY_LOW

class WeightedConfidenceAlgorithm(ConfidenceAlgorithm):
    """Weighted confidence algorithm with multiple factors."""
    
    def __init__(self):
        """Initialize with default weights."""
        self.weights = {
            'similarity': 0.35,
            'result_count': 0.15,
            'complexity': 0.10,
            'legal_terms': 0.05,
            'answer_length': 0.10,
            'citation_quality': 0.15,
            'source_diversity': 0.05,
            'semantic_coherence': 0.05
        }
    
    def calculate_confidence(self, factors: ConfidenceFactors) -> float:
        """Calculate weighted confidence score."""
        try:
            # Normalize similarity score (0-1 to 0-100)
            similarity_score = factors.similarity_score * 100
            
            # Result count bonus (more results = higher confidence)
            result_bonus = min(factors.result_count * 5, 20)
            
            # Complexity adjustment
            complexity_score = self._get_complexity_score(factors.question_complexity)
            
            # Legal terms bonus
            legal_bonus = 10 if factors.has_legal_terms else 0
            
            # Answer length score (optimal length gets highest score)
            length_score = self._get_length_score(factors.answer_length)
            
            # Citation quality (0-100)
            citation_score = factors.citation_quality * 100
            
            # Source diversity (0-100)
            diversity_score = factors.source_diversity * 100
            
            # Semantic coherence (0-100)
            coherence_score = factors.semantic_coherence * 100
            
            # Calculate weighted score
            weighted_score = (
                similarity_score * self.weights['similarity'] +
                result_bonus * self.weights['result_count'] +
                complexity_score * self.weights['complexity'] +
                legal_bonus * self.weights['legal_terms'] +
                length_score * self.weights['answer_length'] +
                citation_score * self.weights['citation_quality'] +
                diversity_score * self.weights['source_diversity'] +
                coherence_score * self.weights['semantic_coherence']
            )
            
            return min(round(weighted_score, 2), 100.0)
            
        except Exception as e:
            logger.error(f"Error calculating weighted confidence: {e}")
            return 0.0
    
    def _get_complexity_score(self, complexity: str) -> float:
        """Get complexity adjustment score."""
        complexity_scores = {
            'simple': 100,
            'medium': 85,
            'complex': 70
        }
        return complexity_scores.get(complexity, 85)
    
    def _get_length_score(self, length: int) -> float:
        """Get answer length score (optimal around 100-300 words)."""
        if length < 50:
            return 60  # Too short
        elif length < 100:
            return 80  # Short but acceptable
        elif length < 300:
            return 100  # Optimal length
        elif length < 500:
            return 90   # Long but still good
        else:
            return 70   # Too long

class BayesianConfidenceAlgorithm(ConfidenceAlgorithm):
    """Bayesian confidence algorithm using probability theory."""
    
    def __init__(self):
        """Initialize Bayesian algorithm."""
        # Prior probabilities for different confidence levels
        self.priors = {
            'high_similarity': 0.7,
            'multiple_results': 0.6,
            'legal_terms': 0.8,
            'good_citations': 0.75
        }
    
    def calculate_confidence(self, factors: ConfidenceFactors) -> float:
        """Calculate Bayesian confidence score."""
        try:
            # Calculate likelihoods
            likelihoods = self._calculate_likelihoods(factors)
            
            # Calculate posterior probability
            posterior = self._calculate_posterior(likelihoods)
            
            # Convert to confidence score
            confidence_score = posterior * 100
            
            return min(round(confidence_score, 2), 100.0)
            
        except Exception as e:
            logger.error(f"Error calculating Bayesian confidence: {e}")
            return 0.0
    
    def _calculate_likelihoods(self, factors: ConfidenceFactors) -> Dict[str, float]:
        """Calculate likelihoods for different factors."""
        likelihoods = {}
        
        # Similarity likelihood
        likelihoods['similarity'] = factors.similarity_score
        
        # Result count likelihood
        likelihoods['results'] = min(factors.result_count / 5, 1.0)
        
        # Legal terms likelihood
        likelihoods['legal'] = 1.0 if factors.has_legal_terms else 0.5
        
        # Citation quality likelihood
        likelihoods['citations'] = factors.citation_quality
        
        # Complexity likelihood
        complexity_likelihoods = {'simple': 0.9, 'medium': 0.8, 'complex': 0.6}
        likelihoods['complexity'] = complexity_likelihoods.get(factors.question_complexity, 0.8)
        
        return likelihoods
    
    def _calculate_posterior(self, likelihoods: Dict[str, float]) -> float:
        """Calculate posterior probability using Bayes' theorem."""
        # Combine likelihoods with priors
        combined_prob = 1.0
        
        for factor, likelihood in likelihoods.items():
            prior = self.priors.get(factor, 0.5)
            # Simple Bayesian update
            combined_prob *= (likelihood * prior + (1 - likelihood) * (1 - prior))
        
        # Normalize to 0-1 range
        return min(combined_prob, 1.0)

class EnsembleConfidenceAlgorithm(ConfidenceAlgorithm):
    """Ensemble confidence algorithm combining multiple approaches."""
    
    def __init__(self):
        """Initialize ensemble algorithm."""
        self.algorithms = [
            WeightedConfidenceAlgorithm(),
            BayesianConfidenceAlgorithm()
        ]
        self.weights = [0.6, 0.4]  # Weight for each algorithm
    
    def calculate_confidence(self, factors: ConfidenceFactors) -> float:
        """Calculate ensemble confidence score."""
        try:
            scores = []
            
            for algorithm in self.algorithms:
                score = algorithm.calculate_confidence(factors)
                scores.append(score)
            
            # Calculate weighted average
            weighted_score = sum(score * weight for score, weight in zip(scores, self.weights))
            
            return min(round(weighted_score, 2), 100.0)
            
        except Exception as e:
            logger.error(f"Error calculating ensemble confidence: {e}")
            return 0.0

class ConfidenceThresholdManager:
    """Manages confidence thresholds and decision making."""
    
    def __init__(self):
        """Initialize threshold manager."""
        self.thresholds = {
            'minimum_acceptable': 40.0,
            'recommended_minimum': 60.0,
            'high_confidence': 80.0,
            'excellent_confidence': 90.0
        }
    
    def should_show_answer(self, confidence_score: float) -> bool:
        """Determine if answer should be shown to user."""
        return confidence_score >= self.thresholds['minimum_acceptable']
    
    def get_confidence_recommendation(self, confidence_score: float) -> str:
        """Get recommendation based on confidence score."""
        if confidence_score >= self.thresholds['excellent_confidence']:
            return "Excellent confidence - Answer is highly reliable"
        elif confidence_score >= self.thresholds['high_confidence']:
            return "High confidence - Answer is reliable"
        elif confidence_score >= self.thresholds['recommended_minimum']:
            return "Good confidence - Answer is generally reliable"
        elif confidence_score >= self.thresholds['minimum_acceptable']:
            return "Low confidence - Answer may be incomplete or uncertain"
        else:
            return "Very low confidence - Answer may not be reliable"
    
    def get_confidence_color(self, confidence_score: float) -> str:
        """Get color class for confidence display."""
        if confidence_score >= 80:
            return "success"
        elif confidence_score >= 60:
            return "warning"
        else:
            return "danger"

class ConfidenceAnalyzer:
    """Analyzes confidence patterns and provides insights."""
    
    def __init__(self):
        """Initialize confidence analyzer."""
        self.algorithm = EnsembleConfidenceAlgorithm()
        self.threshold_manager = ConfidenceThresholdManager()
    
    def analyze_confidence_factors(self, factors: ConfidenceFactors) -> Dict[str, Any]:
        """Analyze confidence factors and provide detailed breakdown."""
        try:
            # Calculate overall confidence
            overall_confidence = self.algorithm.calculate_confidence(factors)
            
            # Get confidence level
            confidence_level = self.algorithm.get_confidence_level(overall_confidence)
            
            # Get recommendation
            recommendation = self.threshold_manager.get_confidence_recommendation(overall_confidence)
            
            # Calculate factor contributions
            factor_contributions = self._calculate_factor_contributions(factors)
            
            # Identify strengths and weaknesses
            strengths, weaknesses = self._identify_strengths_weaknesses(factors)
            
            return {
                'overall_confidence': overall_confidence,
                'confidence_level': confidence_level.value,
                'recommendation': recommendation,
                'factor_contributions': factor_contributions,
                'strengths': strengths,
                'weaknesses': weaknesses,
                'should_show': self.threshold_manager.should_show_answer(overall_confidence),
                'color_class': self.threshold_manager.get_confidence_color(overall_confidence)
            }
            
        except Exception as e:
            logger.error(f"Error analyzing confidence factors: {e}")
            return {
                'overall_confidence': 0.0,
                'confidence_level': ConfidenceLevel.VERY_LOW.value,
                'recommendation': 'Error analyzing confidence',
                'factor_contributions': {},
                'strengths': [],
                'weaknesses': ['Error in confidence analysis'],
                'should_show': False,
                'color_class': 'danger'
            }
    
    def _calculate_factor_contributions(self, factors: ConfidenceFactors) -> Dict[str, float]:
        """Calculate individual factor contributions to confidence."""
        contributions = {}
        
        # Similarity contribution
        contributions['similarity'] = factors.similarity_score * 100
        
        # Result count contribution
        contributions['result_count'] = min(factors.result_count * 10, 20)
        
        # Complexity contribution
        complexity_scores = {'simple': 100, 'medium': 85, 'complex': 70}
        contributions['complexity'] = complexity_scores.get(factors.question_complexity, 85)
        
        # Legal terms contribution
        contributions['legal_terms'] = 100 if factors.has_legal_terms else 50
        
        # Answer length contribution
        length_scores = {50: 60, 100: 80, 300: 100, 500: 90}
        contributions['answer_length'] = length_scores.get(factors.answer_length, 70)
        
        # Citation quality contribution
        contributions['citation_quality'] = factors.citation_quality * 100
        
        return contributions
    
    def _identify_strengths_weaknesses(self, factors: ConfidenceFactors) -> Tuple[List[str], List[str]]:
        """Identify strengths and weaknesses in confidence factors."""
        strengths = []
        weaknesses = []
        
        # Analyze similarity
        if factors.similarity_score >= 0.8:
            strengths.append("High semantic similarity to question")
        elif factors.similarity_score < 0.5:
            weaknesses.append("Low semantic similarity to question")
        
        # Analyze result count
        if factors.result_count >= 3:
            strengths.append("Multiple relevant sources found")
        elif factors.result_count == 1:
            weaknesses.append("Limited source material")
        
        # Analyze legal terms
        if factors.has_legal_terms:
            strengths.append("Question contains legal terminology")
        
        # Analyze answer length
        if 100 <= factors.answer_length <= 300:
            strengths.append("Optimal answer length")
        elif factors.answer_length < 50:
            weaknesses.append("Answer may be too brief")
        elif factors.answer_length > 500:
            weaknesses.append("Answer may be too verbose")
        
        # Analyze citation quality
        if factors.citation_quality >= 0.8:
            strengths.append("High quality citations")
        elif factors.citation_quality < 0.5:
            weaknesses.append("Low quality citations")
        
        return strengths, weaknesses

# Global confidence analyzer instance
confidence_analyzer = ConfidenceAnalyzer()
