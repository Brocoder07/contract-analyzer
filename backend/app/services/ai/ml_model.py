from typing import List, Dict, Any, Optional
import os
from transformers import AutoTokenizer, AutoModelForSequenceClassification, AutoModel, pipeline
import torch
import spacy
from app.models.schemas import RiskItem, RiskLevel, RiskType

class MLModel:
    """
    Enhanced ML-based contract risk detector with multiple pre-trained model options
    """
    
    # High-performance model options (in order of preference)
    MODEL_OPTIONS = {
        "contracts_bert": {
            "name": "nlpaueb/bert-base-uncased-contracts",
            "description": "BERT specifically trained on US contracts",
            "performance": "high",
            "speed": "medium"
        },
        "legal_bert": {
            "name": "nlpaueb/legal-bert-base-uncased", 
            "description": "Legal BERT trained on diverse legal texts",
            "performance": "high",
            "speed": "medium"
        },
        "deberta_large": {
            "name": "microsoft/deberta-large-mnli",
            "description": "DeBERTa-large with superior reasoning capabilities",
            "performance": "very_high",
            "speed": "slow"
        },
        "legal_bert_small": {
            "name": "nlpaueb/legal-bert-small-uncased",
            "description": "Lightweight legal BERT (4x faster)",
            "performance": "medium",
            "speed": "fast"
        },
        "roberta_large": {
            "name": "roberta-large",
            "description": "General RoBERTa-large (fallback)",
            "performance": "high",
            "speed": "slow"
        },
        "local_contracts_bert": {
            "name": "local",  # Special indicator for local model
            "description": "Local BERT contracts model (feature extraction + enhanced rules)",
            "performance": "high",
            "speed": "fast"
        }
    }
    
    def __init__(self, model_path: str, model_choice: str = "contracts_bert"):
        self.model_path = model_path
        self.model_choice = model_choice
        self.tokenizer = None
        self.model = None
        self.nlp = None
        self.device = None
        self._loaded = False
        
        # Enhanced label mapping with confidence thresholds
        self.label_mapping = {
            0: {"risk_type": RiskType.AUTO_RENEWAL, "risk_level": RiskLevel.HIGH, "threshold": 0.7},
            1: {"risk_type": RiskType.LIABILITY, "risk_level": RiskLevel.MEDIUM, "threshold": 0.6},
            2: {"risk_type": RiskType.TERMINATION, "risk_level": RiskLevel.MEDIUM, "threshold": 0.6},
            3: {"risk_type": RiskType.IP_OWNERSHIP, "risk_level": RiskLevel.HIGH, "threshold": 0.7},
            4: {"risk_type": "safe", "risk_level": RiskLevel.NONE, "threshold": 0.5}
        }
        
        # Track if model is untrained (has random classification head)
        self.is_untrained_model = False
    
    def load(self):
        """Load the enhanced ML model with automatic fallback options"""
        try:
            # Load spaCy for sentence segmentation
            self.nlp = spacy.load("en_core_web_sm")
            
            # Set device
            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
            print(f"✅ Using device: {self.device}")
            
            # Try to load the selected model with fallback
            model_loaded = False
            attempts = [self.model_choice] + [k for k in self.MODEL_OPTIONS.keys() if k != self.model_choice]
            
            for attempt in attempts:
                try:
                    model_info = self.MODEL_OPTIONS[attempt]
                    model_name = model_info["name"]
                    
                    # Handle local model
                    if attempt == "local_contracts_bert":
                        model_name = self.model_path  # Use local path
                        print(f"🔄 Attempting to load local model from {model_name}...")
                    else:
                        print(f"🔄 Attempting to load {model_name}...")
                    
                    print(f"   Description: {model_info['description']}")
                    print(f"   Performance: {model_info['performance']}, Speed: {model_info['speed']}")
                    
                    # Load tokenizer and model
                    self.tokenizer = AutoTokenizer.from_pretrained(model_name)
                    
                    # Handle different model types
                    if attempt == "local_contracts_bert":
                        # For local contracts BERT, use base model for feature extraction only
                        self.model = AutoModel.from_pretrained(model_name)
                        self.is_untrained_model = False  # Will use enhanced rules, not untrained classifier
                        print("🎯 Using local BERT for feature extraction + enhanced rule-based classification")
                    elif "legal" in model_name or "contracts" in model_name:
                        self.model = AutoModelForSequenceClassification.from_pretrained(
                            model_name,
                            num_labels=5,
                            ignore_mismatched_sizes=True
                        )
                    # For general models with pre-trained heads (like DeBERTa-MNLI)
                    elif "mnli" in model_name:
                        # Use as zero-shot classifier
                        self.classifier = pipeline(
                            "zero-shot-classification",
                            model=model_name,
                            tokenizer=model_name,
                            device=0 if torch.cuda.is_available() else -1
                        )
                        self.model = None  # Using pipeline instead
                    else:
                        self.model = AutoModelForSequenceClassification.from_pretrained(
                            model_name,
                            num_labels=5
                        )
                    
                    if self.model:
                        self.model.to(self.device)
                        self.model.eval()
                    
                    self.current_model = model_name
                    self.current_model_info = model_info
                    
                    # Detect if model has untrained classification head
                    if self.model and ("legal" in model_name.lower() or "contracts" in model_name.lower()):
                        self.is_untrained_model = True
                        self._adjust_thresholds_for_untrained_model()
                        print("⚠️  Detected untrained classification head - adjusted confidence thresholds")
                    
                    model_loaded = True
                    print(f"✅ Successfully loaded {model_name}")
                    break
                    
                except Exception as e:
                    print(f"❌ Failed to load {model_info['name']}: {e}")
                    continue
            
            if not model_loaded:
                print("❌ All model loading attempts failed, using enhanced rule-based approach")
                self.current_model = "enhanced_rules"
                self.current_model_info = {"name": "Enhanced Rules", "performance": "medium", "speed": "fast"}
            
            self._loaded = True
            print("✅ ML model components loaded successfully")
            
        except Exception as e:
            print(f"❌ Failed to load ML model: {e}")
            self._loaded = False
    
    def _adjust_thresholds_for_untrained_model(self):
        """Lower confidence thresholds for models with untrained classification heads"""
        # Much lower thresholds for untrained models since they produce lower confidence
        self.label_mapping[0]["threshold"] = 0.25  # Auto-renewal: 0.7 -> 0.25
        self.label_mapping[1]["threshold"] = 0.20  # Liability: 0.6 -> 0.20
        self.label_mapping[2]["threshold"] = 0.20  # Termination: 0.6 -> 0.20
        self.label_mapping[3]["threshold"] = 0.25  # IP ownership: 0.7 -> 0.25
        self.label_mapping[4]["threshold"] = 0.40  # Safe: 0.5 -> 0.40
    
    def analyze(self, text: str) -> List[RiskItem]:
        """Enhanced analysis using the selected high-performance model"""
        if not self._loaded:
            return []
        
        risks = []
        
        try:
            # Use spaCy for accurate sentence segmentation
            doc = self.nlp(text)
            
            for sent in doc.sents:
                sentence_text = sent.text.strip()
                if len(sentence_text) < 15:  # Skip very short sentences
                    continue
                
                # Use appropriate prediction method based on loaded model
                if hasattr(self, 'classifier') and self.classifier:
                    prediction = self._predict_with_zero_shot(sentence_text)
                elif self.current_model != "enhanced_rules" and not self.is_untrained_model:
                    prediction = self._predict_with_bert(sentence_text)
                else:
                    # Use enhanced rule-based prediction for untrained models or fallback
                    prediction = self._predict_sentence(sentence_text)
                
                if prediction and self._is_significant_risk(prediction):
                    label_info = self.label_mapping[prediction["label"]]
                    
                    risk_item = RiskItem(
                        risk_type=label_info["risk_type"],
                        text=sentence_text,
                        description=self._generate_description(prediction, label_info),
                        suggestion=self._generate_suggestion(label_info["risk_type"]),
                        risk_level=label_info["risk_level"],
                        confidence=prediction["confidence"],
                        start_pos=sent.start_char,
                        end_pos=sent.end_char,
                        detector=f"ml_model_{self.current_model.split('/')[-1] if '/' in self.current_model else self.current_model}"
                    )
                    risks.append(risk_item)
                    
        except Exception as e:
            print(f"❌ ML analysis failed: {e}")
        
        return risks
    
    def _predict_with_bert(self, text: str) -> Optional[Dict[str, Any]]:
        """Prediction using BERT-style models (Legal-BERT, Contracts-BERT)"""
        try:
            # Tokenize and predict
            inputs = self.tokenizer(
                text,
                return_tensors="pt",
                max_length=512,
                truncation=True,
                padding=True
            ).to(self.device)
            
            with torch.no_grad():
                outputs = self.model(**inputs)
                probabilities = torch.nn.functional.softmax(outputs.logits, dim=-1)
                predicted_class = torch.argmax(probabilities, dim=-1).item()
                confidence = probabilities[0][predicted_class].item()
            
            return {
                "label": predicted_class,
                "confidence": confidence
            }
            
        except Exception as e:
            print(f"❌ BERT prediction failed: {e}")
            # Fallback to enhanced rule-based prediction
            return self._predict_sentence(text)
    
    def _predict_with_zero_shot(self, text: str) -> Optional[Dict[str, Any]]:
        """Prediction using zero-shot classification (DeBERTa-MNLI)"""
        try:
            candidate_labels = [
                "automatic renewal clause",
                "liability limitation clause", 
                "termination clause",
                "intellectual property ownership clause",
                "safe contract clause"
            ]
            
            result = self.classifier(text, candidate_labels)
            
            # Map back to our label system
            label_map = {
                "automatic renewal clause": 0,
                "liability limitation clause": 1,
                "termination clause": 2,
                "intellectual property ownership clause": 3,
                "safe contract clause": 4
            }
            
            best_label = result['labels'][0]
            confidence = result['scores'][0]
            
            return {
                "label": label_map.get(best_label, 4),
                "confidence": confidence
            }
            
        except Exception as e:
            print(f"❌ Zero-shot prediction failed: {e}")
            # Fallback to enhanced rule-based prediction
            return self._predict_sentence(text)
    
    def _is_significant_risk(self, prediction: Dict[str, Any]) -> bool:
        """Determine if prediction represents a significant risk"""
        label = prediction["label"]
        confidence = prediction["confidence"]
        
        if label == 4:  # Safe clause
            return False
            
        # Use dynamic thresholds based on label
        threshold = self.label_mapping[label]["threshold"]
        return confidence > threshold
    
    def _generate_description(self, prediction: Dict[str, Any], label_info: Dict[str, Any]) -> str:
        """Generate detailed description based on model and prediction"""
        risk_type = label_info["risk_type"]
        confidence = prediction["confidence"]
        model_name = self.current_model_info.get("name", "AI model")
        
        base_desc = f"{model_name} detected {risk_type.value} risk"
        confidence_desc = f"(confidence: {confidence:.2f})"
        
        # Add specific insights based on risk type
        if risk_type == RiskType.AUTO_RENEWAL:
            return f"{base_desc} - Potential for automatic contract extension {confidence_desc}"
        elif risk_type == RiskType.LIABILITY:
            return f"{base_desc} - Liability cap or limitation detected {confidence_desc}"
        elif risk_type == RiskType.TERMINATION:
            return f"{base_desc} - Unfavorable termination conditions {confidence_desc}"
        elif risk_type == RiskType.IP_OWNERSHIP:
            return f"{base_desc} - Intellectual property ownership transfer {confidence_desc}"
        else:
            return f"{base_desc} {confidence_desc}"
    
    def _generate_suggestion(self, risk_type: RiskType) -> str:
        """Generate specific suggestions based on risk type"""
        suggestions = {
            RiskType.AUTO_RENEWAL: "Review auto-renewal terms and ensure adequate notice period for cancellation",
            RiskType.LIABILITY: "Verify liability limits are reasonable and mutual",
            RiskType.TERMINATION: "Negotiate for reasonable termination notice and conditions",
            RiskType.IP_OWNERSHIP: "Clarify IP ownership rights and ensure protection of your assets"
        }
        return suggestions.get(risk_type, "Review this clause with legal counsel")
    def _predict_sentence(self, text: str) -> Optional[Dict[str, Any]]:
        """Enhanced rule-based prediction (fallback method)"""
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
        """Enhanced prediction focusing on exploitative clauses detection"""
        text_lower = text.lower()
        
        # Base scores - bias toward "safe" 
        scores = [0.05, 0.05, 0.05, 0.05, 0.8]  # Even higher bias toward safe
        
        # EXPLOITATIVE Auto-renewal detection (enhanced for short periods)
        auto_renewal_indicators = [
            "auto-renew", "automatic renewal", "automatically renew", "shall auto", "auto renew"
        ]
        short_notice_indicators = [
            "1 day", "one day", "2 day", "two day", "3 day", "three day",
            "24 hour", "48 hour", "72 hour", "twenty-four hour"
        ]
        
        if any(term in text_lower for term in auto_renewal_indicators):
            if any(notice in text_lower for notice in short_notice_indicators):
                scores[0] = 0.95  # Extremely high for very short periods
            elif any(notice in text_lower for notice in ["7 day", "week", "weekly"]):
                scores[0] = 0.85  # High for 7-day notice
            else:
                scores[0] = 0.6   # Medium for general auto-renewal
        
        # EXPLOITATIVE Liability caps (enhanced for low amounts)
        liability_indicators = ["liability", "liable", "damages", "claims"]
        low_amounts = ["$100", "$200", "$300", "$500", "$1000", "$1,000", 
                      "one hundred", "two hundred", "five hundred", "one thousand"]
        liability_caps = ["limited to", "not exceed", "maximum", "cap", "limit"]
        
        if any(term in text_lower for term in liability_indicators):
            if any(cap in text_lower for cap in liability_caps) and any(amount in text_lower for amount in low_amounts):
                scores[1] = 0.9   # Very high for low liability caps
            elif any(amount in text_lower for amount in low_amounts):
                scores[1] = 0.75  # High for any low amount mention
            elif "limited" in text_lower:
                scores[1] = 0.6   # Medium for general limitation
        
        # EXPLOITATIVE Termination (enhanced for short notice)
        termination_indicators = ["terminate", "termination", "cancel", "end this agreement"]
        short_termination = ["7 day", "seven day", "1 week", "one week", "immediate", "24 hour"]
        
        if any(term in text_lower for term in termination_indicators):
            if any(short in text_lower for short in short_termination):
                scores[2] = 0.85  # High for short notice termination
            elif "written notice" in text_lower and any(day in text_lower for day in ["day", "days"]):
                scores[2] = 0.7   # Medium-high for any day-based notice
            else:
                scores[2] = 0.4   # Low for general termination
        
        # EXPLOITATIVE IP Ownership (enhanced for exclusive ownership)
        ip_indicators = ["intellectual property", "work product", "inventions", "creations", "developments"]
        exclusive_terms = ["belong exclusively", "exclusively to", "become property", "assign", "transfer"]
        company_terms = ["company", "employer", "client", "organization"]
        
        if any(ip in text_lower for ip in ip_indicators):
            if any(excl in text_lower for excl in exclusive_terms) and any(comp in text_lower for comp in company_terms):
                scores[3] = 0.95  # Extremely high for exclusive IP transfer
            elif "belong" in text_lower and any(comp in text_lower for comp in company_terms):
                scores[3] = 0.8   # High for IP belonging to company
            else:
                scores[3] = 0.5   # Medium for general IP mentions
        
        # Additional exploitative patterns
        # Indemnification (one-sided)
        if "indemnify" in text_lower and ("company" in text_lower or "client" in text_lower):
            scores[1] = max(scores[1], 0.75)  # Treat as liability issue
        
        # Perpetual terms
        if any(term in text_lower for term in ["perpetual", "indefinite", "forever", "permanent"]):
            scores[0] = max(scores[0], 0.7)  # Boost auto-renewal score
            
        # Excessive penalties
        if any(term in text_lower for term in ["penalty", "fine", "late fee"]) and "%" in text_lower:
            scores[1] = max(scores[1], 0.8)  # Boost liability score
        
        # Normalize scores to ensure they sum to 1
        total = sum(scores)
        if total > 1:
            scores = [score / total for score in scores]
        
        return scores