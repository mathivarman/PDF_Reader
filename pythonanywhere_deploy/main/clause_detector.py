"""
AI-Powered Clause Detection System
Detects legal clauses in documents using NLP and pattern matching.
"""

import re
import spacy
import logging
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class ClauseType(Enum):
    """Types of legal clauses."""
    TERMINATION = "termination"
    AUTO_RENEWAL = "auto_renewal"
    PENALTIES = "penalties"
    CONFIDENTIALITY = "confidentiality"
    LIABILITY = "liability"
    JURISDICTION = "jurisdiction"
    ARBITRATION = "arbitration"
    FORCE_MAJEURE = "force_majeure"
    INDEMNIFICATION = "indemnification"
    NON_COMPETE = "non_compete"
    SEVERABILITY = "severability"
    ENTIRE_AGREEMENT = "entire_agreement"
    AMENDMENT = "amendment"
    ASSIGNMENT = "assignment"
    NOTICE = "notice"
    GOVERNING_LAW = "governing_law"
    OTHER = "other"

class ImportanceLevel(Enum):
    """Importance levels for clauses."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class DetectedClause:
    """Represents a detected legal clause."""
    clause_type: ClauseType
    text: str
    start_pos: int
    end_pos: int
    confidence: float
    importance: ImportanceLevel
    page_number: int
    context: str
    reasoning: str

class ClauseDetector:
    """Main class for detecting legal clauses in documents."""
    
    def __init__(self):
        """Initialize the clause detector with spaCy model and patterns."""
        try:
            self.nlp = spacy.load("en_core_web_sm")
            logger.info("spaCy model loaded successfully")
        except OSError:
            logger.error("spaCy model not found. Please run: python -m spacy download en_core_web_sm")
            raise
        
        self.clause_patterns = self._initialize_patterns()
        self.importance_keywords = self._initialize_importance_keywords()
        
    def _initialize_patterns(self) -> Dict[ClauseType, List[Dict]]:
        """Initialize regex patterns for different clause types."""
        return {
            ClauseType.TERMINATION: [
                {
                    'pattern': r'\b(termination|terminate|terminates|terminated)\b',
                    'context_words': ['contract', 'agreement', 'effective', 'notice', 'days'],
                    'importance': ImportanceLevel.HIGH
                },
                {
                    'pattern': r'\b(terminate\s+this\s+agreement|termination\s+of\s+this\s+contract)\b',
                    'context_words': ['immediate', 'effective', 'upon', 'notice'],
                    'importance': ImportanceLevel.CRITICAL
                }
            ],
            ClauseType.AUTO_RENEWAL: [
                {
                    'pattern': r'\b(auto[\s-]?renewal|automatic\s+renewal|renew\s+automatically)\b',
                    'context_words': ['unless', 'notice', 'terminate', 'cancel', 'days'],
                    'importance': ImportanceLevel.HIGH
                },
                {
                    'pattern': r'\b(renewal\s+term|renew\s+for|extended\s+automatically)\b',
                    'context_words': ['same', 'terms', 'conditions', 'period'],
                    'importance': ImportanceLevel.MEDIUM
                }
            ],
            ClauseType.PENALTIES: [
                {
                    'pattern': r'\b(penalty|penalties|liquidated\s+damages|late\s+fee)\b',
                    'context_words': ['payment', 'breach', 'violation', 'amount', 'percent'],
                    'importance': ImportanceLevel.HIGH
                },
                {
                    'pattern': r'\b(consequences\s+of\s+breach|remedies\s+for\s+violation)\b',
                    'context_words': ['damages', 'costs', 'expenses', 'attorney'],
                    'importance': ImportanceLevel.CRITICAL
                }
            ],
            ClauseType.CONFIDENTIALITY: [
                {
                    'pattern': r'\b(confidentiality|confidential|non[\s-]?disclosure)\b',
                    'context_words': ['information', 'trade', 'secret', 'proprietary', 'private'],
                    'importance': ImportanceLevel.HIGH
                },
                {
                    'pattern': r'\b(nda|non[\s-]?disclosure\s+agreement)\b',
                    'context_words': ['obligations', 'survive', 'termination', 'years'],
                    'importance': ImportanceLevel.CRITICAL
                }
            ],
            ClauseType.LIABILITY: [
                {
                    'pattern': r'\b(liability|liable|limitation\s+of\s+liability)\b',
                    'context_words': ['damages', 'claims', 'losses', 'exclude', 'limit'],
                    'importance': ImportanceLevel.HIGH
                },
                {
                    'pattern': r'\b(disclaimer|disclaim|warranty)\b',
                    'context_words': ['implied', 'express', 'merchantability', 'fitness'],
                    'importance': ImportanceLevel.MEDIUM
                }
            ],
            ClauseType.JURISDICTION: [
                {
                    'pattern': r'\b(jurisdiction|venue|governing\s+law)\b',
                    'context_words': ['state', 'court', 'federal', 'county', 'district'],
                    'importance': ImportanceLevel.MEDIUM
                },
                {
                    'pattern': r'\b(subject\s+to\s+.*jurisdiction|exclusive\s+venue)\b',
                    'context_words': ['courts', 'state', 'federal', 'county'],
                    'importance': ImportanceLevel.HIGH
                }
            ],
            ClauseType.ARBITRATION: [
                {
                    'pattern': r'\b(arbitration|arbitrate|arbitrator)\b',
                    'context_words': ['dispute', 'resolution', 'binding', 'award'],
                    'importance': ImportanceLevel.HIGH
                },
                {
                    'pattern': r'\b(alternative\s+dispute\s+resolution|adr)\b',
                    'context_words': ['mediation', 'arbitration', 'binding', 'final'],
                    'importance': ImportanceLevel.MEDIUM
                }
            ],
            ClauseType.FORCE_MAJEURE: [
                {
                    'pattern': r'\b(force\s+majeure|act\s+of\s+god|unforeseen\s+circumstances)\b',
                    'context_words': ['natural', 'disaster', 'war', 'strike', 'beyond'],
                    'importance': ImportanceLevel.MEDIUM
                },
                {
                    'pattern': r'\b(events\s+beyond\s+control|impossible\s+to\s+perform)\b',
                    'context_words': ['reasonable', 'control', 'prevent', 'avoid'],
                    'importance': ImportanceLevel.LOW
                }
            ],
            ClauseType.INDEMNIFICATION: [
                {
                    'pattern': r'\b(indemnify|indemnification|hold\s+harmless)\b',
                    'context_words': ['damages', 'claims', 'expenses', 'defend', 'against'],
                    'importance': ImportanceLevel.HIGH
                },
                {
                    'pattern': r'\b(defend\s+and\s+indemnify|defense\s+and\s+indemnification)\b',
                    'context_words': ['claims', 'suits', 'actions', 'proceedings'],
                    'importance': ImportanceLevel.CRITICAL
                }
            ],
            ClauseType.NON_COMPETE: [
                {
                    'pattern': r'\b(non[\s-]?compete|non[\s-]?competition|restrictive\s+covenant)\b',
                    'context_words': ['employment', 'business', 'competitor', 'period', 'geographic'],
                    'importance': ImportanceLevel.HIGH
                },
                {
                    'pattern': r'\b(not\s+to\s+compete|restricted\s+from\s+competing)\b',
                    'context_words': ['directly', 'indirectly', 'similar', 'business'],
                    'importance': ImportanceLevel.CRITICAL
                }
            ],
            ClauseType.SEVERABILITY: [
                {
                    'pattern': r'\b(severability|severable|severed)\b',
                    'context_words': ['invalid', 'unenforceable', 'remain', 'effect'],
                    'importance': ImportanceLevel.MEDIUM
                },
                {
                    'pattern': r'\b(if\s+any\s+provision.*invalid|unenforceable\s+provision)\b',
                    'context_words': ['remain', 'effect', 'valid', 'enforceable'],
                    'importance': ImportanceLevel.LOW
                }
            ],
            ClauseType.ENTIRE_AGREEMENT: [
                {
                    'pattern': r'\b(entire\s+agreement|complete\s+agreement|integration)\b',
                    'context_words': ['supersede', 'replace', 'prior', 'oral', 'written'],
                    'importance': ImportanceLevel.MEDIUM
                },
                {
                    'pattern': r'\b(merger\s+clause|integration\s+clause)\b',
                    'context_words': ['entire', 'agreement', 'parties', 'supersede'],
                    'importance': ImportanceLevel.LOW
                }
            ],
            ClauseType.AMENDMENT: [
                {
                    'pattern': r'\b(amendment|amend|modification)\b',
                    'context_words': ['written', 'signed', 'parties', 'effective'],
                    'importance': ImportanceLevel.MEDIUM
                },
                {
                    'pattern': r'\b(change\s+to\s+agreement|modify\s+terms)\b',
                    'context_words': ['written', 'notice', 'consent', 'approval'],
                    'importance': ImportanceLevel.LOW
                }
            ],
            ClauseType.ASSIGNMENT: [
                {
                    'pattern': r'\b(assignment|assign|assignable)\b',
                    'context_words': ['rights', 'obligations', 'transfer', 'consent'],
                    'importance': ImportanceLevel.MEDIUM
                },
                {
                    'pattern': r'\b(not\s+assignable|prohibited\s+assignment)\b',
                    'context_words': ['without', 'consent', 'written', 'approval'],
                    'importance': ImportanceLevel.HIGH
                }
            ],
            ClauseType.NOTICE: [
                {
                    'pattern': r'\b(notice|notification|notify)\b',
                    'context_words': ['written', 'email', 'mail', 'address', 'days'],
                    'importance': ImportanceLevel.MEDIUM
                },
                {
                    'pattern': r'\b(how\s+to\s+give\s+notice|notice\s+requirements)\b',
                    'context_words': ['deliver', 'send', 'address', 'effective'],
                    'importance': ImportanceLevel.LOW
                }
            ],
            ClauseType.GOVERNING_LAW: [
                {
                    'pattern': r'\b(governing\s+law|applicable\s+law|law\s+governing)\b',
                    'context_words': ['state', 'jurisdiction', 'laws', 'statutes'],
                    'importance': ImportanceLevel.MEDIUM
                },
                {
                    'pattern': r'\b(this\s+agreement.*governed\s+by|subject\s+to.*law)\b',
                    'context_words': ['state', 'laws', 'jurisdiction', 'courts'],
                    'importance': ImportanceLevel.HIGH
                }
            ]
        }
    
    def _initialize_importance_keywords(self) -> Dict[ImportanceLevel, List[str]]:
        """Initialize keywords that indicate importance levels."""
        return {
            ImportanceLevel.CRITICAL: [
                'critical', 'essential', 'fundamental', 'vital', 'crucial',
                'termination', 'breach', 'penalty', 'damages', 'indemnification'
            ],
            ImportanceLevel.HIGH: [
                'important', 'significant', 'major', 'key', 'primary',
                'liability', 'confidentiality', 'non-compete', 'arbitration'
            ],
            ImportanceLevel.MEDIUM: [
                'standard', 'normal', 'typical', 'usual', 'regular',
                'notice', 'amendment', 'assignment', 'governing law'
            ],
            ImportanceLevel.LOW: [
                'minor', 'secondary', 'auxiliary', 'supplementary',
                'severability', 'entire agreement', 'force majeure'
            ]
        }
    
    def detect_clauses(self, text: str, page_number: int = 1) -> List[DetectedClause]:
        """
        Detect legal clauses in the given text.
        
        Args:
            text: The text to analyze
            page_number: Page number for context
            
        Returns:
            List of detected clauses
        """
        detected_clauses = []
        
        # Process text with spaCy
        doc = self.nlp(text)
        
        # Detect clauses using pattern matching
        for clause_type, patterns in self.clause_patterns.items():
            for pattern_info in patterns:
                pattern = pattern_info['pattern']
                context_words = pattern_info['context_words']
                base_importance = pattern_info['importance']
                
                # Find all matches
                matches = re.finditer(pattern, text, re.IGNORECASE)
                
                for match in matches:
                    start_pos = match.start()
                    end_pos = match.end()
                    matched_text = match.group()
                    
                    # Get context around the match
                    context_start = max(0, start_pos - 200)
                    context_end = min(len(text), end_pos + 200)
                    context = text[context_start:context_end]
                    
                    # Calculate confidence based on context
                    confidence = self._calculate_confidence(
                        matched_text, context, context_words, doc
                    )
                    
                    # Determine importance level
                    importance = self._determine_importance(
                        matched_text, context, base_importance
                    )
                    
                    # Generate reasoning
                    reasoning = self._generate_reasoning(
                        clause_type, matched_text, context, confidence
                    )
                    
                    # Create detected clause
                    clause = DetectedClause(
                        clause_type=clause_type,
                        text=matched_text,
                        start_pos=start_pos,
                        end_pos=end_pos,
                        confidence=confidence,
                        importance=importance,
                        page_number=page_number,
                        context=context,
                        reasoning=reasoning
                    )
                    
                    detected_clauses.append(clause)
        
        # Sort by confidence and importance
        detected_clauses.sort(
            key=lambda x: (x.confidence, self._importance_score(x.importance)),
            reverse=True
        )
        
        return detected_clauses
    
    def _calculate_confidence(
        self, 
        matched_text: str, 
        context: str, 
        context_words: List[str], 
        doc: spacy.tokens.Doc
    ) -> float:
        """Calculate confidence score for a detected clause."""
        confidence = 0.5  # Base confidence
        
        # Check for context words
        context_lower = context.lower()
        context_word_count = sum(1 for word in context_words if word.lower() in context_lower)
        confidence += min(0.3, context_word_count * 0.1)
        
        # Check for legal terminology
        legal_terms = ['agreement', 'contract', 'party', 'obligation', 'right', 'duty']
        legal_term_count = sum(1 for term in legal_terms if term in context_lower)
        confidence += min(0.2, legal_term_count * 0.05)
        
        # Check for sentence structure (clause-like patterns)
        if re.search(r'\b(shall|will|must|may|should)\b', context, re.IGNORECASE):
            confidence += 0.1
        
        return min(1.0, confidence)
    
    def _determine_importance(
        self, 
        matched_text: str, 
        context: str, 
        base_importance: ImportanceLevel
    ) -> ImportanceLevel:
        """Determine the importance level of a detected clause."""
        context_lower = context.lower()
        
        # Check for importance keywords
        for importance_level, keywords in self.importance_keywords.items():
            for keyword in keywords:
                if keyword.lower() in context_lower:
                    # Upgrade importance if higher keywords found
                    if self._importance_score(importance_level) > self._importance_score(base_importance):
                        return importance_level
        
        return base_importance
    
    def _importance_score(self, importance: ImportanceLevel) -> int:
        """Get numeric score for importance level."""
        scores = {
            ImportanceLevel.LOW: 1,
            ImportanceLevel.MEDIUM: 2,
            ImportanceLevel.HIGH: 3,
            ImportanceLevel.CRITICAL: 4
        }
        return scores.get(importance, 1)
    
    def _generate_reasoning(
        self, 
        clause_type: ClauseType, 
        matched_text: str, 
        context: str, 
        confidence: float
    ) -> str:
        """Generate reasoning for the detected clause."""
        reasoning_parts = []
        
        # Add clause type explanation
        reasoning_parts.append(f"Detected {clause_type.value.replace('_', ' ')} clause")
        
        # Add confidence explanation
        if confidence >= 0.8:
            reasoning_parts.append("High confidence due to strong legal context")
        elif confidence >= 0.6:
            reasoning_parts.append("Medium confidence with supporting context")
        else:
            reasoning_parts.append("Lower confidence - may need review")
        
        # Add context summary
        context_words = context.split()[:10]  # First 10 words
        reasoning_parts.append(f"Context: {' '.join(context_words)}...")
        
        return ". ".join(reasoning_parts)
    
    def get_clause_summary(self, clauses: List[DetectedClause]) -> Dict:
        """Generate a summary of detected clauses."""
        summary = {
            'total_clauses': len(clauses),
            'clauses_by_type': {},
            'clauses_by_importance': {},
            'high_confidence_clauses': 0,
            'critical_clauses': 0
        }
        
        for clause in clauses:
            # Count by type
            clause_type = clause.clause_type.value
            summary['clauses_by_type'][clause_type] = summary['clauses_by_type'].get(clause_type, 0) + 1
            
            # Count by importance
            importance = clause.importance.value
            summary['clauses_by_importance'][importance] = summary['clauses_by_importance'].get(importance, 0) + 1
            
            # Count high confidence and critical clauses
            if clause.confidence >= 0.7:
                summary['high_confidence_clauses'] += 1
            if clause.importance == ImportanceLevel.CRITICAL:
                summary['critical_clauses'] += 1
        
        return summary
