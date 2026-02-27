from transformers import T5ForConditionalGeneration, T5Tokenizer
import torch
from app.models.schemas import Suggestion

class T5SuggestionModel:
    def __init__(self, model_name: str = "google/flan-t5-base"):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.tokenizer = T5Tokenizer.from_pretrained(model_name)
        self.model = T5ForConditionalGeneration.from_pretrained(model_name)
        self.model.to(self.device)
        self.model.eval()
    
    # In the generate_suggestion method, change:

    def generate_suggestion(
        self, 
        risk_text: str, 
        risk_type: str,
        max_length: int = 150
    ) -> Suggestion:
        """Generate suggestion using T5"""
        
        prompt = f"""Given this risky contract clause about {risk_type}:
    "{risk_text}"

    Suggest how to reduce this risk:"""
        
        inputs = self.tokenizer(prompt, return_tensors="pt", max_length=512, truncation=True)
        inputs = {k: v.to(self.device) for k, v in inputs.items()}
        
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_length=max_length,
                num_beams=5,
                temperature=0.7,
                do_sample=True,
                top_p=0.9
            )
        
        suggestion_text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        confidence = self._calculate_confidence(outputs)
        
        return Suggestion(
            suggestion_text=suggestion_text,
            rationale="AI-generated recommendation based on contract analysis",
            confidence=confidence,
            source="t5_model",
            priority=2
        )

    def _calculate_confidence(self, outputs) -> float:
        """Calculate confidence from model outputs"""
        # Simple heuristic - can be improved
        return 0.75