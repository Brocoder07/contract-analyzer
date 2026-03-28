from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable, List

import torch
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

from app.services.ai.hindi_recommendations import get_hindi_recommendation


@dataclass
class TranslatorConfig:
    model_path: str
    max_input_length: int = 256
    max_output_length: int = 256


class OutputTranslator:
    """
    Lazy-loaded EN->HI translation helper for analysis outputs.
    Uses local model artifacts provided in app/data/models/en_hi_translate.
    """

    def __init__(self, config: TranslatorConfig):
        self.config = config
        self._loaded = False
        self._tokenizer = None
        self._model = None
        self._device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    def _load(self) -> None:
        if self._loaded:
            return

        self._tokenizer = AutoTokenizer.from_pretrained(self.config.model_path, local_files_only=True)
        self._model = AutoModelForSeq2SeqLM.from_pretrained(self.config.model_path, local_files_only=True)
        self._model.to(self._device)
        self._model.eval()
        self._loaded = True

    def translate_text(self, text: str) -> str:
        if not text or not text.strip():
            return text

        self._load()

        try:
            inputs = self._tokenizer(
                text,
                return_tensors="pt",
                truncation=True,
                max_length=self.config.max_input_length,
            )
            inputs = {k: v.to(self._device) for k, v in inputs.items()}

            with torch.no_grad():
                output_ids = self._model.generate(
                    **inputs,
                    max_length=self.config.max_output_length,
                    num_beams=4,
                    early_stopping=True,
                )
            return self._tokenizer.decode(output_ids[0], skip_special_tokens=True)
        except Exception:
            # Graceful fallback to original text if translation fails
            return text

    def translate_many(self, texts: Iterable[str]) -> List[str]:
        return [self.translate_text(t) for t in texts]

    def translate_analysis_result(self, result: dict[str, Any]) -> dict[str, Any]:
        """
        Mutates + returns result dictionary from HybridRiskAnalyzer.
        Translates model-generated textual outputs into Hindi.
        """
        risks = result.get("risks", [])
        for risk in risks:
            risk_type = None
            if hasattr(risk, "risk_type"):
                rt = getattr(risk, "risk_type")
                risk_type = getattr(rt, "value", rt)

            if hasattr(risk, "description"):
                risk.description = self.translate_text(risk.description)
            if hasattr(risk, "suggestion"):
                translated = self.translate_text(risk.suggestion)
                risk.suggestion = get_hindi_recommendation(risk_type, translated)

            if getattr(risk, "best_suggestion", None):
                bs = risk.best_suggestion
                translated = self.translate_text(bs.suggestion_text)
                bs.suggestion_text = get_hindi_recommendation(risk_type, translated)
                bs.rationale = self.translate_text(bs.rationale)

            suggestions = getattr(risk, "suggestions", None) or []
            for s in suggestions:
                translated = self.translate_text(s.suggestion_text)
                s.suggestion_text = get_hindi_recommendation(risk_type, translated)
                s.rationale = self.translate_text(s.rationale)

        summary = result.get("summary")
        if summary is not None:
            if hasattr(summary, "summary_text"):
                summary.summary_text = self.translate_text(summary.summary_text)
            if hasattr(summary, "key_points") and isinstance(summary.key_points, list):
                summary.key_points = self.translate_many(summary.key_points)
            if hasattr(summary, "contract_type") and isinstance(summary.contract_type, str):
                summary.contract_type = self.translate_text(summary.contract_type)

        result["output_language"] = "hi"
        return result
