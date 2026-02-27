"""
Hybrid risk analyzer combining rule-based and ML approaches with suggestion generation and summarization
"""

from typing import List, Dict, Any
import time
import logging

from app.services.ai.rule_engine import RuleEngine
from app.services.ai.ml_model import MLModel
from app.services.ai.custom_ml_model import CustomMLModel
from app.services.ai.suggestion_model_factory import SuggestionModelFactory
from app.services.ai.summarization_model_factory import SummarizationModelFactory
from app.models.schemas import RiskItem, RiskLevel, RiskType
from app.core.config import Settings

logger = logging.getLogger(__name__)


class HybridRiskAnalyzer:
    """
    Hybrid risk analyzer combining rule-based and ML approaches with spaCy
    Now includes AI-powered suggestion generation and contract summarization
    """
    
    def __init__(
        self, 
        rule_config_path: str, 
        ml_model_path: str, 
        settings: Settings,
        model_choice: str = "contracts_bert"
    ):
        self.rule_config_path = rule_config_path
        self.ml_model_path = ml_model_path
        self.model_choice = model_choice
        self.settings = settings
        
        # Risk detection components
        self.rule_engine = RuleEngine(rule_config_path)

        # Choose ML back-end: custom multi-task model takes priority when selected
        if model_choice == "custom":
            self.ml_model = CustomMLModel(settings.CUSTOM_MODEL_PATH)
            self.custom_model: CustomMLModel | None = self.ml_model  # type: ignore[assignment]
        else:
            self.ml_model = MLModel(ml_model_path, model_choice)
            self.custom_model = None
        
        # Suggestion generation component
        self._suggestion_model = None
        
        # NEW: Summarization component
        self._summarization_model = None
        
        self._models_loaded = False
        
    def load_models(self):
        """Lazy loading of models"""
        if not self._models_loaded:
            logger.info("🔄 Loading AI models...")
            self.rule_engine.load_rules()
            self.ml_model.load()
            self._models_loaded = True
            model_label = "CustomMLModel (MiniLM + CUAD)" if self.custom_model else f"MLModel ({self.model_choice})"
            logger.info(f"✅ All AI models loaded — ML back-end: {model_label}")
    
    @property
    def suggestion_model(self):
        """Lazy load suggestion model based on configuration"""
        if self._suggestion_model is None:
            logger.info("🔄 Loading suggestion generation model...")
            self._suggestion_model = SuggestionModelFactory.create_model(self.settings)
            logger.info("✅ Suggestion model loaded successfully")
        return self._suggestion_model
    
    @property
    def summarization_model(self):
        """Lazy load summarization model based on configuration"""
        if self._summarization_model is None:
            logger.info("🔄 Loading summarization model...")
            self._summarization_model = SummarizationModelFactory.create_model(self.settings)
            logger.info("✅ Summarization model loaded successfully")
        return self._summarization_model
    
    def analyze_contract(
        self, 
        text: str, 
        generate_suggestions: bool = True,
        generate_summary: bool = True
    ) -> Dict[str, Any]:
        start_time = time.time()
        
        # Ensure models are loaded
        t = time.time()
        self.load_models()
        print(f"[⏱ TIMER] model load/check:       {time.time()-t:.3f}s")

        print(f"\n{'='*60}")
        print(f"[🔍 ANALYSIS START] {len(text)} chars")
        print(f"{'='*60}")

        # Rule engine
        t = time.time()
        rule_risks = self.rule_engine.analyze(text)
        print(f"[⏱ TIMER] rule engine:            {time.time()-t:.3f}s  → {len(rule_risks)} risks")

        # ML model (sentence-by-sentence — usually the slow part)
        t = time.time()
        ml_risks = self.ml_model.analyze(text)
        print(f"[⏱ TIMER] ml model:               {time.time()-t:.3f}s  → {len(ml_risks)} risks")

        # Merge
        t = time.time()
        all_risks = self._merge_risks(rule_risks + ml_risks)
        print(f"[⏱ TIMER] merge/dedup:            {time.time()-t:.3f}s  → {len(all_risks)} final risks")

        
        # Generate suggestions for each risk
        if generate_suggestions and all_risks:
            logger.info("💡 Generating mitigation suggestions...")
            suggestion_start = time.time()
            
            for i, risk in enumerate(all_risks):
                t = time.time()
                try:
                    suggestions = self.suggestion_model.generate_suggestions(
                        risk, 
                        text
                    )
                    risk.suggestions = suggestions
                    risk.best_suggestion = suggestions[0] if suggestions else None
                    print(f"[⏱ TIMER] suggestion [{i+1}/{len(all_risks)}] {risk.risk_type.value[:30]:<30} {time.time()-t:.3f}s")
                except Exception as e:
                    logger.error(f"Suggestion generation failed for risk {risk.id}: {e}")
                    risk.suggestions = []
                    risk.best_suggestion = None
            
            suggestion_time = time.time() - suggestion_start
            print(f"[⏱ TIMER] suggestions total:      {suggestion_time:.3f}s")
        
        # NEW: Generate contract summary
        summary = None
        summary_metadata = None
        if generate_summary:
            logger.info("📝 Generating contract summary...")
            summary_start = time.time()
            
            try:
                summary_result = self.summarization_model.generate_summary(text)
                
                # Handle both hybrid and single model responses
                if isinstance(summary_result, dict):
                    summary = summary_result.get("summary")
                    summary_metadata = summary_result.get("metadata")
                else:
                    summary = summary_result
                
                summary_time = time.time() - summary_start
                print(f"[⏱ TIMER] summarization:          {summary_time:.3f}s")
            except Exception as e:
                logger.error(f"Summary generation failed: {e}")
                summary = None
                summary_metadata = None
        
        # Calculate overall metrics
        processing_time = time.time() - start_time
        risk_score = self._calculate_risk_score(all_risks)
        risk_level = self._get_risk_level(risk_score)
        
        print(f"[⏱ TIMER] TOTAL:                  {processing_time:.3f}s")
        print(f"{'='*60}\n")
        
        return {
            "risks": all_risks,
            "overall_risk_score": risk_score,
            "risk_level": risk_level,
            "total_risks_found": len(all_risks),
            "processing_time": processing_time,
            "suggestion_model_type": self.settings.SUGGESTION_MODEL_TYPE if generate_suggestions else None,
            "summary": summary,
            "summary_metadata": summary_metadata,
            "document_metadata": {
                "text_length": len(text),
                "paragraphs_count": text.count('\n\n') + 1,
                "sentences_count": len(list(self.ml_model.nlp(text).sents))
            }
        }
    
    def _merge_risks(self, risks: List[RiskItem]) -> List[RiskItem]:
        """
        Merge and deduplicate risks from different detectors using position information
        """
        if not risks:
            return []
        
        merged_risks = []
        seen_positions = set()
        
        for risk in risks:
            # Create position signature
            pos_signature = f"{risk.start_pos}:{risk.end_pos}"
            
            if pos_signature not in seen_positions:
                seen_positions.add(pos_signature)
                merged_risks.append(risk)
            else:
                # Update existing risk if this one has higher confidence
                for existing_risk in merged_risks:
                    existing_signature = f"{existing_risk.start_pos}:{existing_risk.end_pos}"
                    if existing_signature == pos_signature and risk.confidence > existing_risk.confidence:
                        existing_risk.confidence = risk.confidence
                        existing_risk.detector = f"combined_{risk.detector}"
        
        return merged_risks
    
    def _calculate_risk_score(self, risks: List[RiskItem]) -> float:
        """
        Calculate overall risk score 0-1 with weighted average
        """
        if not risks:
            return 0.0
        
        risk_weights = {
            RiskLevel.HIGH: 1.0,
            RiskLevel.MEDIUM: 0.6, 
            RiskLevel.LOW: 0.3,
            RiskLevel.NONE: 0.0
        }
        
        # Weighted average considering both risk level and confidence
        weighted_sum = 0.0
        total_weight = 0.0
        
        for risk in risks:
            weight = risk_weights.get(risk.risk_level, 0.3)
            weighted_value = weight * risk.confidence
            weighted_sum += weighted_value
            total_weight += weight
        
        if total_weight == 0:
            return 0.0
        
        return min(weighted_sum / total_weight, 1.0)
    
    def _get_risk_level(self, score: float) -> RiskLevel:
        """
        Convert numeric score to risk level
        """
        if score >= 0.7:
            return RiskLevel.HIGH
        elif score >= 0.4:
            return RiskLevel.MEDIUM
        elif score >= 0.1:
            return RiskLevel.LOW
        else:
            return RiskLevel.NONE
    
    def regenerate_suggestions_for_risk(
        self, 
        risk: RiskItem, 
        text_context: str = ""
    ) -> List:
        """
        Regenerate suggestions for a specific risk
        """
        try:
            suggestions = self.suggestion_model.generate_suggestions(risk, text_context)
            logger.info(f"Regenerated {len(suggestions)} suggestions for risk {risk.id}")
            return suggestions
        except Exception as e:
            logger.error(f"Failed to regenerate suggestions: {e}")
            return []
    
    def regenerate_summary(self, text: str) -> Dict[str, Any]:
        """
        Regenerate contract summary
        
        Args:
            text: Contract text
            
        Returns:
            Summary and metadata
        """
        try:
            summary_result = self.summarization_model.generate_summary(text)
            logger.info("Regenerated contract summary")
            return summary_result if isinstance(summary_result, dict) else {"summary": summary_result}
        except Exception as e:
            logger.error(f"Failed to regenerate summary: {e}")
            return None
    
    def get_suggestion_stats(self, risks: List[RiskItem]) -> Dict[str, Any]:
        """
        Get statistics about generated suggestions
        """
        total_suggestions = 0
        suggestions_by_source = {"rule_based": 0, "t5_model": 0, "gpt_model": 0}
        risks_with_suggestions = 0
        avg_confidence = 0.0
        
        for risk in risks:
            if risk.suggestions:
                risks_with_suggestions += 1
                total_suggestions += len(risk.suggestions)
                
                for suggestion in risk.suggestions:
                    suggestions_by_source[suggestion.source] = suggestions_by_source.get(suggestion.source, 0) + 1
                    avg_confidence += suggestion.confidence
        
        if total_suggestions > 0:
            avg_confidence /= total_suggestions
        
        return {
            "total_suggestions": total_suggestions,
            "risks_with_suggestions": risks_with_suggestions,
            "risks_without_suggestions": len(risks) - risks_with_suggestions,
            "suggestions_by_source": suggestions_by_source,
            "average_confidence": round(avg_confidence, 2),
            "suggestions_per_risk": round(total_suggestions / len(risks), 2) if risks else 0
        }