"""
Wrapper for T5 model to match common interface
"""

from typing import List
import logging
from app.core.config import Settings
from app.models.schemas import Suggestion, RiskItem
from app.services.ai.t5_suggestion_model import T5SuggestionModel

logger = logging.getLogger(__name__)


class T5Wrapper:
    """Wrapper for T5 generative model"""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.model = T5SuggestionModel(settings.SUGGESTION_T5_MODEL)
        logger.info(f"Initialized T5Wrapper with model: {settings.SUGGESTION_T5_MODEL}")
    
    def generate_suggestions(
        self, 
        risk_item: RiskItem,
        text_context: str
    ) -> List[Suggestion]:
        """Generate T5-based suggestions only"""
        
        try:
            suggestion = self.model.generate_suggestion(
                risk_item.text,
                risk_item.risk_type.value,
                self.settings.SUGGESTION_MAX_LENGTH
            )
            
            # Filter by minimum confidence
            if suggestion.confidence >= self.settings.SUGGESTION_MIN_CONFIDENCE:
                return [suggestion]
            else:
                logger.warning(f"T5 suggestion below confidence threshold: {suggestion.confidence}")
                return []
                
        except Exception as e:
            logger.error(f"T5 generation failed: {e}")
            return []