import re
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
        """Load rules and spaCy model"""
        try:
            self.nlp = spacy.load("en_core_web_sm")
            self.rules = self._get_builtin_rules()
            print(f"✅ Loaded {len(self.rules)} rule patterns with spaCy")
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
                if self._matches_rule(sentence_text, rule):
                    risk_item = RiskItem(
                        risk_type=rule["risk_type"],
                        text=sentence_text,
                        description=rule["description"],
                        suggestion=rule["suggestion"],
                        risk_level=rule["risk_level"],
                        confidence=0.85,
                        start_pos=sent.start_char,
                        end_pos=sent.end_char,
                        detector="rule_based"
                    )
                    risks.append(risk_item)
                    break  # Only match one rule per sentence
        
        return risks
    
    def _matches_rule(self, text: str, rule: dict) -> bool:
        """Check if text matches any pattern in the rule"""
        for pattern in rule["patterns"]:
            try:
                if re.search(pattern, text, re.IGNORECASE):
                    print(f"🔍 Rule matched: {rule['risk_type']} - '{text}'")
                    return True
            except Exception as e:
                print(f"❌ Regex error with pattern '{pattern}': {e}")
        return False
    
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