import re
import json
import spacy
from typing import List
from app.models.schemas import RiskItem, RiskLevel, RiskType

class RuleEngine:
    """
    Rule-based contract risk detector with spaCy
    """
    
    def __init__(self, rules_config_path: str):
        self.rules_config_path = rules_config_path
        self.nlp = None
        self.rules = []
        
    def load_rules(self):
        """Load rules from JSON file and spaCy model"""
        try:
            self.nlp = spacy.load("en_core_web_sm")
            
            # Try to load from JSON file first, fallback to built-in rules
            try:
                with open(self.rules_config_path, 'r') as f:
                    rules_data = json.load(f)
                    self.rules = self._process_json_rules(rules_data['risk_patterns'])
                    print(f"✅ Loaded {len(self.rules)} rule patterns from {self.rules_config_path}")
            except (FileNotFoundError, json.JSONDecodeError, KeyError) as e:
                print(f"⚠️  Could not load JSON rules ({e}), using built-in rules")
                self.rules = self._get_builtin_rules()
                print(f"✅ Loaded {len(self.rules)} built-in rule patterns with spaCy")
                
        except Exception as e:
            print(f"❌ Failed to load spaCy model: {e}")
            raise
    
    def analyze(self, text: str) -> List[RiskItem]:
        """Analyze text using rule-based patterns with spaCy sentence segmentation"""
        if not self.nlp or not self.rules:
            self.load_rules()
        
        risks = []
        doc = self.nlp(text)
        
        # Use spaCy for accurate sentence segmentation
        for sent in doc.sents:
            sentence_text = sent.text.strip()
            if len(sentence_text) < 10:  # Skip very short sentences
                continue
                
            for rule in self.rules:
                match_result = self._matches_rule(sentence_text, rule)
                if isinstance(match_result, tuple):
                    matches, confidence, description = match_result
                else:
                    matches = match_result
                    confidence = 0.85
                    description = rule["description"]
                    
                if matches:
                    risk_item = RiskItem(
                        risk_type=rule["risk_type"],
                        text=sentence_text,
                        description=description,
                        suggestion=rule["suggestion"],
                        risk_level=rule["risk_level"],
                        confidence=confidence,
                        start_pos=sent.start_char,
                        end_pos=sent.end_char,
                        detector="rule_engine"
                    )
                    risks.append(risk_item)
                    break  # Only match one rule per sentence
        
        return risks
    
    def _matches_rule(self, text: str, rule: dict) -> tuple[bool, float, str]:
        """Check if text matches any pattern in the rule"""
        for pattern_info in rule["patterns"]:
            try:
                # Handle both string patterns (built-in) and dict patterns (JSON)
                if isinstance(pattern_info, str):
                    pattern = pattern_info
                    flags = re.IGNORECASE
                else:
                    pattern = pattern_info.get("text", "")
                    flags = re.IGNORECASE
                    if "flags" in pattern_info:
                        # Convert flag names to re module constants
                        for flag_name in pattern_info["flags"]:
                            if hasattr(re, flag_name):
                                flags |= getattr(re, flag_name)
                
                if re.search(pattern, text, flags):
                    confidence = pattern_info.get("weight", 0.8) if isinstance(pattern_info, dict) else 0.8
                    description = pattern_info.get("description", rule["description"]) if isinstance(pattern_info, dict) else rule["description"]
                    print(f"🔍 Rule matched: {rule['risk_type']} (confidence: {confidence:.2f}) - '{text[:60]}...'")
                    return True, confidence, description
            except Exception as e:
                print(f"❌ Regex error with pattern '{pattern}': {e}")
        return False, 0.0, ""
    
    def _process_json_rules(self, json_patterns: List[dict]) -> List[dict]:
        """Convert JSON rule patterns to internal format"""
        processed_rules = []
        
        for pattern_group in json_patterns:
            # Convert string risk types to enum values
            risk_type_str = pattern_group.get("risk_type", "").lower()
            risk_type = getattr(RiskType, risk_type_str.upper(), RiskType.LIABILITY)
            
            # Convert string risk levels to enum values  
            risk_level_str = pattern_group.get("risk_level", "medium").lower()
            risk_level = getattr(RiskLevel, risk_level_str.upper(), RiskLevel.MEDIUM)
            
            processed_rule = {
                "risk_type": risk_type,
                "risk_level": risk_level,
                "description": pattern_group.get("description", "Risk detected"),
                "suggestion": self._get_suggestion_for_risk_type(risk_type),
                "patterns": pattern_group.get("patterns", [])
            }
            processed_rules.append(processed_rule)
            
        return processed_rules
    
    def _get_suggestion_for_risk_type(self, risk_type: RiskType) -> str:
        """Get appropriate suggestion based on risk type"""
        suggestions = {
            RiskType.AUTO_RENEWAL: "Increase notice period to at least 30 days and consider manual renewal instead of automatic",
            RiskType.LIABILITY: "Ensure liability cap is reasonable and mutual, exclude gross negligence and willful misconduct", 
            RiskType.TERMINATION: "Increase notice period to 30+ days and ensure mutual termination rights",
            RiskType.IP_OWNERSHIP: "Limit IP claims to work done with company resources, exclude pre-existing IP and personal projects",
            RiskType.INDEMNIFICATION: "Make indemnification mutual and exclude company's own negligence or misconduct",
            RiskType.CONFIDENTIALITY: "Limit confidentiality period (3-5 years) and exclude publicly available information"
        }
        return suggestions.get(risk_type, "Review this clause with legal counsel for fairness")
    
    def _get_builtin_rules(self) -> List[dict]:
        """Enhanced rule patterns for better detection"""
        return [
            {
                "risk_type": RiskType.AUTO_RENEWAL,
                "risk_level": RiskLevel.HIGH,
                "description": "Short auto-renewal notice period",
                "suggestion": "Increase notice period to at least 30 days and consider manual renewal instead of automatic",
                "patterns": [
                    r"auto.*renew.*\d+\s*day",  # More flexible number matching
                    r"automatic.*extension.*\d+\s*day",
                    r"renew.*unless.*cancel.*\d+\s*day",
                    r"automatic.*renewal",
                    r"auto.*renew",  # Basic pattern without specific days
                    r"perpetual.*renew",
                    r"1 day.*renew",  # Specific case for 1 day
                    r"24 hour.*renew"
                ]
            },
            {
                "risk_type": RiskType.LIABILITY,
                "risk_level": RiskLevel.MEDIUM,
                "description": "Specific liability cap with low amount",
                "suggestion": "Ensure liability cap is reasonable for potential damages and consider excluding intentional misconduct",
                "patterns": [
                    r"liability.*limit.*\$\d+",  # Any dollar amount
                    r"maximum liability.*\$\d+",
                    r"cap on liability.*\$\d+",
                    r"total liability.*\$\d+",
                    r"not liable.*consequential",
                    r"liability.*\$\d+",  # Simpler pattern
                    r"\$1000.*liability",  # Specific amount
                    r"limited.*liability.*\$\d+"
                ]
            },
            {
                "risk_type": RiskType.TERMINATION,
                "risk_level": RiskLevel.MEDIUM,
                "description": "Short termination notice period",
                "suggestion": "Increase termination notice period to 30 days and ensure mutual termination rights",
                "patterns": [
                    r"terminat.*\d+\s*day",  # Any number of days
                    r"termination.*notice.*\d+\s*day",
                    r"cancel.*\d+\s*day",
                    r"termination.*without cause.*\d+\s*day",
                    r"7 day.*terminat",  # Specific case
                    r"7 day.*notice",
                    r"written notice.*\d+\s*day"
                ]
            },
            {
                "risk_type": RiskType.IP_OWNERSHIP,
                "risk_level": RiskLevel.HIGH,
                "description": "Overly broad intellectual property ownership",
                "suggestion": "Limit IP claims to work done during working hours using company resources, exclude pre-existing IP",
                "patterns": [
                    r"intellectual property.*belong to",  # More flexible
                    r"all inventions.*company",
                    r"IP.*ownership.*company",
                    r"work product.*company",
                    r"inventions.*assign.*company",
                    r"intellectual property.*company",
                    r"belong.*exclusively.*company",
                    r"developed.*belong.*company"
                ]
            }
        ]