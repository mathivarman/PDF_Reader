"""
Red-Flag Detection System
Identifies potential risks and issues in legal documents.
"""

import re
import logging
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class RiskLevel(Enum):
    """Risk levels for red flags."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class RedFlagCategory(Enum):
    """Categories of red flags."""
    FINANCIAL = "financial"
    LEGAL = "legal"
    OPERATIONAL = "operational"
    COMPLIANCE = "compliance"
    REPUTATIONAL = "reputational"
    STRATEGIC = "strategic"

@dataclass
class DetectedRedFlag:
    """Represents a detected red flag."""
    category: RedFlagCategory
    risk_level: RiskLevel
    title: str
    description: str
    text: str
    start_pos: int
    end_pos: int
    confidence: float
    page_number: int
    context: str
    recommendations: List[str]
    reasoning: str

class RedFlagDetector:
    """Main class for detecting red flags in legal documents."""
    
    def __init__(self):
        """Initialize the red flag detector with patterns and rules."""
        self.red_flag_patterns = self._initialize_patterns()
        self.risk_keywords = self._initialize_risk_keywords()
        
    def _initialize_patterns(self) -> Dict[RedFlagCategory, List[Dict]]:
        """Initialize patterns for different red flag categories."""
        return {
            RedFlagCategory.FINANCIAL: [
                {
                    'pattern': r'\b(unlimited\s+liability|unlimited\s+damages)\b',
                    'title': 'Unlimited Liability Clause',
                    'description': 'Contract contains unlimited liability provisions',
                    'risk_level': RiskLevel.CRITICAL,
                    'recommendations': [
                        'Negotiate liability caps',
                        'Add insurance requirements',
                        'Include limitation of liability clause'
                    ]
                },
                {
                    'pattern': r'\b(liquidated\s+damages.*exceed.*\d+%|penalty.*\d+%)\b',
                    'title': 'Excessive Liquidated Damages',
                    'description': 'Liquidated damages exceed reasonable amounts',
                    'risk_level': RiskLevel.HIGH,
                    'recommendations': [
                        'Negotiate lower penalty amounts',
                        'Ensure damages are reasonable',
                        'Add cure period before penalties'
                    ]
                },
                {
                    'pattern': r'\b(automatic\s+renewal.*\d+\s+years|renew.*\d+\s+years)\b',
                    'title': 'Long Auto-Renewal Period',
                    'description': 'Automatic renewal for extended periods',
                    'risk_level': RiskLevel.MEDIUM,
                    'recommendations': [
                        'Shorten renewal periods',
                        'Add termination rights',
                        'Include price escalation limits'
                    ]
                }
            ],
            RedFlagCategory.LEGAL: [
                {
                    'pattern': r'\b(waiver\s+of\s+all\s+rights|waive\s+all\s+claims)\b',
                    'title': 'Broad Rights Waiver',
                    'description': 'Contract requires waiver of all legal rights',
                    'risk_level': RiskLevel.CRITICAL,
                    'recommendations': [
                        'Limit scope of waiver',
                        'Preserve essential rights',
                        'Add carve-outs for statutory rights'
                    ]
                },
                {
                    'pattern': r'\b(exclusive\s+jurisdiction.*\d+\s+states\s+away|venue.*remote)\b',
                    'title': 'Unfavorable Jurisdiction',
                    'description': 'Jurisdiction clause favors other party',
                    'risk_level': RiskLevel.HIGH,
                    'recommendations': [
                        'Negotiate neutral jurisdiction',
                        'Consider arbitration clause',
                        'Add choice of law provisions'
                    ]
                },
                {
                    'pattern': r'\b(no\s+remedy\s+for\s+breach|exclusive\s+remedy.*limited)\b',
                    'title': 'Limited Remedies',
                    'description': 'Contract severely limits available remedies',
                    'risk_level': RiskLevel.HIGH,
                    'recommendations': [
                        'Expand available remedies',
                        'Add specific performance rights',
                        'Include injunctive relief'
                    ]
                }
            ],
            RedFlagCategory.OPERATIONAL: [
                {
                    'pattern': r'\b(immediate\s+termination|terminate\s+without\s+notice)\b',
                    'title': 'Immediate Termination Rights',
                    'description': 'Contract allows immediate termination without notice',
                    'risk_level': RiskLevel.HIGH,
                    'recommendations': [
                        'Add notice periods',
                        'Include cure periods',
                        'Define termination events'
                    ]
                },
                {
                    'pattern': r'\b(change\s+terms\s+unilaterally|modify\s+without\s+consent)\b',
                    'title': 'Unilateral Modification Rights',
                    'description': 'Other party can modify terms without consent',
                    'risk_level': RiskLevel.CRITICAL,
                    'recommendations': [
                        'Require mutual consent for changes',
                        'Add notice requirements',
                        'Include right to terminate on material changes'
                    ]
                },
                {
                    'pattern': r'\b(assign\s+without\s+consent|transfer\s+freely)\b',
                    'title': 'Unrestricted Assignment',
                    'description': 'Contract can be assigned without consent',
                    'risk_level': RiskLevel.MEDIUM,
                    'recommendations': [
                        'Add assignment restrictions',
                        'Require written consent',
                        'Include right to terminate on assignment'
                    ]
                }
            ],
            RedFlagCategory.COMPLIANCE: [
                {
                    'pattern': r'\b(comply\s+with\s+all\s+laws|regulatory\s+compliance.*unlimited)\b',
                    'title': 'Unlimited Compliance Obligations',
                    'description': 'Broad compliance requirements without limits',
                    'risk_level': RiskLevel.HIGH,
                    'recommendations': [
                        'Limit compliance scope',
                        'Add reasonable efforts standard',
                        'Include compliance cost sharing'
                    ]
                },
                {
                    'pattern': r'\b(waive\s+regulatory\s+rights|comply\s+with\s+future\s+laws)\b',
                    'title': 'Future Law Compliance',
                    'description': 'Must comply with future unknown laws',
                    'risk_level': RiskLevel.MEDIUM,
                    'recommendations': [
                        'Limit to current laws',
                        'Add materiality threshold',
                        'Include cost impact analysis'
                    ]
                },
                {
                    'pattern': r'\b(no\s+audit\s+rights|confidential\s+information.*no\s+access)\b',
                    'title': 'No Audit Rights',
                    'description': 'No right to audit or verify compliance',
                    'risk_level': RiskLevel.MEDIUM,
                    'recommendations': [
                        'Add audit rights',
                        'Include reporting requirements',
                        'Add verification procedures'
                    ]
                }
            ],
            RedFlagCategory.REPUTATIONAL: [
                {
                    'pattern': r'\b(public\s+disclosure.*negative|adverse\s+publicity)\b',
                    'title': 'Public Disclosure Risks',
                    'description': 'Contract may lead to negative publicity',
                    'risk_level': RiskLevel.MEDIUM,
                    'recommendations': [
                        'Add confidentiality provisions',
                        'Include press release controls',
                        'Add reputation protection clauses'
                    ]
                },
                {
                    'pattern': r'\b(use\s+name.*advertising|endorsement.*without\s+consent)\b',
                    'title': 'Unauthorized Use of Name',
                    'description': 'Other party can use your name without consent',
                    'risk_level': RiskLevel.HIGH,
                    'recommendations': [
                        'Require written consent',
                        'Add approval rights',
                        'Include usage guidelines'
                    ]
                }
            ],
            RedFlagCategory.STRATEGIC: [
                {
                    'pattern': r'\b(exclusive\s+relationship|non[\s-]?compete.*unlimited)\b',
                    'title': 'Overly Restrictive Exclusivity',
                    'description': 'Exclusivity provisions are too broad',
                    'risk_level': RiskLevel.HIGH,
                    'recommendations': [
                        'Limit exclusivity scope',
                        'Add reasonable restrictions',
                        'Include termination rights'
                    ]
                },
                {
                    'pattern': r'\b(technology\s+transfer.*irrevocable|perpetual\s+license)\b',
                    'title': 'Irrevocable Technology Transfer',
                    'description': 'Technology rights are irrevocable',
                    'risk_level': RiskLevel.CRITICAL,
                    'recommendations': [
                        'Add termination conditions',
                        'Include reversion rights',
                        'Limit license scope'
                    ]
                },
                {
                    'pattern': r'\b(most\s+favored\s+nation|mfn.*unlimited)\b',
                    'title': 'Broad MFN Clause',
                    'description': 'Most favored nation clause is too broad',
                    'risk_level': RiskLevel.MEDIUM,
                    'recommendations': [
                        'Limit MFN scope',
                        'Add exclusions',
                        'Include notification requirements'
                    ]
                }
            ]
        }
    
    def _initialize_risk_keywords(self) -> Dict[RiskLevel, List[str]]:
        """Initialize keywords that indicate risk levels."""
        return {
            RiskLevel.CRITICAL: [
                'unlimited', 'irrevocable', 'perpetual', 'absolute', 'total',
                'waive all', 'no rights', 'no remedies', 'no recourse'
            ],
            RiskLevel.HIGH: [
                'excessive', 'unreasonable', 'unilateral', 'immediate',
                'without notice', 'without consent', 'broad', 'sweeping'
            ],
            RiskLevel.MEDIUM: [
                'restrictive', 'limited', 'conditional', 'subject to',
                'reasonable', 'standard', 'typical', 'normal'
            ],
            RiskLevel.LOW: [
                'minor', 'minimal', 'standard', 'routine', 'usual',
                'reasonable', 'appropriate', 'adequate'
            ]
        }
    
    def detect_red_flags(self, text: str, page_number: int = 1) -> List[DetectedRedFlag]:
        """
        Detect red flags in the given text.
        
        Args:
            text: The text to analyze
            page_number: Page number for context
            
        Returns:
            List of detected red flags
        """
        detected_flags = []
        
        # Detect red flags using pattern matching
        for category, patterns in self.red_flag_patterns.items():
            for pattern_info in patterns:
                pattern = pattern_info['pattern']
                title = pattern_info['title']
                description = pattern_info['description']
                base_risk_level = pattern_info['risk_level']
                recommendations = pattern_info['recommendations']
                
                # Find all matches
                matches = re.finditer(pattern, text, re.IGNORECASE)
                
                for match in matches:
                    start_pos = match.start()
                    end_pos = match.end()
                    matched_text = match.group()
                    
                    # Get context around the match
                    context_start = max(0, start_pos - 300)
                    context_end = min(len(text), end_pos + 300)
                    context = text[context_start:context_end]
                    
                    # Calculate confidence based on context
                    confidence = self._calculate_confidence(
                        matched_text, context, base_risk_level
                    )
                    
                    # Determine risk level
                    risk_level = self._determine_risk_level(
                        matched_text, context, base_risk_level
                    )
                    
                    # Generate reasoning
                    reasoning = self._generate_reasoning(
                        category, title, matched_text, context, confidence
                    )
                    
                    # Create detected red flag
                    red_flag = DetectedRedFlag(
                        category=category,
                        risk_level=risk_level,
                        title=title,
                        description=description,
                        text=matched_text,
                        start_pos=start_pos,
                        end_pos=end_pos,
                        confidence=confidence,
                        page_number=page_number,
                        context=context,
                        recommendations=recommendations,
                        reasoning=reasoning
                    )
                    
                    detected_flags.append(red_flag)
        
        # Sort by risk level and confidence
        detected_flags.sort(
            key=lambda x: (self._risk_score(x.risk_level), x.confidence),
            reverse=True
        )
        
        return detected_flags
    
    def _calculate_confidence(
        self, 
        matched_text: str, 
        context: str, 
        base_risk_level: RiskLevel
    ) -> float:
        """Calculate confidence score for a detected red flag."""
        confidence = 0.6  # Base confidence for red flags
        
        # Check for risk keywords
        context_lower = context.lower()
        risk_keywords = self.risk_keywords.get(base_risk_level, [])
        keyword_count = sum(1 for keyword in risk_keywords if keyword.lower() in context_lower)
        confidence += min(0.3, keyword_count * 0.1)
        
        # Check for legal terminology that supports the red flag
        legal_terms = ['shall', 'will', 'must', 'obligation', 'liability', 'damages']
        legal_term_count = sum(1 for term in legal_terms if term in context_lower)
        confidence += min(0.1, legal_term_count * 0.02)
        
        return min(1.0, confidence)
    
    def _determine_risk_level(
        self, 
        matched_text: str, 
        context: str, 
        base_risk_level: RiskLevel
    ) -> RiskLevel:
        """Determine the risk level of a detected red flag."""
        context_lower = context.lower()
        
        # Check for risk keywords that might upgrade the risk level
        for risk_level, keywords in self.risk_keywords.items():
            for keyword in keywords:
                if keyword.lower() in context_lower:
                    # Upgrade risk level if higher keywords found
                    if self._risk_score(risk_level) > self._risk_score(base_risk_level):
                        return risk_level
        
        return base_risk_level
    
    def _risk_score(self, risk_level: RiskLevel) -> int:
        """Get numeric score for risk level."""
        scores = {
            RiskLevel.LOW: 1,
            RiskLevel.MEDIUM: 2,
            RiskLevel.HIGH: 3,
            RiskLevel.CRITICAL: 4
        }
        return scores.get(risk_level, 1)
    
    def _generate_reasoning(
        self, 
        category: RedFlagCategory, 
        title: str, 
        matched_text: str, 
        context: str, 
        confidence: float
    ) -> str:
        """Generate reasoning for the detected red flag."""
        reasoning_parts = []
        
        # Add category and title
        reasoning_parts.append(f"Detected {category.value} red flag: {title}")
        
        # Add confidence explanation
        if confidence >= 0.8:
            reasoning_parts.append("High confidence due to clear risk indicators")
        elif confidence >= 0.6:
            reasoning_parts.append("Medium confidence with supporting context")
        else:
            reasoning_parts.append("Lower confidence - may need review")
        
        # Add context summary
        context_words = context.split()[:15]  # First 15 words
        reasoning_parts.append(f"Context: {' '.join(context_words)}...")
        
        return ". ".join(reasoning_parts)
    
    def get_red_flag_summary(self, red_flags: List[DetectedRedFlag]) -> Dict:
        """Generate a summary of detected red flags."""
        summary = {
            'total_red_flags': len(red_flags),
            'red_flags_by_category': {},
            'red_flags_by_risk': {},
            'high_risk_flags': 0,
            'critical_flags': 0,
            'recommendations': []
        }
        
        for red_flag in red_flags:
            # Count by category
            category = red_flag.category.value
            summary['red_flags_by_category'][category] = summary['red_flags_by_category'].get(category, 0) + 1
            
            # Count by risk level
            risk_level = red_flag.risk_level.value
            summary['red_flags_by_risk'][risk_level] = summary['red_flags_by_risk'].get(risk_level, 0) + 1
            
            # Count high risk and critical flags
            if red_flag.risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]:
                summary['high_risk_flags'] += 1
            if red_flag.risk_level == RiskLevel.CRITICAL:
                summary['critical_flags'] += 1
            
            # Collect unique recommendations
            for rec in red_flag.recommendations:
                if rec not in summary['recommendations']:
                    summary['recommendations'].append(rec)
        
        return summary
