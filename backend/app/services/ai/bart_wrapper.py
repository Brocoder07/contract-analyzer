"""
Wrapper for BART summarization model to match common interface
"""

from typing import Dict, Any
import logging
from app.core.config import Settings
from app.models.schemas import Summary
from app.services.ai.bart_summarizer import BARTSummarizer

logger = logging.getLogger(__name__)


class BARTWrapper:
    """Wrapper for BART summarization model"""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.model = BARTSummarizer(settings.SUMMARIZATION_BART_MODEL)
        logger.info(f"Initialized BARTWrapper with model: {settings.SUMMARIZATION_BART_MODEL}")
    
    def generate_summary(self, text: str) -> Summary:
        """Generate BART-based summary"""
        try:
            summary = self.model.generate_summary(
                text,
                min_length=self.settings.SUMMARY_MIN_LENGTH,
                max_length=self.settings.SUMMARY_MAX_LENGTH
            )
            return summary
        except Exception as e:
            logger.error(f"BART summarization failed: {e}")
            raise