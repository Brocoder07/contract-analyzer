"""
Rule-based summarization engine
Uses extractive summarization and template-based key point extraction
"""

from typing import Dict, List
import logging
from app.models.schemas import Summary
from app.services.ai.summarization_templates import (
    detect_contract_type,
    extract_parties,
    extract_dates,
    extractive_summarization,
    extract_keywords
)

logger = logging.getLogger(__name__)


class RuleSummarizer:
    """
    Rule-based contract summarizer using extractive methods
    """
    
    def __init__(self, num_sentences: int = 5):
        """
        Initialize rule-based summarizer
        
        Args:
            num_sentences: Number of sentences to extract for summary
        """
        self.num_sentences = num_sentences
        logger.info(f"Initialized RuleSummarizer with {num_sentences} sentence extraction")
    
    def generate_summary(self, text: str) -> Summary:
        """
        Generate rule-based summary of contract
        
        Args:
            text: Contract text
            
        Returns:
            Summary object
        """
        logger.info("Generating rule-based extractive summary")
        
        # Detect contract type
        contract_type = detect_contract_type(text)
        logger.debug(f"Detected contract type: {contract_type}")
        
        # Extract parties
        parties = extract_parties(text)
        logger.debug(f"Extracted {len(parties)} parties")
        
        # Extract dates
        dates = extract_dates(text)
        logger.debug(f"Extracted {len(dates)} dates")
        
        # Generate extractive summary
        summary_data = extractive_summarization(text, self.num_sentences)
        summary_text = summary_data["summary"]
        
        # Extract key points (keywords)
        keywords = extract_keywords(text, top_n=10)
        key_points = [f"Key topic: {keyword}" for keyword in keywords[:5]]
        
        # Calculate word counts
        original_words = len(text.split())
        summary_words = len(summary_text.split())
        
        return Summary(
            summary_text=summary_text,
            key_points=key_points,
            parties_involved=parties,
            important_dates=dates,
            contract_type=contract_type,
            confidence=0.85,  # Rule-based is fairly confident
            source="rule_based",
            word_count=summary_words,
            compression_ratio=summary_data["compression_ratio"]
        )