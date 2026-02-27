"""
Wrapper for T5 summarization model
"""

from typing import Dict, Any
import logging
from app.core.config import Settings
from app.models.schemas import Summary
from app.services.ai.t5_summarizer import T5Summarizer

logger = logging.getLogger(__name__)


class T5SummaryWrapper:
    """Wrapper for T5 summarization model"""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.model = T5Summarizer(settings.SUMMARIZATION_T5_MODEL)
        logger.info(f"Initialized T5SummaryWrapper with model: {settings.SUMMARIZATION_T5_MODEL}")
    
    def generate_summary(self, text: str) -> Summary:
        """Generate T5-based summary"""
        try:
            summary = self.model.generate_summary(
                text,
                min_length=self.settings.SUMMARY_MIN_LENGTH,
                max_length=self.settings.SUMMARY_MAX_LENGTH
            )
            return summary
        except Exception as e:
            logger.error(f"T5 summarization failed: {e}")
            raise