"""
BART-SAMSum summarization model
Uses philschmid/bart-large-cnn-samsum for dialogue-style summarization
"""

import torch
from transformers import BartTokenizer, BartForConditionalGeneration
import logging
from app.models.schemas import Summary

logger = logging.getLogger(__name__)


class BARTSamSumSummarizer:
    """
    BART-SAMSum model for contract summarization
    Optimized for dialogue and conversational text
    """
    
    def __init__(self, model_name: str = "philschmid/bart-large-cnn-samsum"):
        self.model_name = model_name
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.tokenizer = None
        self.model = None
        logger.info(f"Initializing BART-SAMSum summarizer with {model_name}")
    
    def load(self):
        """Load BART-SAMSum model and tokenizer"""
        if self.model is None:
            logger.info(f"Loading BART-SAMSum model: {self.model_name}")
            self.tokenizer = BartTokenizer.from_pretrained(self.model_name)
            self.model = BartForConditionalGeneration.from_pretrained(self.model_name)
            self.model.to(self.device)
            self.model.eval()
            logger.info("BART-SAMSum model loaded successfully")
    
    def generate_summary(
        self,
        text: str,
        min_length: int = 50,
        max_length: int = 300
    ) -> Summary:
        """
        Generate summary using BART-SAMSum
        
        Args:
            text: Contract text to summarize
            min_length: Minimum summary length
            max_length: Maximum summary length
            
        Returns:
            Summary object
        """
        self.load()
        
        logger.info("Generating BART-SAMSum summary")
        
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
                early_stopping=True,
                no_repeat_ngram_size=3
            )
        
        summary_text = self.tokenizer.decode(
            summary_ids[0],
            skip_special_tokens=True,
            clean_up_tokenization_spaces=True
        )
        
        original_words = len(text.split())
        summary_words = len(summary_text.split())
        compression_ratio = original_words / summary_words if summary_words > 0 else 1.0
        
        logger.info(f"BART-SAMSum summary generated: {summary_words} words")
        
        return Summary(
            summary_text=summary_text,
            key_points=[],
            parties_involved=[],
            important_dates=[],
            contract_type=None,
            confidence=0.87,
            source="bart_samsum",
            word_count=summary_words,
            compression_ratio=compression_ratio
        )