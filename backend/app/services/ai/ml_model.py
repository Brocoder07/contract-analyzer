from typing import List, Dict, Any
import os
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
import spacy
from app.models.schemas import RiskItem, RiskLevel, RiskType

class MLModel:
    """
    ML-based contract risk detector with spaCy integration
    """
    
    def __init__(self, model_path: str):
        self.model_path = model_path
        self.tokenizer = None
        self.model = None
        self.nlp = None
        self.device = None
        self._loaded = False
        
        # Label mapping for risk types
        self.label_mapping = {
            0: {"risk_type": RiskType.AUTO_RENEWAL, "risk_level": RiskLevel.HIGH},
            1: {"risk_type": RiskType.LIABILITY, "risk_level": RiskLevel.MEDIUM},
            2: {"risk_type": RiskType.TERMINATION, "risk_level": RiskLevel.MEDIUM},
            3: {"risk_type": RiskType.IP_OWNERSHIP, "risk_level": RiskLevel.HIGH},
            4: {"risk_type": "safe", "risk_level": RiskLevel.NONE}
        }
    
    def load(self):
        """Load the ML model, tokenizer, and spaCy"""
        try:
            # Load spaCy for sentence segmentation
            self.nlp = spacy.load("en_core_web_sm")
            
            # For now, we'll use a placeholder since we don't have a trained model
            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
            print(f"✅ Using device: {self.device}")
            
            # Placeholder - using a small model for demonstration
            model_name = "distilbert-base-uncased"
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.model = AutoModelForSequenceClassification.from_pretrained(
                model_name,
                num_labels=5
            )
            self.model.to(self.device)
            self.model.eval()
            
            self._loaded = True
            print("✅ ML model components loaded successfully")
            
        except Exception as e:
            print(f"❌ Failed to load ML model: {e}")
            self._loaded = False
    
    def analyze(self, text: str) -> List[RiskItem]:
        """Analyze text using ML model with spaCy sentence segmentation"""
        if not self._loaded:
            return []  # Return empty if model not loaded
        
        risks = []
        
        try:
            # Use spaCy for accurate sentence segmentation
            doc = self.nlp(text)
            
            for sent in doc.sents:
                sentence_text = sent.text.strip()
                if len(sentence_text) < 15:  # Skip very short sentences
                    continue
                    
                prediction = self._predict_sentence(sentence_text)
                
                if prediction and prediction["label"] != 4 and prediction["confidence"] > 0.5:  # Not "safe" and confident
                    label_info = self.label_mapping[prediction["label"]]
                    
                    risk_item = RiskItem(
                        risk_type=label_info["risk_type"],
                        text=sentence_text,
                        description=f"AI-detected {label_info['risk_type'].value} risk",
                        suggestion="Review this clause with legal counsel",
                        risk_level=label_info["risk_level"],
                        confidence=prediction["confidence"],
                        start_pos=sent.start_char,
                        end_pos=sent.end_char,
                        detector="ml_model"
                    )
                    risks.append(risk_item)
                    
        except Exception as e:
            print(f"❌ ML analysis failed: {e}")
        
        return risks
    
    def _predict_sentence(self, text: str) -> Dict[str, Any]:
        """Smarter mock prediction based on keyword matching"""
        try:
            # Improved keyword-based mock prediction
            confidence_scores = self._smart_mock_prediction(text)
            predicted_class = confidence_scores.index(max(confidence_scores))
            confidence = max(confidence_scores)
            
            # Only return if confidence is reasonable
            if confidence > 0.3:
                return {
                    "label": predicted_class,
                    "confidence": confidence
                }
            else:
                return {
                    "label": 4,  # safe
                    "confidence": 0.9
                }
            
        except Exception as e:
            print(f"❌ Sentence prediction failed: {e}")
            return None
    
    def _smart_mock_prediction(self, text: str) -> List[float]:
        """Smarter mock confidence prediction based on keyword context"""
        text_lower = text.lower()
        
        # Base scores - bias toward "safe"
        scores = [0.1, 0.1, 0.1, 0.1, 0.6]  # Higher base for "safe"
        
        # Auto-renewal detection
        auto_renewal_terms = ["auto renew", "automatic renewal", "auto-renew", "perpetual renew"]
        if any(term in text_lower for term in auto_renewal_terms):
            if any(day in text_lower for day in ["1 day", "24 hour", "48 hour"]):
                scores[0] = 0.9  # High confidence for short renewal periods
            else:
                scores[0] = 0.7  # Medium confidence for auto-renewal in general
        
        # Liability detection
        liability_terms = ["liability limit", "maximum liability", "cap on liability"]
        if any(term in text_lower for term in liability_terms):
            if any(amount in text_lower for amount in ["$1000", "$500", "$100"]):
                scores[1] = 0.8  # High confidence for low amounts
            else:
                scores[1] = 0.5  # Medium confidence for liability mentions
        
        # Termination detection
        termination_terms = ["termination", "terminate", "cancel"]
        if any(term in text_lower for term in termination_terms):
            if any(short in text_lower for short in ["7 day", "5 day", "10 day"]):
                scores[2] = 0.8  # High confidence for short notice
            else:
                scores[2] = 0.4  # Low confidence for termination mentions
        
        # IP Ownership detection
        ip_terms = ["intellectual property", "inventions", "work product", "ip ownership"]
        if any(term in text_lower for term in ip_terms):
            if "belong to" in text_lower or "exclusively" in text_lower:
                scores[3] = 0.9  # High confidence for broad IP claims
            else:
                scores[3] = 0.6  # Medium confidence for IP mentions
        
        # Normalize scores
        total = sum(scores)
        if total > 0:
            scores = [score / total for score in scores]
        
        return scores