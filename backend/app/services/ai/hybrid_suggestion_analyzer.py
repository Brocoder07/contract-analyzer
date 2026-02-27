"""
Hybrid suggestion analyzer - combines multiple models
"""

from typing import List
import logging
from app.core.config import Settings
from app.models.schemas import Suggestion, RiskItem
from app.services.ai.rule_suggestion_engine import RuleSuggestionEngine
from app.services.ai.t5_suggestion_model import T5SuggestionModel
from app.services.ai.gpt_suggestion_model import GPTSuggestionModel
from app.services.ai.deduplicator import SuggestionDeduplicator  # ✅ NOW IMPORTED

logger = logging.getLogger(__name__)


class HybridSuggestionAnalyzer:
    """Combines rule-based, T5, and GPT models for comprehensive suggestions"""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self._rule_engine = None
        self._t5_model = None
        self._gpt_model = None
        self._deduplicator = None
        logger.info("Initialized HybridSuggestionAnalyzer")
    
    @property
    def rule_engine(self):
        if self._rule_engine is None and self.settings.ENABLE_RULE_SUGGESTIONS:
            self._rule_engine = RuleSuggestionEngine()
        return self._rule_engine
    
    @property
    def t5_model(self):
        if self._t5_model is None and self.settings.ENABLE_T5_SUGGESTIONS:
            try:
                self._t5_model = T5SuggestionModel(self.settings.SUGGESTION_T5_MODEL)
            except Exception as e:
                logger.error(f"Failed to load T5 model: {e}")
        return self._t5_model
    
    @property
    def gpt_model(self):
        if self._gpt_model is None and self.settings.ENABLE_GPT_SUGGESTIONS:
            try:
                self._gpt_model = GPTSuggestionModel(self.settings.SUGGESTION_GPT_MODEL)
            except Exception as e:
                logger.error(f"Failed to load GPT model: {e}")
        return self._gpt_model
    
    @property
    def deduplicator(self):
        if self._deduplicator is None and self.settings.ENABLE_SUGGESTION_DEDUPLICATION:
            self._deduplicator = SuggestionDeduplicator(
                self.settings.DEDUPLICATION_SIMILARITY_THRESHOLD
            )
        return self._deduplicator
    
    def generate_suggestions(
        self, 
        risk_item: RiskItem,
        text_context: str
    ) -> List[Suggestion]:
        """Generate suggestions from all enabled sources"""
        
        all_suggestions = []
        
        # 1. Rule-based suggestions
        if self.rule_engine:
            try:
                rule_suggestions = self.rule_engine.generate_suggestions(
                    risk_item.risk_type,
                    risk_item.risk_level,
                    text_context
                )
                all_suggestions.extend(rule_suggestions)
                logger.info(f"Added {len(rule_suggestions)} rule-based suggestions")
            except Exception as e:
                logger.error(f"Rule engine failed: {e}")
        
        # 2. T5 model suggestions
        if self.t5_model:
            try:
                t5_suggestion = self.t5_model.generate_suggestion(
                    risk_item.text,
                    risk_item.risk_type.value,
                    self.settings.SUGGESTION_MAX_LENGTH
                )
                if t5_suggestion.confidence >= self.settings.SUGGESTION_MIN_CONFIDENCE:
                    all_suggestions.append(t5_suggestion)
                    logger.info("Added T5 suggestion")
            except Exception as e:
                logger.error(f"T5 model failed: {e}")
        
        # 3. GPT model suggestions
        if self.gpt_model:
            try:
                gpt_suggestion = self.gpt_model.generate_suggestion(
                    risk_item.text,
                    risk_item.risk_type.value,
                    self.settings.SUGGESTION_MAX_LENGTH
                )
                if gpt_suggestion.confidence >= self.settings.SUGGESTION_MIN_CONFIDENCE:
                    all_suggestions.append(gpt_suggestion)
                    logger.info("Added GPT suggestion")
            except Exception as e:
                logger.error(f"GPT model failed: {e}")
        
        # 4. Deduplicate if enabled ✅ NOW FUNCTIONAL
        if self.deduplicator and all_suggestions:
            all_suggestions = self.deduplicator.deduplicate(all_suggestions)
        
        # 5. Rank suggestions
        ranked = self._rank_suggestions(all_suggestions)
        
        # 6. Return top N
        return ranked[:self.settings.SUGGESTION_MAX_RESULTS]
    
    def _rank_suggestions(self, suggestions: List[Suggestion]) -> List[Suggestion]:
        """Rank by confidence * priority weight"""
        return sorted(
            suggestions,
            key=lambda s: (s.confidence * (1 / s.priority)),
            reverse=True
        )