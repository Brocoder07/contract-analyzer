"""
Wrapper for GPT model to match common interface
"""

from typing import List
import logging
from app.core.config import Settings
from app.models.schemas import Suggestion, RiskItem
from app.services.ai.gpt_suggestion_model import GPTSuggestionModel

logger = logging.getLogger(__name__)


class GPTWrapper:
    """Wrapper for GPT generative model"""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.model = GPTSuggestionModel(settings.SUGGESTION_GPT_MODEL)
        logger.info(f"Initialized GPTWrapper with model: {settings.SUGGESTION_GPT_MODEL}")
    
    def generate_suggestions(
        self, 
        risk_item: RiskItem,
        text_context: str
    ) -> List[Suggestion]:
        """Generate GPT-based suggestions only"""
        
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
                logger.warning(f"GPT suggestion below confidence threshold: {suggestion.confidence}")
                return []
                
        except Exception as e:
            logger.error(f"GPT generation failed: {e}")
            return []