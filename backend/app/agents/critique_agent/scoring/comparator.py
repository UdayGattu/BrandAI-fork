"""
Variation comparator for comparing multiple ad variations.
"""
from typing import Dict, List, Optional
from pathlib import Path

from app.models.response import VariationResult
from app.services.logger import app_logger


class VariationComparator:
    """Compare multiple ad variations."""
    
    def __init__(self):
        """Initialize comparator."""
        self.logger = app_logger
    
    def compare_variations(
        self,
        variation_results: List[VariationResult]
    ) -> Dict:
        """
        Compare multiple variations and identify best/worst.
        
        Args:
            variation_results: List of VariationResult objects
        
        Returns:
            Dictionary with comparison results:
            - best: VariationResult
            - worst: VariationResult
            - average_score: float
            - score_range: tuple (min, max)
        """
        if not variation_results:
            return {
                "best": None,
                "worst": None,
                "average_score": 0.0,
                "score_range": (0.0, 0.0)
            }
        
        # Sort by overall score (descending)
        sorted_variations = sorted(
            variation_results,
            key=lambda v: v.overall_score,
            reverse=True
        )
        
        scores = [v.overall_score for v in variation_results]
        average_score = sum(scores) / len(scores) if scores else 0.0
        score_range = (min(scores), max(scores)) if scores else (0.0, 0.0)
        
        return {
            "best": sorted_variations[0],
            "worst": sorted_variations[-1],
            "average_score": average_score,
            "score_range": score_range,
            "total_variations": len(variation_results)
        }
    
    def get_dimension_comparison(
        self,
        variation_results: List[VariationResult],
        dimension: str
    ) -> Dict:
        """
        Compare variations on a specific dimension.
        
        Args:
            variation_results: List of VariationResult objects
            dimension: Dimension name to compare
        
        Returns:
            Dictionary with dimension comparison:
            - best: VariationResult with highest dimension score
            - scores: List of (variation_id, score) tuples
            - average: float
        """
        dimension_scores = []
        
        for var in variation_results:
            # Find scorecard for this dimension
            scorecard = next(
                (sc for sc in var.scorecard if sc.dimension == dimension),
                None
            )
            
            if scorecard:
                dimension_scores.append((var.variation_id, scorecard.score))
        
        if not dimension_scores:
            return {
                "best": None,
                "scores": [],
                "average": 0.0
            }
        
        # Sort by score
        dimension_scores.sort(key=lambda x: x[1], reverse=True)
        
        # Find best variation
        best_id = dimension_scores[0][0]
        best_variation = next(
            (v for v in variation_results if v.variation_id == best_id),
            None
        )
        
        average = sum(score for _, score in dimension_scores) / len(dimension_scores)
        
        return {
            "best": best_variation,
            "scores": dimension_scores,
            "average": average
        }


# Global comparator instance
variation_comparator = VariationComparator()
