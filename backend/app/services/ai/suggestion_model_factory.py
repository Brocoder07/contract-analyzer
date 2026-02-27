"""
Factory for creating suggestion models based on configuration
"""

import logging
from typing import Protocol, List
from app.core.config import Settings, SuggestionModelType
from app.models.schemas import Suggestion, RiskItem

logger = logging.getLogger(__name__)


class SuggestionModelProtocol(Protocol):
    """Interface that all suggestion models must implement"""
    
    def generate_suggestions(
        self, 
        risk_item: RiskItem,
        text_context: str
    ) -> List[Suggestion]:
        """Generate suggestions for a risk item"""
        ...


class SuggestionModelFactory:
    """
    Factory for creating appropriate suggestion model based on configuration
    """
    
    @staticmethod
    def create_model(settings: Settings) -> SuggestionModelProtocol:
        """
        Create and return the configured suggestion model
        
        Args:
            settings: Application settings with model configuration
            
        Returns:
            Configured suggestion model instance
        """
        
        model_type = settings.SUGGESTION_MODEL_TYPE
        
        logger.info(f"Creating suggestion model: {model_type}")
        
        if model_type == SuggestionModelType.RULE_BASED:
            from app.services.ai.rule_based_wrapper import RuleBasedWrapper
            return RuleBasedWrapper(settings)
        
        elif model_type == SuggestionModelType.T5:
            from app.services.ai.t5_wrapper import T5Wrapper
            return T5Wrapper(settings)
        
        elif model_type == SuggestionModelType.GPT:
            from app.services.ai.gpt_wrapper import GPTWrapper
            return GPTWrapper(settings)
        
        elif model_type == SuggestionModelType.HYBRID:
            from app.services.ai.hybrid_suggestion_analyzer import HybridSuggestionAnalyzer
            return HybridSuggestionAnalyzer(settings)
        
        else:
            logger.warning(f"Unknown model type: {model_type}, defaulting to HYBRID")
            from app.services.ai.hybrid_suggestion_analyzer import HybridSuggestionAnalyzer
            return HybridSuggestionAnalyzer(settings)