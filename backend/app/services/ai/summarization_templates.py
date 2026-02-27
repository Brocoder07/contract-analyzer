"""
Rule-based summarization templates and extractive summarization
Uses keyword extraction and sentence ranking for contract summarization
"""

import re
from typing import List, Dict
from collections import Counter
import logging

logger = logging.getLogger(__name__)


# Contract type detection patterns
CONTRACT_TYPE_PATTERNS = {
    "employment": [
        r"employment agreement",
        r"employment contract",
        r"employee",
        r"employer",
        r"job description",
        r"salary",
        r"compensation package"
    ],
    "nda": [
        r"non-disclosure agreement",
        r"confidentiality agreement",
        r"confidential information",
        r"proprietary information",
        r"trade secrets"
    ],
    "service": [
        r"service agreement",
        r"services agreement",
        r"statement of work",
        r"sow",
        r"consulting agreement",
        r"professional services"
    ],
    "lease": [
        r"lease agreement",
        r"rental agreement",
        r"landlord",
        r"tenant",
        r"premises",
        r"rent payment"
    ],
    "sales": [
        r"purchase agreement",
        r"sales agreement",
        r"buyer",
        r"seller",
        r"goods",
        r"merchandise"
    ],
    "license": [
        r"license agreement",
        r"licensing agreement",
        r"licensor",
        r"licensee",
        r"intellectual property",
        r"software license"
    ]
}

# Important section headers to look for
IMPORTANT_SECTIONS = [
    "definitions",
    "scope of work",
    "payment terms",
    "term and termination",
    "confidentiality",
    "intellectual property",
    "warranties",
    "limitation of liability",
    "indemnification",
    "governing law",
    "dispute resolution"
]

# Party detection patterns
PARTY_PATTERNS = [
    r"(?:between|by and between)\s+([A-Z][A-Za-z\s&,\.]+?)(?:\s+\(|,|\s+and)",
    r"(?:\"[A-Za-z\s]+\"\s*\()?([A-Z][A-Za-z\s&,\.]+?)\s*\)",
    r"(?:Client|Customer|Vendor|Supplier|Party):\s*([A-Z][A-Za-z\s&,\.]+)",
]

# Date patterns
DATE_PATTERNS = [
    r"\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b",
    r"\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4}\b",
    r"\b\d{1,2}\s+(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4}\b",
    r"(?:Effective Date|Start Date|End Date|Termination Date):\s*([^\n]+)"
]


def detect_contract_type(text: str) -> str:
    """
    Detect the type of contract based on keyword patterns
    
    Args:
        text: Contract text
        
    Returns:
        Contract type string
    """
    text_lower = text.lower()
    scores = {}
    
    for contract_type, patterns in CONTRACT_TYPE_PATTERNS.items():
        score = 0
        for pattern in patterns:
            matches = re.findall(pattern, text_lower)
            score += len(matches)
        scores[contract_type] = score
    
    if not scores or max(scores.values()) == 0:
        return "general"
    
    return max(scores, key=scores.get)


def extract_parties(text: str) -> List[str]:
    """
    Extract party names from contract
    
    Args:
        text: Contract text
        
    Returns:
        List of party names
    """
    parties = set()
    
    for pattern in PARTY_PATTERNS:
        matches = re.findall(pattern, text[:2000])  # Look in first 2000 chars
        for match in matches:
            cleaned = match.strip().strip('",.')
            if len(cleaned) > 3 and len(cleaned) < 100:
                parties.add(cleaned)
    
    return list(parties)[:5]  # Return max 5 parties


def extract_dates(text: str) -> List[str]:
    """
    Extract important dates from contract
    
    Args:
        text: Contract text
        
    Returns:
        List of dates
    """
    dates = set()
    
    for pattern in DATE_PATTERNS:
        matches = re.findall(pattern, text, re.IGNORECASE)
        for match in matches:
            if isinstance(match, tuple):
                match = match[0]
            cleaned = match.strip()
            if cleaned:
                dates.add(cleaned)
    
    return list(dates)[:10]  # Return max 10 dates


def calculate_sentence_importance(sentence: str, keywords: List[str]) -> float:
    """
    Calculate importance score for a sentence
    
    Args:
        sentence: Sentence text
        keywords: List of important keywords
        
    Returns:
        Importance score
    """
    score = 0.0
    sentence_lower = sentence.lower()
    
    # Check for important keywords
    for keyword in keywords:
        if keyword.lower() in sentence_lower:
            score += 2.0
    
    # Check for section headers
    for section in IMPORTANT_SECTIONS:
        if section in sentence_lower:
            score += 3.0
    
    # Prefer sentences with numbers (often important terms)
    if re.search(r'\d+', sentence):
        score += 1.0
    
    # Prefer sentences mentioning parties
    if re.search(r'\b(?:party|parties|client|vendor|supplier|customer)\b', sentence_lower):
        score += 1.5
    
    # Penalize very short or very long sentences
    word_count = len(sentence.split())
    if word_count < 5:
        score *= 0.5
    elif word_count > 50:
        score *= 0.7
    
    return score


def extract_keywords(text: str, top_n: int = 20) -> List[str]:
    """
    Extract most important keywords from text
    
    Args:
        text: Contract text
        top_n: Number of keywords to return
        
    Returns:
        List of keywords
    """
    # Remove common words
    stop_words = {
        'the', 'be', 'to', 'of', 'and', 'a', 'in', 'that', 'have', 'i',
        'it', 'for', 'not', 'on', 'with', 'he', 'as', 'you', 'do', 'at',
        'this', 'but', 'his', 'by', 'from', 'they', 'we', 'say', 'her', 'she',
        'or', 'an', 'will', 'my', 'one', 'all', 'would', 'there', 'their'
    }
    
    # Extract words
    words = re.findall(r'\b[a-z]{3,}\b', text.lower())
    
    # Filter and count
    filtered_words = [w for w in words if w not in stop_words]
    word_counts = Counter(filtered_words)
    
    # Return top keywords
    return [word for word, count in word_counts.most_common(top_n)]


def extractive_summarization(text: str, num_sentences: int = 5) -> Dict:
    """
    Create extractive summary by selecting most important sentences
    
    Args:
        text: Contract text
        num_sentences: Number of sentences to extract
        
    Returns:
        Dict with summary text and metadata
    """
    # Split into sentences
    sentences = re.split(r'(?<=[.!?])\s+', text)
    sentences = [s.strip() for s in sentences if len(s.strip()) > 20]
    
    if len(sentences) <= num_sentences:
        return {
            "summary": text,
            "sentences_used": len(sentences),
            "compression_ratio": 1.0
        }
    
    # Extract keywords
    keywords = extract_keywords(text)
    
    # Score sentences
    sentence_scores = []
    for i, sentence in enumerate(sentences):
        score = calculate_sentence_importance(sentence, keywords)
        
        # Prefer sentences from beginning and end
        if i < 3:
            score *= 1.5
        elif i >= len(sentences) - 3:
            score *= 1.3
        
        sentence_scores.append((score, sentence))
    
    # Sort by score and select top sentences
    sentence_scores.sort(reverse=True, key=lambda x: x[0])
    selected_sentences = [s for _, s in sentence_scores[:num_sentences]]
    
    # Reorder selected sentences to maintain original order
    ordered_sentences = []
    for sentence in sentences:
        if sentence in selected_sentences:
            ordered_sentences.append(sentence)
    
    summary_text = ' '.join(ordered_sentences)
    
    return {
        "summary": summary_text,
        "sentences_used": len(ordered_sentences),
        "compression_ratio": len(text) / len(summary_text) if summary_text else 1.0
    }