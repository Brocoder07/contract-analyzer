"""
Rule-based suggestion engine for contract risk mitigation
Uses predefined templates to generate actionable recommendations
"""

from typing import List
import logging

from app.models.schemas import RiskType, RiskLevel
from app.models.schemas import Suggestion
from app.services.ai.suggestion_templates import (
    SUGGESTION_TEMPLATES,
    get_suggestions_for_risk
)

logger = logging.getLogger(__name__)


class RuleSuggestionEngine:
    """
    Generates rule-based suggestions for contract risks using predefined templates
    """
    
    def __init__(self):
        self.templates = SUGGESTION_TEMPLATES
        logger.info(f"Initialized RuleSuggestionEngine with {len(self.templates)} risk type templates")
    
    def generate_suggestions(
        self, 
        risk_type: RiskType, 
        risk_level: RiskLevel,
        context: str
    ) -> List[Suggestion]:
        """
        Generate template-based suggestions for a detected risk
        
        Args:
            risk_type: The type of risk detected
            risk_level: The severity level of the risk (HIGH, MEDIUM, LOW)
            context: The text context where the risk was found
            
        Returns:
            List of Suggestion objects with recommendations
        """
        
        # Get templates for this risk type
        templates = get_suggestions_for_risk(risk_type)
        
        if not templates:
            logger.warning(f"No templates found for risk type: {risk_type}")
            return []
        
        suggestions = []
        
        for template in templates:
            # Calculate confidence based on risk level and template priority
            confidence = self._calculate_confidence(risk_level, template)
            
            # Create suggestion object
            suggestion = Suggestion(
                suggestion_text=template["text"],
                rationale=template["rationale"],
                confidence=confidence,
                source="rule_based",
                priority=template["priority"]
            )
            
            suggestions.append(suggestion)
        
        logger.info(f"Generated {len(suggestions)} rule-based suggestions for {risk_type}")
        return suggestions
    
    def _calculate_confidence(self, risk_level: RiskLevel, template: dict) -> float:
        """
        Calculate confidence score based on risk level and template priority
        
        Higher risk levels get higher confidence for priority 1 suggestions
        Lower priority suggestions get slightly reduced confidence
        
        Args:
            risk_level: The severity of the detected risk
            template: The suggestion template dictionary
            
        Returns:
            Confidence score between 0.0 and 1.0
        """
        
        # Base confidence scores for each risk level
        base_confidence = {
            RiskLevel.HIGH: 0.95,
            RiskLevel.MEDIUM: 0.85,
            RiskLevel.LOW: 0.75
        }
        
        # Get base confidence for this risk level
        confidence = base_confidence.get(risk_level, 0.70)
        
        # Adjust based on template priority
        priority = template.get("priority", 2)
        
        if priority == 1:
            # Priority 1 suggestions are most critical - boost confidence
            confidence = min(confidence + 0.05, 1.0)
        elif priority == 2:
            # Priority 2 suggestions are important but secondary
            confidence = confidence
        else:
            # Lower priority suggestions get reduced confidence
            confidence = max(confidence - 0.10, 0.60)
        
        return round(confidence, 2)
    
    def get_available_risk_types(self) -> List[str]:
        """
        Get list of all risk types that have suggestion templates
        
        Returns:
            List of risk type strings with templates available
        """
        return list(self.templates.keys())
    
    def has_templates_for(self, risk_type) -> bool:
        """
        Check if templates exist for a given risk type
        
        Args:
            risk_type: The risk type to check (enum or string)
            
        Returns:
            True if templates exist, False otherwise
        """
        risk_key = risk_type.value if hasattr(risk_type, 'value') else str(risk_type)
        return risk_key in self.templates and len(self.templates[risk_key]) > 0