"""
Custom ML model for contract risk analysis.

Loads the trained MultiTaskTransformer (TF-IDF SVM or MiniLM fine-tuned model)
from the custom_analysis_model directory.  The model was trained on the CUAD
dataset and detects the 15 unfair-clause categories defined by the CUAD benchmark.

Architecture (matches contractanalysis_tfidf_slm.ipynb):
  - Encoder: microsoft/MiniLM-L12-H384-uncased
  - Binary head: Linear(hidden, 1)   → fair / unfair
  - Multi-label head: Linear(hidden, 15) → one sigmoid per category
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import List, Optional

import spacy
import torch
import torch.nn as nn
from transformers import AutoModel, AutoTokenizer

from app.models.schemas import RiskItem, RiskLevel, RiskType


# ── Category → (RiskType, RiskLevel) mapping ─────────────────────────────────
# Order MUST match mlb.classes_ (alphabetical, as sklearn sorts them).
CUAD_CATEGORY_MAP: dict[str, tuple[RiskType, RiskLevel]] = {
    "Anti-Assignment":          (RiskType.ANTI_ASSIGNMENT,          RiskLevel.MEDIUM),
    "Cap On Liability":         (RiskType.CAP_ON_LIABILITY,         RiskLevel.HIGH),
    "Change Of Control":        (RiskType.CHANGE_OF_CONTROL,        RiskLevel.HIGH),
    "Covenant Not To Sue":      (RiskType.COVENANT_NOT_TO_SUE,      RiskLevel.HIGH),
    "Exclusivity":              (RiskType.EXCLUSIVITY,              RiskLevel.MEDIUM),
    "IP Ownership Assignment":  (RiskType.IP_OWNERSHIP_ASSIGNMENT,  RiskLevel.HIGH),
    "Liquidated Damages":       (RiskType.LIQUIDATED_DAMAGES,       RiskLevel.HIGH),
    "Minimum Commitment":       (RiskType.MINIMUM_COMMITMENT,       RiskLevel.MEDIUM),
    "No-Solicit Of Employees":  (RiskType.NO_SOLICIT_OF_EMPLOYEES,  RiskLevel.MEDIUM),
    "Non-Compete":              (RiskType.NON_COMPETE,              RiskLevel.HIGH),
    "Non-Disparagement":        (RiskType.NON_DISPARAGEMENT,        RiskLevel.LOW),
    "Post-Termination Services":(RiskType.POST_TERMINATION_SERVICES,RiskLevel.MEDIUM),
    "ROFR/ROFO/ROFN":           (RiskType.ROFR_ROFO_ROFN,          RiskLevel.MEDIUM),
    "Termination For Convenience":(RiskType.TERMINATION_FOR_CONVENIENCE, RiskLevel.HIGH),
    "Uncapped Liability":       (RiskType.UNCAPPED_LIABILITY,       RiskLevel.HIGH),
}

CATEGORY_DESCRIPTIONS: dict[str, str] = {
    "Anti-Assignment":           "Restricts a party's ability to assign the contract to a third party.",
    "Cap On Liability":          "Limits the maximum financial exposure of a party.",
    "Change Of Control":         "Contains provisions triggered by a change in ownership or control.",
    "Covenant Not To Sue":       "Restricts a party's right to bring legal action.",
    "Exclusivity":               "Grants exclusive rights to one party, restricting dealings with others.",
    "IP Ownership Assignment":   "Transfers intellectual property rights to another party.",
    "Liquidated Damages":        "Specifies predetermined damages for contract breach.",
    "Minimum Commitment":        "Requires a party to meet a minimum purchase or usage threshold.",
    "No-Solicit Of Employees":   "Prohibits soliciting or hiring the other party's employees.",
    "Non-Compete":               "Restricts a party from engaging in competing business activities.",
    "Non-Disparagement":         "Prohibits parties from making negative statements about each other.",
    "Post-Termination Services": "Requires continued services or obligations after contract termination.",
    "ROFR/ROFO/ROFN":            "Grants rights of first refusal, offer, or negotiation.",
    "Termination For Convenience":"Allows unilateral termination without cause.",
    "Uncapped Liability":        "Places no ceiling on a party's financial liability.",
}


class _MultiTaskTransformer(nn.Module):
    """
    Exact replica of the MultiTaskTransformer class from the notebook.
    Must stay in sync with the saved model.pt checkpoint.
    """

    def __init__(self, model_name: str, num_labels: int, dropout: float = 0.1):
        super().__init__()
        self.encoder = AutoModel.from_pretrained(model_name)
        self.hidden_size = self.encoder.config.hidden_size
        self.dropout = nn.Dropout(dropout)
        self.binary_head = nn.Linear(self.hidden_size, 1)
        self.multilabel_head = nn.Linear(self.hidden_size, num_labels)

    def forward(self, input_ids, attention_mask):
        outputs = self.encoder(input_ids=input_ids, attention_mask=attention_mask)
        pooled = outputs.last_hidden_state[:, 0, :]   # [CLS]
        pooled = self.dropout(pooled)
        return self.binary_head(pooled), self.multilabel_head(pooled)


class CustomMLModel:
    """
    Wrapper around the trained MiniLM multi-task model.
    Drop-in replacement for MLModel inside HybridRiskAnalyzer.
    """

    BINARY_THRESHOLD: float = 0.5    # sigmoid > threshold → unfair
    CATEGORY_THRESHOLD: float = 0.4  # per-label sigmoid threshold (slightly lower for recall)
    MIN_SENTENCE_LEN: int = 15

    def __init__(self, model_dir: str):
        self.model_dir = Path(model_dir)
        self.device: Optional[torch.device] = None
        self.tokenizer = None
        self._model: Optional[_MultiTaskTransformer] = None
        self.nlp = None
        self._categories: list[str] = []
        self._loaded = False
        self._max_length: int = 256

    # ── Loading ──────────────────────────────────────────────────────────────

    def load(self) -> None:
        """Load tokenizer, model weights, and spaCy sentence splitter."""
        try:
            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
            print(f"✅ CustomMLModel: using device {self.device}")

            checkpoint_path = self.model_dir / "model.pt"
            tokenizer_path  = self.model_dir / "tokenizer"
            config_path     = self.model_dir / "config.json"

            if not checkpoint_path.exists():
                raise FileNotFoundError(f"model.pt not found at {checkpoint_path}")

            # Load checkpoint
            checkpoint = torch.load(checkpoint_path, map_location=self.device, weights_only=False)

            model_name  = checkpoint["config"]["model_name"]
            num_labels  = checkpoint["config"]["num_labels"]
            self._max_length = checkpoint["config"].get("max_length", 256)

            # Resolve category names from the saved MultiLabelBinarizer
            mlb = checkpoint.get("mlb")
            if mlb is not None:
                self._categories = list(mlb.classes_)
            else:
                # Fallback: alphabetical sort of the known categories
                self._categories = sorted(CUAD_CATEGORY_MAP.keys())

            print(f"   Model: {model_name}")
            print(f"   Labels ({num_labels}): {self._categories}")

            # Load tokenizer (from saved copy if available, else from HuggingFace)
            tok_source = str(tokenizer_path) if tokenizer_path.exists() else model_name
            self.tokenizer = AutoTokenizer.from_pretrained(tok_source)
            print(f"   Tokenizer loaded from: {tok_source}")

            # Instantiate architecture and load weights
            self._model = _MultiTaskTransformer(
                model_name=model_name,
                num_labels=num_labels,
            ).to(self.device)
            self._model.load_state_dict(checkpoint["model_state_dict"])
            self._model.eval()
            print("   Weights loaded ✅")

            # spaCy for sentence segmentation (same as rule_engine / old ml_model)
            self.nlp = spacy.load("en_core_web_sm")

            self._loaded = True
            print("✅ CustomMLModel loaded successfully")

        except Exception as exc:
            print(f"❌ CustomMLModel failed to load: {exc}")
            self._loaded = False

    # ── Inference ────────────────────────────────────────────────────────────

    def analyze(self, text: str) -> List[RiskItem]:
        """Run sentence-level inference and return detected risks."""
        if not self._loaded or self._model is None:
            return []

        risks: List[RiskItem] = []

        try:
            import time
            t0 = time.time()
            doc = self.nlp(text)
            sentences = [s for s in doc.sents if len(s.text.strip()) >= self.MIN_SENTENCE_LEN]
            print(f"[⏱ ML]  spaCy segmentation:      {time.time()-t0:.3f}s  ({len(sentences)} sentences to classify)")

            for i, sent in enumerate(sentences):
                sentence = sent.text.strip()
                t = time.time()
                is_unfair, category_hits = self._predict(sentence)
                elapsed = time.time() - t
                label = f"[{', '.join(c for c,_ in category_hits)}]" if category_hits else "clean"
                print(f"[⏱ ML]  sent {i+1:>3}/{len(sentences)}  {elapsed:.3f}s  unfair={is_unfair}  {label}")

                if not is_unfair or not category_hits:
                    continue

                for category, confidence in category_hits:
                    risk_type, risk_level = CUAD_CATEGORY_MAP.get(
                        category,
                        (RiskType.TERMINATION, RiskLevel.MEDIUM),
                    )
                    risks.append(
                        RiskItem(
                            risk_type=risk_type,
                            text=sentence,
                            description=self._description(category, confidence),
                            suggestion=self._suggestion(category),
                            risk_level=risk_level,
                            confidence=round(confidence, 4),
                            start_pos=sent.start_char,
                            end_pos=sent.end_char,
                            detector="custom_ml_model",
                        )
                    )

            print(f"[⏱ ML]  total inference:         {time.time()-t0:.3f}s  → {len(risks)} risks found")

        except Exception as exc:
            print(f"❌ CustomMLModel.analyze failed: {exc}")

        return risks

    # ── Private helpers ──────────────────────────────────────────────────────

    @torch.no_grad()
    def _predict(self, text: str) -> tuple[bool, list[tuple[str, float]]]:
        """
        Returns (is_unfair, [(category, confidence), ...]).
        Both tasks run independently (same as notebook architecture).
        """
        encoding = self.tokenizer(
            text,
            padding="max_length",
            truncation=True,
            max_length=self._max_length,
            return_tensors="pt",
        )
        input_ids      = encoding["input_ids"].to(self.device)
        attention_mask = encoding["attention_mask"].to(self.device)

        binary_logits, multilabel_logits = self._model(input_ids, attention_mask)

        binary_prob  = torch.sigmoid(binary_logits).item()
        is_unfair    = binary_prob >= self.BINARY_THRESHOLD

        category_probs = torch.sigmoid(multilabel_logits).squeeze(0).cpu().tolist()
        category_hits  = [
            (self._categories[i], float(p))
            for i, p in enumerate(category_probs)
            if p >= self.CATEGORY_THRESHOLD
        ]
        # Sort by confidence descending
        category_hits.sort(key=lambda x: x[1], reverse=True)

        return is_unfair, category_hits

    @staticmethod
    def _description(category: str, confidence: float) -> str:
        base = CATEGORY_DESCRIPTIONS.get(category, f"Detected {category} clause.")
        return f"{base} (confidence: {confidence:.0%})"

    @staticmethod
    def _suggestion(category: str) -> str:
        suggestions = {
            "Anti-Assignment":
                "Negotiate for mutual assignment rights or add exceptions for affiliate transfers.",
            "Cap On Liability":
                "Ensure the liability cap is reasonable and symmetric for both parties.",
            "Change Of Control":
                "Review change-of-control triggers and negotiate carve-outs where appropriate.",
            "Covenant Not To Sue":
                "Limit scope and duration; retain the right to defend against third-party claims.",
            "Exclusivity":
                "Limit exclusivity to a defined scope and add performance benchmarks.",
            "IP Ownership Assignment":
                "Clarify which IP is pre-existing and ensure background IP is carved out.",
            "Liquidated Damages":
                "Verify amounts are reasonable estimates of actual damages, not punitive.",
            "Minimum Commitment":
                "Negotiate lower minimums or include ramp-up periods and force-majeure relief.",
            "No-Solicit Of Employees":
                "Limit duration and scope; ensure reciprocal application.",
            "Non-Compete":
                "Narrow geographic scope, duration, and covered activities.",
            "Non-Disparagement":
                "Ensure mutual application and carve out truthful statements to regulators.",
            "Post-Termination Services":
                "Define scope, duration, and compensation for any post-termination obligations.",
            "ROFR/ROFO/ROFN":
                "Set clear timelines and pricing mechanisms for the right of first refusal/offer.",
            "Termination For Convenience":
                "Add a minimum notice period and severance/wind-down cost reimbursement.",
            "Uncapped Liability":
                "Negotiate a mutual liability cap tied to contract value or insurance coverage.",
        }
        return suggestions.get(category, "Review this clause with legal counsel.")
