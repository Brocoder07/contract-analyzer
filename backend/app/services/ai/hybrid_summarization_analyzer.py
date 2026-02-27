"""
Hybrid summarization analyzer - combines multiple summarization models
"""

from typing import List, Dict, Any
import time
import logging
from app.core.config import Settings
from app.models.schemas import Summary, SummaryMetadata
from app.services.ai.rule_summarizer import RuleSummarizer
from app.services.ai.bart_summarizer import BARTSummarizer
from app.services.ai.pegasus_summarizer import PegasusSummarizer
from app.services.ai.t5_summarizer import T5Summarizer
from app.services.ai.bart_samsum_summarizer import BARTSamSumSummarizer

logger = logging.getLogger(__name__)


class HybridSummarizationAnalyzer:
    """
    Combines multiple summarization models for comprehensive contract summarization
    """
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self._rule_summarizer = None
        self._bart_model = None
        self._pegasus_model = None
        self._t5_model = None
        self._bart_samsum_model = None
        logger.info("Initialized HybridSummarizationAnalyzer")
    
    @property
    def rule_summarizer(self):
        if self._rule_summarizer is None and self.settings.ENABLE_RULE_SUMMARIZATION:
            self._rule_summarizer = RuleSummarizer(
                num_sentences=self.settings.SUMMARY_EXTRACTIVE_SENTENCES
            )
        return self._rule_summarizer
    
    @property
    def bart_model(self):
        if self._bart_model is None and self.settings.ENABLE_BART_SUMMARIZATION:
            try:
                self._bart_model = BARTSummarizer(self.settings.SUMMARIZATION_BART_MODEL)
            except Exception as e:
                logger.error(f"Failed to load BART model: {e}")
        return self._bart_model
    
    @property
    def pegasus_model(self):
        if self._pegasus_model is None and self.settings.ENABLE_PEGASUS_SUMMARIZATION:
            try:
                self._pegasus_model = PegasusSummarizer(self.settings.SUMMARIZATION_PEGASUS_MODEL)
            except Exception as e:
                logger.error(f"Failed to load Pegasus model: {e}")
        return self._pegasus_model
    
    @property
    def t5_model(self):
        if self._t5_model is None and self.settings.ENABLE_T5_SUMMARIZATION:
            try:
                self._t5_model = T5Summarizer(self.settings.SUMMARIZATION_T5_MODEL)
            except Exception as e:
                logger.error(f"Failed to load T5 model: {e}")
        return self._t5_model
    
    @property
    def bart_samsum_model(self):
        if self._bart_samsum_model is None and self.settings.ENABLE_BART_SAMSUM_SUMMARIZATION:
            try:
                self._bart_samsum_model = BARTSamSumSummarizer(self.settings.SUMMARIZATION_BART_SAMSUM_MODEL)
            except Exception as e:
                logger.error(f"Failed to load BART-SAMSum model: {e}")
        return self._bart_samsum_model
    
    def generate_summary(self, text: str) -> Dict[str, Any]:
        """
        Generate summary from all enabled sources
        
        Args:
            text: Contract text to summarize
            
        Returns:
            Dict with summary and metadata
        """
        start_time = time.time()
        all_summaries = []
        models_used = []
        
        # 1. Rule-based summary
        if self.rule_summarizer:
            try:
                logger.info("Generating rule-based summary...")
                summary = self.rule_summarizer.generate_summary(text)
                all_summaries.append(summary)
                models_used.append("rule_based")
                logger.info("Rule-based summary generated")
            except Exception as e:
                logger.error(f"Rule-based summarization failed: {e}")
        
        # 2. BART summary
        if self.bart_model:
            try:
                logger.info("Generating BART summary...")
                summary = self.bart_model.generate_summary(
                    text,
                    min_length=self.settings.SUMMARY_MIN_LENGTH,
                    max_length=self.settings.SUMMARY_MAX_LENGTH
                )
                all_summaries.append(summary)
                models_used.append("bart")
                logger.info("BART summary generated")
            except Exception as e:
                logger.error(f"BART summarization failed: {e}")
        
        # 3. Pegasus summary
        if self.pegasus_model:
            try:
                logger.info("Generating Pegasus summary...")
                summary = self.pegasus_model.generate_summary(
                    text,
                    min_length=self.settings.SUMMARY_MIN_LENGTH,
                    max_length=self.settings.SUMMARY_MAX_LENGTH
                )
                all_summaries.append(summary)
                models_used.append("pegasus")
                logger.info("Pegasus summary generated")
            except Exception as e:
                logger.error(f"Pegasus summarization failed: {e}")
        
        # 4. T5 summary
        if self.t5_model:
            try:
                logger.info("Generating T5 summary...")
                summary = self.t5_model.generate_summary(
                    text,
                    min_length=self.settings.SUMMARY_MIN_LENGTH,
                    max_length=self.settings.SUMMARY_MAX_LENGTH
                )
                all_summaries.append(summary)
                models_used.append("t5")
                logger.info("T5 summary generated")
            except Exception as e:
                logger.error(f"T5 summarization failed: {e}")
        
        # 5. BART-SAMSum summary
        if self.bart_samsum_model:
            try:
                logger.info("Generating BART-SAMSum summary...")
                summary = self.bart_samsum_model.generate_summary(
                    text,
                    min_length=self.settings.SUMMARY_MIN_LENGTH,
                    max_length=self.settings.SUMMARY_MAX_LENGTH
                )
                all_summaries.append(summary)
                models_used.append("bart_samsum")
                logger.info("BART-SAMSum summary generated")
            except Exception as e:
                logger.error(f"BART-SAMSum summarization failed: {e}")
        
        if not all_summaries:
            logger.warning("No summaries generated")
            return None
        
        # 6. Fuse summaries if enabled
        if self.settings.ENABLE_SUMMARY_FUSION and len(all_summaries) > 1:
            final_summary = self._fuse_summaries(all_summaries, text)
        else:
            # Use the highest confidence summary
            final_summary = max(all_summaries, key=lambda s: s.confidence)
        
        # Calculate metadata
        processing_time = time.time() - start_time
        original_words = len(text.split())
        
        metadata = SummaryMetadata(
            total_summaries_generated=len(all_summaries),
            models_used=models_used,
            processing_time=processing_time,
            original_word_count=original_words,
            summary_word_count=final_summary.word_count,
            compression_ratio=final_summary.compression_ratio
        )
        
        logger.info(f"Hybrid summarization completed in {processing_time:.2f}s using {len(models_used)} models")
        
        return {
            "summary": final_summary,
            "metadata": metadata,
            "all_summaries": all_summaries  # Return all for comparison
        }
    
    def _fuse_summaries(self, summaries: List[Summary], original_text: str) -> Summary:
        """
        Fuse multiple summaries into one
        s
        Args:
            summaries: List of Summary objects
            original_text: Original contract text
            
        Returns:
            Fused Summary object
        """
        fusion_method = self.settings.SUMMARY_FUSION_METHOD
        
        if fusion_method == "weighted_average":
            return self._weighted_fusion(summaries, original_text)
        elif fusion_method == "voting":
            return self._voting_fusion(summaries)
        elif fusion_method == "longest":
            return max(summaries, key=lambda s: s.word_count)
        else:
            # Default: highest confidence
            return max(summaries, key=lambda s: s.confidence)
    
    def _weighted_fusion(self, summaries: List[Summary], original_text: str) -> Summary:
        """
        Combine summaries using weighted averaging based on confidence
        """
        # For now, pick the best ML summary and enhance with rule-based metadata
        ml_summaries = [s for s in summaries if s.source != "rule_based"]
        rule_summary = next((s for s in summaries if s.source == "rule_based"), None)
        
        if ml_summaries:
            best_ml = max(ml_summaries, key=lambda s: s.confidence)
        else:
            best_ml = summaries[0]
        
        # Enhance with metadata from rule-based if available
        if rule_summary:
            best_ml.key_points = rule_summary.key_points
            best_ml.parties_involved = rule_summary.parties_involved
            best_ml.important_dates = rule_summary.important_dates
            best_ml.contract_type = rule_summary.contract_type
        
        best_ml.source = "hybrid"
        best_ml.confidence = min(best_ml.confidence + 0.05, 1.0)
        
        return best_ml
    
    def _voting_fusion(self, summaries: List[Summary]) -> Summary:
        """
        Select summary using voting mechanism (most common sentences)
        For simplicity, picks highest confidence for now
        """
        return max(summaries, key=lambda s: s.confidence)