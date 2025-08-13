"""
Legal Recommendation Engine for Week 11
Provides intelligent legal recommendations based on document analysis
"""

import logging
import re
from typing import Dict, Any, List, Optional, Tuple
from enum import Enum
from dataclasses import dataclass

logger = logging.getLogger(__name__)

class RecommendationType(Enum):
    """Types of legal recommendations."""
    WARNING = "warning"
    ADVICE = "advice"
    ACTION = "action"
    INFORMATION = "information"
    REVIEW = "review"

class RecommendationPriority(Enum):
    """Priority levels for recommendations."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

@dataclass
class LegalRecommendation:
    """Legal recommendation with metadata."""
    title: str
    description: str
    recommendation_type: RecommendationType
    priority: RecommendationPriority
    reasoning: str
    suggested_actions: List[str]
    related_clauses: List[str] = None
    related_red_flags: List[str] = None
    confidence: float = 0.0

class LegalRuleEngine:
    """Engine for applying legal rules and generating recommendations."""
    
    def __init__(self):
        """Initialize legal rule engine."""
        self.legal_rules = self._initialize_legal_rules()
        self.recommendation_templates = self._initialize_templates()
    
    def _initialize_legal_rules(self) -> Dict[str, Dict[str, Any]]:
        """Initialize legal rules for different scenarios."""
        return {
            'liability_issues': {
                'triggers': ['liability', 'damages', 'indemnification', 'hold harmless'],
                'priority': RecommendationPriority.HIGH,
                'type': RecommendationType.WARNING,
                'template': 'liability_warning'
            },
            'termination_clauses': {
                'triggers': ['termination', 'cancellation', 'breach', 'default'],
                'priority': RecommendationPriority.MEDIUM,
                'type': RecommendationType.ADVICE,
                'template': 'termination_advice'
            },
            'payment_terms': {
                'triggers': ['payment', 'invoice', 'due date', 'late fees', 'interest'],
                'priority': RecommendationPriority.MEDIUM,
                'type': RecommendationType.INFORMATION,
                'template': 'payment_info'
            },
            'confidentiality': {
                'triggers': ['confidential', 'non-disclosure', 'trade secret', 'proprietary'],
                'priority': RecommendationPriority.HIGH,
                'type': RecommendationType.WARNING,
                'template': 'confidentiality_warning'
            },
            'intellectual_property': {
                'triggers': ['intellectual property', 'copyright', 'patent', 'trademark', 'IP'],
                'priority': RecommendationPriority.HIGH,
                'type': RecommendationType.REVIEW,
                'template': 'ip_review'
            },
            'force_majeure': {
                'triggers': ['force majeure', 'act of god', 'unforeseen', 'beyond control'],
                'priority': RecommendationPriority.MEDIUM,
                'type': RecommendationType.INFORMATION,
                'template': 'force_majeure_info'
            },
            'governing_law': {
                'triggers': ['governing law', 'jurisdiction', 'venue', 'choice of law'],
                'priority': RecommendationPriority.MEDIUM,
                'type': RecommendationType.INFORMATION,
                'template': 'governing_law_info'
            },
            'dispute_resolution': {
                'triggers': ['arbitration', 'mediation', 'dispute', 'litigation', 'court'],
                'priority': RecommendationPriority.MEDIUM,
                'type': RecommendationType.ADVICE,
                'template': 'dispute_resolution_advice'
            }
        }
    
    def _initialize_templates(self) -> Dict[str, Dict[str, str]]:
        """Initialize recommendation templates."""
        return {
            'liability_warning': {
                'title': 'Liability Clause Review Required',
                'description': 'This document contains significant liability provisions that require careful review.',
                'reasoning': 'Liability clauses can expose parties to substantial financial risk and legal obligations.',
                'suggested_actions': [
                    'Review liability limits and exclusions',
                    'Consider insurance requirements',
                    'Evaluate indemnification obligations',
                    'Consult with legal counsel'
                ]
            },
            'termination_advice': {
                'title': 'Termination Provisions Analysis',
                'description': 'Review termination clauses to understand exit conditions and obligations.',
                'reasoning': 'Termination clauses define how and when parties can end the agreement.',
                'suggested_actions': [
                    'Identify termination triggers',
                    'Review notice requirements',
                    'Understand post-termination obligations',
                    'Consider termination fees or penalties'
                ]
            },
            'payment_info': {
                'title': 'Payment Terms Summary',
                'description': 'Key payment terms and conditions identified in the document.',
                'reasoning': 'Payment terms affect cash flow and financial planning.',
                'suggested_actions': [
                    'Note payment due dates',
                    'Review late payment penalties',
                    'Understand payment methods',
                    'Check for advance payment requirements'
                ]
            },
            'confidentiality_warning': {
                'title': 'Confidentiality Obligations',
                'description': 'This document contains confidentiality provisions that require attention.',
                'reasoning': 'Confidentiality clauses can have long-term implications for information sharing.',
                'suggested_actions': [
                    'Review confidentiality scope',
                    'Understand duration of obligations',
                    'Identify permitted disclosures',
                    'Consider return/destruction requirements'
                ]
            },
            'ip_review': {
                'title': 'Intellectual Property Review',
                'description': 'Intellectual property provisions require careful analysis.',
                'reasoning': 'IP clauses affect ownership and usage rights of creative works and innovations.',
                'suggested_actions': [
                    'Review IP ownership provisions',
                    'Understand licensing terms',
                    'Check for assignment requirements',
                    'Consider infringement protections'
                ]
            },
            'force_majeure_info': {
                'title': 'Force Majeure Provisions',
                'description': 'Force majeure clauses define circumstances for excused performance.',
                'reasoning': 'Force majeure clauses can provide relief from contractual obligations.',
                'suggested_actions': [
                    'Review covered events',
                    'Understand notice requirements',
                    'Check for mitigation obligations',
                    'Consider termination rights'
                ]
            },
            'governing_law_info': {
                'title': 'Governing Law and Jurisdiction',
                'description': 'Legal framework and dispute resolution forum specified.',
                'reasoning': 'Governing law affects how the contract will be interpreted and enforced.',
                'suggested_actions': [
                    'Note applicable law',
                    'Identify jurisdiction',
                    'Understand venue requirements',
                    'Consider enforcement implications'
                ]
            },
            'dispute_resolution_advice': {
                'title': 'Dispute Resolution Process',
                'description': 'Dispute resolution mechanisms and procedures outlined.',
                'reasoning': 'Dispute resolution clauses determine how conflicts will be resolved.',
                'suggested_actions': [
                    'Review dispute resolution steps',
                    'Understand mediation/arbitration process',
                    'Check for time limitations',
                    'Consider cost implications'
                ]
            }
        }
    
    def analyze_document_for_recommendations(self, document_text: str, 
                                           red_flags: List[Dict[str, Any]] = None,
                                           clauses: List[Dict[str, Any]] = None) -> List[LegalRecommendation]:
        """Analyze document and generate legal recommendations."""
        try:
            recommendations = []
            
            # Analyze text for legal rule triggers
            for rule_name, rule_config in self.legal_rules.items():
                if self._check_rule_triggers(document_text, rule_config['triggers']):
                    recommendation = self._create_recommendation(rule_config, rule_name)
                    recommendations.append(recommendation)
            
            # Add recommendations based on red flags
            if red_flags:
                red_flag_recommendations = self._generate_red_flag_recommendations(red_flags)
                recommendations.extend(red_flag_recommendations)
            
            # Add recommendations based on clauses
            if clauses:
                clause_recommendations = self._generate_clause_recommendations(clauses)
                recommendations.extend(clause_recommendations)
            
            # Sort by priority
            recommendations.sort(key=lambda r: self._get_priority_score(r.priority), reverse=True)
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error analyzing document for recommendations: {e}")
            return []
    
    def _check_rule_triggers(self, text: str, triggers: List[str]) -> bool:
        """Check if any triggers are present in the text."""
        text_lower = text.lower()
        return any(trigger.lower() in text_lower for trigger in triggers)
    
    def _create_recommendation(self, rule_config: Dict[str, Any], rule_name: str) -> LegalRecommendation:
        """Create recommendation from rule configuration."""
        template = self.recommendation_templates[rule_config['template']]
        
        return LegalRecommendation(
            title=template['title'],
            description=template['description'],
            recommendation_type=rule_config['type'],
            priority=rule_config['priority'],
            reasoning=template['reasoning'],
            suggested_actions=template['suggested_actions'],
            confidence=0.8
        )
    
    def _generate_red_flag_recommendations(self, red_flags: List[Dict[str, Any]]) -> List[LegalRecommendation]:
        """Generate recommendations based on red flags."""
        recommendations = []
        
        for red_flag in red_flags:
            risk_level = red_flag.get('risk_level', 'medium')
            title = red_flag.get('title', 'Unknown Risk')
            
            if risk_level in ['high', 'critical']:
                recommendation = LegalRecommendation(
                    title=f"Critical Review Required: {title}",
                    description=f"This document contains a high-risk issue: {title}",
                    recommendation_type=RecommendationType.WARNING,
                    priority=RecommendationPriority.CRITICAL if risk_level == 'critical' else RecommendationPriority.HIGH,
                    reasoning=f"High-risk issues require immediate attention and may indicate significant legal or financial exposure.",
                    suggested_actions=[
                        "Immediate legal review required",
                        "Consider contract renegotiation",
                        "Evaluate risk mitigation strategies",
                        "Consult with subject matter experts"
                    ],
                    related_red_flags=[title],
                    confidence=red_flag.get('confidence_score', 0.0) / 100.0
                )
                recommendations.append(recommendation)
        
        return recommendations
    
    def _generate_clause_recommendations(self, clauses: List[Dict[str, Any]]) -> List[LegalRecommendation]:
        """Generate recommendations based on important clauses."""
        recommendations = []
        
        for clause in clauses:
            importance = clause.get('importance', 'medium')
            clause_type = clause.get('clause_type', 'general')
            
            if importance in ['high', 'critical']:
                recommendation = LegalRecommendation(
                    title=f"Important Clause: {clause_type.title()}",
                    description=f"This document contains an important {clause_type} clause that requires attention.",
                    recommendation_type=RecommendationType.REVIEW,
                    priority=RecommendationPriority.HIGH if importance == 'high' else RecommendationPriority.CRITICAL,
                    reasoning=f"Important clauses often contain key rights, obligations, or risk allocations.",
                    suggested_actions=[
                        "Review clause language carefully",
                        "Understand implications and obligations",
                        "Consider negotiation opportunities",
                        "Document any concerns or questions"
                    ],
                    related_clauses=[clause_type],
                    confidence=clause.get('confidence_score', 0.0) / 100.0
                )
                recommendations.append(recommendation)
        
        return recommendations
    
    def _get_priority_score(self, priority: RecommendationPriority) -> int:
        """Get numerical score for priority sorting."""
        priority_scores = {
            RecommendationPriority.CRITICAL: 4,
            RecommendationPriority.HIGH: 3,
            RecommendationPriority.MEDIUM: 2,
            RecommendationPriority.LOW: 1
        }
        return priority_scores.get(priority, 0)

class QuestionBasedRecommender:
    """Generates recommendations based on specific user questions."""
    
    def __init__(self):
        """Initialize question-based recommender."""
        self.question_patterns = self._initialize_question_patterns()
    
    def _initialize_question_patterns(self) -> Dict[str, Dict[str, Any]]:
        """Initialize patterns for different question types."""
        return {
            'liability_questions': {
                'patterns': [r'liability', r'damages', r'indemnification', r'hold harmless'],
                'recommendation': {
                    'title': 'Liability Analysis Required',
                    'description': 'Your question relates to liability provisions which are critical contract terms.',
                    'type': RecommendationType.WARNING,
                    'priority': RecommendationPriority.HIGH,
                    'reasoning': 'Liability clauses determine financial exposure and legal obligations.',
                    'actions': [
                        'Review all liability-related clauses',
                        'Understand scope of indemnification',
                        'Check for liability caps or exclusions',
                        'Consider insurance requirements'
                    ]
                }
            },
            'termination_questions': {
                'patterns': [r'terminate', r'cancel', r'end', r'breach', r'default'],
                'recommendation': {
                    'title': 'Termination Rights Analysis',
                    'description': 'Your question involves termination provisions which define exit conditions.',
                    'type': RecommendationType.ADVICE,
                    'priority': RecommendationPriority.MEDIUM,
                    'reasoning': 'Termination clauses affect how and when parties can end the agreement.',
                    'actions': [
                        'Identify termination triggers',
                        'Review notice requirements',
                        'Understand post-termination obligations',
                        'Check for termination fees'
                    ]
                }
            },
            'payment_questions': {
                'patterns': [r'payment', r'invoice', r'due', r'fee', r'cost'],
                'recommendation': {
                    'title': 'Payment Terms Review',
                    'description': 'Your question relates to payment terms which affect cash flow.',
                    'type': RecommendationType.INFORMATION,
                    'priority': RecommendationPriority.MEDIUM,
                    'reasoning': 'Payment terms impact financial planning and obligations.',
                    'actions': [
                        'Review payment schedules',
                        'Note due dates and penalties',
                        'Understand payment methods',
                        'Check for advance payment requirements'
                    ]
                }
            },
            'confidentiality_questions': {
                'patterns': [r'confidential', r'secret', r'private', r'non-disclosure'],
                'recommendation': {
                    'title': 'Confidentiality Obligations',
                    'description': 'Your question involves confidentiality provisions.',
                    'type': RecommendationType.WARNING,
                    'priority': RecommendationPriority.HIGH,
                    'reasoning': 'Confidentiality clauses have long-term implications for information sharing.',
                    'actions': [
                        'Review confidentiality scope',
                        'Understand duration of obligations',
                        'Identify permitted disclosures',
                        'Check for return requirements'
                    ]
                }
            }
        }
    
    def get_question_recommendations(self, question: str, document_context: str = None) -> List[LegalRecommendation]:
        """Generate recommendations based on user question."""
        try:
            recommendations = []
            question_lower = question.lower()
            
            for pattern_name, pattern_config in self.question_patterns.items():
                if any(re.search(pattern, question_lower) for pattern in pattern_config['patterns']):
                    rec_config = pattern_config['recommendation']
                    
                    recommendation = LegalRecommendation(
                        title=rec_config['title'],
                        description=rec_config['description'],
                        recommendation_type=rec_config['type'],
                        priority=rec_config['priority'],
                        reasoning=rec_config['reasoning'],
                        suggested_actions=rec_config['actions'],
                        confidence=0.9
                    )
                    recommendations.append(recommendation)
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error generating question recommendations: {e}")
            return []

class RecommendationManager:
    """Main manager for generating and organizing recommendations."""
    
    def __init__(self):
        """Initialize recommendation manager."""
        self.rule_engine = LegalRuleEngine()
        self.question_recommender = QuestionBasedRecommender()
    
    def generate_comprehensive_recommendations(self, 
                                             document_text: str,
                                             question: str = None,
                                             red_flags: List[Dict[str, Any]] = None,
                                             clauses: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Generate comprehensive recommendations for a document."""
        try:
            recommendations = []
            
            # Document-based recommendations
            doc_recommendations = self.rule_engine.analyze_document_for_recommendations(
                document_text, red_flags, clauses
            )
            recommendations.extend(doc_recommendations)
            
            # Question-based recommendations
            if question:
                question_recommendations = self.question_recommender.get_question_recommendations(question)
                recommendations.extend(question_recommendations)
            
            # Remove duplicates and organize
            unique_recommendations = self._remove_duplicates(recommendations)
            organized_recommendations = self._organize_by_priority(unique_recommendations)
            
            return {
                'recommendations': organized_recommendations,
                'total_count': len(unique_recommendations),
                'critical_count': len([r for r in unique_recommendations if r.priority == RecommendationPriority.CRITICAL]),
                'high_count': len([r for r in unique_recommendations if r.priority == RecommendationPriority.HIGH]),
                'summary': self._generate_summary(unique_recommendations)
            }
            
        except Exception as e:
            logger.error(f"Error generating comprehensive recommendations: {e}")
            return {
                'recommendations': {},
                'total_count': 0,
                'critical_count': 0,
                'high_count': 0,
                'summary': 'Error generating recommendations'
            }
    
    def _remove_duplicates(self, recommendations: List[LegalRecommendation]) -> List[LegalRecommendation]:
        """Remove duplicate recommendations based on title."""
        seen_titles = set()
        unique_recommendations = []
        
        for rec in recommendations:
            if rec.title not in seen_titles:
                seen_titles.add(rec.title)
                unique_recommendations.append(rec)
        
        return unique_recommendations
    
    def _organize_by_priority(self, recommendations: List[LegalRecommendation]) -> Dict[str, List[Dict[str, Any]]]:
        """Organize recommendations by priority level."""
        organized = {
            'critical': [],
            'high': [],
            'medium': [],
            'low': []
        }
        
        for rec in recommendations:
            priority_key = rec.priority.value
            organized[priority_key].append({
                'title': rec.title,
                'description': rec.description,
                'type': rec.recommendation_type.value,
                'reasoning': rec.reasoning,
                'suggested_actions': rec.suggested_actions,
                'confidence': rec.confidence,
                'related_clauses': rec.related_clauses or [],
                'related_red_flags': rec.related_red_flags or []
            })
        
        return organized
    
    def _generate_summary(self, recommendations: List[LegalRecommendation]) -> str:
        """Generate summary of recommendations."""
        if not recommendations:
            return "No specific recommendations at this time."
        
        critical_count = len([r for r in recommendations if r.priority == RecommendationPriority.CRITICAL])
        high_count = len([r for r in recommendations if r.priority == RecommendationPriority.HIGH])
        
        if critical_count > 0:
            return f"⚠️ {critical_count} critical and {high_count} high-priority recommendations require immediate attention."
        elif high_count > 0:
            return f"⚠️ {high_count} high-priority recommendations should be reviewed."
        else:
            return f"📋 {len(recommendations)} recommendations for review."

# Global recommendation manager instance
recommendation_manager = RecommendationManager()
