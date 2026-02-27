"""
Wrapper for Pegasus summarization model
"""

from typing import Dict, Any
import logging
from app.core.config import Settings
from app.models.schemas import Summary
from app.services.ai.pegasus_summarizer import PegasusSummarizer

logger = logging.getLogger(__name__)


class PegasusWrapper:
    """Wrapper for Pegasus summarization model"""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.model = PegasusSummarizer(settings.SUMMARIZATION_PEGASUS_MODEL)
        logger.info(f"Initialized PegasusWrapper with model: {settings.SUMMARIZATION_PEGASUS_MODEL}")
    
    def generate_summary(self, text: str) -> Summary:
        """Generate Pegasus-based summary"""
        try:
            summary = self.model.generate_summary(
                text,
                min_length=self.settings.SUMMARY_MIN_LENGTH,
                max_length=self.settings.SUMMARY_MAX_LENGTH
            )
            return summary
        except Exception as e:
            logger.error(f"Pegasus summarization failed: {e}")
            raise