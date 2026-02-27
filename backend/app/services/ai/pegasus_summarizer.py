"""
Pegasus-based summarization model
Uses google/pegasus-cnn_dailymail for abstractive summarization
"""

import torch
from transformers import PegasusTokenizer, PegasusForConditionalGeneration
import logging
from app.models.schemas import Summary

logger = logging.getLogger(__name__)


class PegasusSummarizer:
    """
    Pegasus model for abstractive contract summarization
    """
    
    def __init__(self, model_name: str = "google/pegasus-cnn_dailymail"):
        self.model_name = model_name
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.tokenizer = None
        self.model = None
        logger.info(f"Initializing Pegasus summarizer with {model_name}")
    
    def load(self):
        """Load Pegasus model and tokenizer"""
        if self.model is None:
            logger.info(f"Loading Pegasus model: {self.model_name}")
            self.tokenizer = PegasusTokenizer.from_pretrained(self.model_name)
            self.model = PegasusForConditionalGeneration.from_pretrained(self.model_name)
            self.model.to(self.device)
            self.model.eval()
            logger.info("Pegasus model loaded successfully")
    
    def generate_summary(
        self,
        text: str,
        min_length: int = 50,
        max_length: int = 300
    ) -> Summary:
        """Generate summary using Pegasus"""
        self.load()
        
        logger.info("Generating Pegasus summary")
        
        inputs = self.tokenizer(
            text,
            max_length=1024,
            truncation=True,
            return_tensors="pt"
        )
        inputs = {k: v.to(self.device) for k, v in inputs.items()}
        
        with torch.no_grad():
            summary_ids = self.model.generate(
                inputs["input_ids"],
                num_beams=4,
                min_length=min_length,
                max_length=max_length,
                early_stopping=True
            )
        
        summary_text = self.tokenizer.decode(
            summary_ids[0],
            skip_special_tokens=True
        )
        
        original_words = len(text.split())
        summary_words = len(summary_text.split())
        
        return Summary(
            summary_text=summary_text,
            key_points=[],
            parties_involved=[],
            important_dates=[],
            contract_type=None,
            confidence=0.86,
            source="pegasus",
            word_count=summary_words,
            compression_ratio=original_words / summary_words if summary_words > 0 else 1.0
        )