"""
Ranking system for ad variations.
Ranks variations based on overall and dimension scores.
"""
from typing import Dict, List, Optional
from app.models.response import VariationResult
from app.services.logger import app_logger


class VariationRanker:
    """Rank ad variations by quality."""
    
    def __init__(self):
        """Initialize ranker."""
        self.logger = app_logger
    
    def rank_variations(
        self,
        variation_results: List[VariationResult],
        ranking_strategy: str = "overall"
    ) -> List[VariationResult]:
        """
        Rank variations by score.
        
        Args:
            variation_results: List of VariationResult objects
            ranking_strategy: 'overall' (default) or 'weighted'
        
        Returns:
            List of VariationResult objects, ranked (best first)
        """
        if ranking_strategy == "overall":
            # Simple ranking by overall score
            ranked = sorted(
                variation_results,
                key=lambda v: v.overall_score,
                reverse=True
            )
        elif ranking_strategy == "weighted":
            # Weighted ranking (can be enhanced)
            ranked = sorted(
                variation_results,
                key=lambda v: self._calculate_weighted_score(v),
                reverse=True
            )
        else:
            ranked = variation_results
        
        # Assign ranks
        for i, variation in enumerate(ranked):
            variation.rank = i + 1
        
        return ranked
    
    def _calculate_weighted_score(self, variation: VariationResult) -> float:
        """
        Calculate weighted score for ranking.
        
        Can weight certain dimensions more heavily.
        For now, uses overall score.
        
        Args:
            variation: VariationResult object
        
        Returns:
            Weighted score
        """
        # For now, use overall score
        # Can be enhanced to weight safety, brand alignment more heavily
        return variation.overall_score
    
    def get_top_variations(
        self,
        variation_results: List[VariationResult],
        top_n: int = 1
    ) -> List[VariationResult]:
        """
        Get top N variations.
        
        Args:
            variation_results: List of VariationResult objects
            top_n: Number of top variations to return
        
        Returns:
            List of top N VariationResult objects
        """
        ranked = self.rank_variations(variation_results)
        return ranked[:top_n]
    
    def get_passed_variations(
        self,
        variation_results: List[VariationResult]
    ) -> List[VariationResult]:
        """
        Get only variations that passed evaluation.
        
        Args:
            variation_results: List of VariationResult objects
        
        Returns:
            List of passed VariationResult objects
        """
        return [v for v in variation_results if v.passed]


# Global ranker instance
variation_ranker = VariationRanker()
