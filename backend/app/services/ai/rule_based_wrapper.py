"""
Wrapper for rule-based engine to match common interface
"""

from typing import List
import logging
from app.core.config import Settings
from app.models.schemas import Suggestion, RiskItem
from app.services.ai.rule_suggestion_engine import RuleSuggestionEngine

logger = logging.getLogger(__name__)


class RuleBasedWrapper:
    """Wrapper for rule-based engine"""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.engine = RuleSuggestionEngine()
        logger.info("Initialized RuleBasedWrapper (pure template-based)")
    
    def generate_suggestions(
        self, 
        risk_item: RiskItem,
        text_context: str
    ) -> List[Suggestion]:
        """Generate rule-based suggestions only"""
        
        suggestions = self.engine.generate_suggestions(
            risk_item.risk_type,
            risk_item.risk_level,
            text_context
        )
        
        # Limit to max results
        return suggestions[:self.settings.SUGGESTION_MAX_RESULTS]