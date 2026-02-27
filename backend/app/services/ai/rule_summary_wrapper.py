"""
Wrapper for rule-based summarization
"""

from typing import Dict, Any
import logging
from app.core.config import Settings
from app.models.schemas import Summary
from app.services.ai.rule_summarizer import RuleSummarizer

logger = logging.getLogger(__name__)


class RuleSummaryWrapper:
    """Wrapper for rule-based extractive summarization"""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.model = RuleSummarizer(
            num_sentences=settings.SUMMARY_EXTRACTIVE_SENTENCES
        )
        logger.info("Initialized RuleSummaryWrapper (extractive summarization)")
    
    def generate_summary(self, text: str) -> Summary:
        """Generate rule-based extractive summary"""
        try:
            summary = self.model.generate_summary(text)
            return summary
        except Exception as e:
            logger.error(f"Rule-based summarization failed: {e}")
            raise