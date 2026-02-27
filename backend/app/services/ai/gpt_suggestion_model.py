from transformers import GPT2LMHeadModel, GPT2Tokenizer
import torch
from app.models.schemas import Suggestion

class GPTSuggestionModel:
    def __init__(self, model_name: str = "distilgpt2"):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.tokenizer = GPT2Tokenizer.from_pretrained(model_name)
        self.model = GPT2LMHeadModel.from_pretrained(model_name)
        self.model.to(self.device)
        self.model.eval()
        
        # Set pad token
        self.tokenizer.pad_token = self.tokenizer.eos_token
    
    def generate_suggestion(
        self, 
        risk_text: str, 
        risk_type: str,
        max_length: int = 150
    ) -> Suggestion:
        """Generate suggestion using GPT-2"""
        
        prompt = f"Risk in contract: {risk_text}\nRecommendation to mitigate or reduce this {risk_type} risk:"
        
        inputs = self.tokenizer(prompt, return_tensors="pt", truncation=True)
        inputs = {k: v.to(self.device) for k, v in inputs.items()}
        
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_length=len(inputs['input_ids'][0]) + max_length,
                temperature=0.8,
                top_k=50,
                top_p=0.95,
                do_sample=True,
                pad_token_id=self.tokenizer.eos_token_id
            )
        
        full_text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        suggestion_text = full_text.replace(prompt, "").strip()
        
        return Suggestion(
            suggestion_text=suggestion_text,
            rationale="Context-aware AI recommendation",
            confidence=0.75,
            source="gpt_model",
            priority=2
        )