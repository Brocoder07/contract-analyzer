"""
Suggestion deduplication using TF-IDF semantic similarity
Removes redundant suggestions while keeping the highest confidence version
"""

from typing import List
import logging
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer

logger = logging.getLogger(__name__)


class SuggestionDeduplicator:
    """
    Deduplicate suggestions using TF-IDF semantic similarity
    """
    
    def __init__(self, similarity_threshold: float = 0.85):
        """
        Initialize deduplicator
        
        Args:
            similarity_threshold: Threshold for considering suggestions similar (0.0-1.0)
                                 Higher values = more strict (fewer duplicates removed)
        """
        self.similarity_threshold = similarity_threshold
        self._tfidf = TfidfVectorizer(
            max_features=500,
            stop_words='english',
            ngram_range=(1, 2),
            lowercase=True,
            strip_accents='unicode'
        )
        logger.info("Initialized TF-IDF SuggestionDeduplicator")
    
    def deduplicate(self, suggestions: List) -> List:
        """
        Remove duplicate suggestions based on semantic similarity
        
        Args:
            suggestions: List of Suggestion objects
            
        Returns:
            Deduplicated list with only unique suggestions
        """
        if not suggestions or len(suggestions) <= 1:
            return suggestions
        
        logger.info(f"Deduplicating {len(suggestions)} suggestions with threshold {self.similarity_threshold}")
        
        # Extract suggestion texts
        texts = [s.suggestion_text for s in suggestions]
        
        # Compute similarity matrix
        similarity_matrix = self._compute_similarity_tfidf(texts)
        
        # Find and remove duplicates
        unique_indices = self._find_unique_indices(similarity_matrix, suggestions)
        
        deduplicated = [suggestions[i] for i in sorted(unique_indices)]
        
        logger.info(f"Reduced from {len(suggestions)} to {len(deduplicated)} suggestions")
        return deduplicated
    
    def _compute_similarity_tfidf(self, texts: List[str]) -> np.ndarray:
        """
        Compute similarity matrix using TF-IDF
        
        Args:
            texts: List of suggestion texts
            
        Returns:
            Similarity matrix (n x n)
        """
        try:
            # Generate TF-IDF vectors
            tfidf_matrix = self._tfidf.fit_transform(texts)
            
            # Compute cosine similarity
            similarity_matrix = cosine_similarity(tfidf_matrix)
            
            return similarity_matrix
        
        except Exception as e:
            logger.error(f"TF-IDF similarity failed: {e}, returning identity matrix")
            # Return identity matrix (no duplicates found)
            return np.eye(len(texts))
    
    def _find_unique_indices(
        self, 
        similarity_matrix: np.ndarray, 
        suggestions: List
    ) -> set:
        """
        Find indices of unique suggestions to keep
        
        For similar suggestions, keeps the one with highest confidence
        
        Args:
            similarity_matrix: Similarity matrix (n x n)
            suggestions: List of Suggestion objects
            
        Returns:
            Set of indices to keep
        """
        n = len(suggestions)
        keep_indices = set(range(n))
        
        # Process each pair of suggestions
        for i in range(n):
            if i not in keep_indices:
                continue
            
            for j in range(i + 1, n):
                if j not in keep_indices:
                    continue
                
                # Check if suggestions are similar
                similarity = similarity_matrix[i][j]
                
                if similarity >= self.similarity_threshold:
                    # They're similar - keep the one with higher confidence
                    if suggestions[i].confidence >= suggestions[j].confidence:
                        # Keep i, remove j
                        keep_indices.discard(j)
                        logger.debug(
                            f"Removing suggestion {j} (similar to {i}, "
                            f"similarity={similarity:.2f})"
                        )
                    else:
                        # Keep j, remove i
                        keep_indices.discard(i)
                        logger.debug(
                            f"Removing suggestion {i} (similar to {j}, "
                            f"similarity={similarity:.2f})"
                        )
                        break  # Move to next i since we removed it
        
        return keep_indices
    
    def compute_pairwise_similarity(self, text1: str, text2: str) -> float:
        """
        Compute similarity between two texts
        
        Args:
            text1: First text
            text2: Second text
            
            
        Returns:
            Similarity score (0.0-1.0)
        """
        try:
            tfidf_matrix = self._tfidf.fit_transform([text1, text2])
            similarity = cosine_similarity(tfidf_matrix)[0][1]
            return float(similarity)
        except Exception as e:
            logger.error(f"Pairwise similarity failed: {e}")
            return 0.0


class SimpleDeduplicator:
    """
    Simple deduplicator using exact string matching and basic text normalization
    Fallback option if ML-based similarity is not desired
    """
    
    def __init__(self):
        logger.info("Initialized SimpleDeduplicator (exact matching)")
    
    def deduplicate(self, suggestions: List) -> List:
        """
        Remove exact duplicate suggestions
        
        Args:
            suggestions: List of Suggestion objects
            
        Returns:
            Deduplicated list
        """
        if not suggestions or len(suggestions) <= 1:
            return suggestions
        
        seen_texts = {}
        unique_suggestions = []
        
        for suggestion in suggestions:
            # Normalize text for comparison
            normalized = self._normalize_text(suggestion.suggestion_text)
            
            if normalized not in seen_texts:
                seen_texts[normalized] = suggestion
                unique_suggestions.append(suggestion)
            else:
                # Keep the one with higher confidence
                existing = seen_texts[normalized]
                if suggestion.confidence > existing.confidence:
                    # Replace with higher confidence version
                    unique_suggestions.remove(existing)
                    unique_suggestions.append(suggestion)
                    seen_texts[normalized] = suggestion
        
        logger.info(f"Simple dedup: {len(suggestions)} -> {len(unique_suggestions)}")
        return unique_suggestions
    
    @staticmethod
    def _normalize_text(text: str) -> str:
        """Normalize text for comparison"""
        # Convert to lowercase, remove extra whitespace
        return ' '.join(text.lower().split())