"""
Wrapper for BART-SAMSum summarization model
"""

from typing import Dict, Any
import logging
from app.core.config import Settings
from app.models.schemas import Summary
from app.services.ai.bart_samsum_summarizer import BARTSamSumSummarizer

logger = logging.getLogger(__name__)


class BARTSamSumWrapper:
    """Wrapper for BART-SAMSum summarization model"""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.model = BARTSamSumSummarizer(settings.SUMMARIZATION_BART_SAMSUM_MODEL)
        logger.info(f"Initialized BARTSamSumWrapper with model: {settings.SUMMARIZATION_BART_SAMSUM_MODEL}")
    
    def generate_summary(self, text: str) -> Summary:
        """Generate BART-SAMSum-based summary"""
        try:
            summary = self.model.generate_summary(
                text,
                min_length=self.settings.SUMMARY_MIN_LENGTH,
                max_length=self.settings.SUMMARY_MAX_LENGTH
            )
            return summary
        except Exception as e:
            logger.error(f"BART-SAMSum summarization failed: {e}")
            raise