from typing import List, Dict, Any
import time
from app.services.ai.rule_engine import RuleEngine
from app.services.ai.ml_model import MLModel
from app.models.schemas import RiskItem, RiskLevel, RiskType

class HybridRiskAnalyzer:
    """
    Hybrid risk analyzer combining rule-based and ML approaches with spaCy
    """
    
    def __init__(self, rule_config_path: str, ml_model_path: str, model_choice: str = "contracts_bert"):
        self.rule_config_path = rule_config_path
        self.ml_model_path = ml_model_path
        self.model_choice = model_choice
        self.rule_engine = RuleEngine(rule_config_path)
        self.ml_model = MLModel(ml_model_path, model_choice)
        self._models_loaded = False
        
    def load_models(self):
        """Lazy loading of models"""
        if not self._models_loaded:
            print("🔄 Loading AI models...")
            self.rule_engine.load_rules()
            self.ml_model.load()
            self._models_loaded = True
            print("✅ All AI models loaded successfully")
    
    def analyze_contract(self, text: str) -> Dict[str, Any]:
        """
        Analyze contract text for risks using hybrid approach
        """
        start_time = time.time()
        
        # Ensure models are loaded
        self.load_models()
        
        print(f"📄 Analyzing contract text ({len(text)} characters)")
        
        # Run both analyzers
        rule_risks = self.rule_engine.analyze(text)
        ml_risks = self.ml_model.analyze(text)
        
        print(f"🔍 Rule-based found {len(rule_risks)} risks")
        print(f"🤖 ML model found {len(ml_risks)} risks")
        
        # Merge and deduplicate results
        all_risks = self._merge_risks(rule_risks + ml_risks)
        
        # Calculate overall metrics
        processing_time = time.time() - start_time
        risk_score = self._calculate_risk_score(all_risks)
        risk_level = self._get_risk_level(risk_score)
        
        print(f"✅ Analysis completed: {len(all_risks)} total risks found, score: {risk_score:.2f}")
        
        return {
            "risks": all_risks,
            "overall_risk_score": risk_score,
            "risk_level": risk_level,
            "total_risks_found": len(all_risks),
            "processing_time": processing_time,
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