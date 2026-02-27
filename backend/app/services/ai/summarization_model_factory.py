"""
Factory for creating summarization models based on configuration
"""

import logging
from typing import Protocol
from app.core.config import Settings, SummarizationModelType
from app.models.schemas import Summary

logger = logging.getLogger(__name__)


class SummarizationModelProtocol(Protocol):
    """Interface that all summarization models must implement"""
    
    def generate_summary(self, text: str) -> Summary:
        """Generate summary for contract text"""
        ...


class SummarizationModelFactory:
    """
    Factory for creating appropriate summarization model based on configuration
    """
    
    @staticmethod
    def create_model(settings: Settings) -> SummarizationModelProtocol:
        """
        Create and return the configured summarization model
        
        Args:
            settings: Application settings with model configuration
            
        Returns:
            Configured summarization model instance
        """
        
        model_type = settings.SUMMARIZATION_MODEL_TYPE
        
        logger.info(f"Creating summarization model: {model_type}")
        
        if model_type == SummarizationModelType.RULE_BASED:
            from app.services.ai.rule_summary_wrapper import RuleSummaryWrapper
            return RuleSummaryWrapper(settings)
        
        elif model_type == SummarizationModelType.BART:
            from app.services.ai.bart_wrapper import BARTWrapper
            return BARTWrapper(settings)
        
        elif model_type == SummarizationModelType.PEGASUS:
            from app.services.ai.pegasus_wrapper import PegasusWrapper
            return PegasusWrapper(settings)
        
        elif model_type == SummarizationModelType.T5:
            from app.services.ai.t5_summary_wrapper import T5SummaryWrapper
            return T5SummaryWrapper(settings)
        
        elif model_type == SummarizationModelType.BART_SAMSUM:
            from app.services.ai.bart_samsum_wrapper import BARTSamSumWrapper
            return BARTSamSumWrapper(settings)
        
        elif model_type == SummarizationModelType.HYBRID:
            from app.services.ai.hybrid_summarization_analyzer import HybridSummarizationAnalyzer
            return HybridSummarizationAnalyzer(settings)
        
        else:
            logger.warning(f"Unknown model type: {model_type}, defaulting to BART")
            from app.services.ai.bart_wrapper import BARTWrapper
            return BARTWrapper(settings)