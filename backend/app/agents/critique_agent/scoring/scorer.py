"""
Scoring system for critique agent.
Calculates per-dimension and overall scores.
"""
from typing import Dict, List, Optional
from pathlib import Path

from app.models.response import ScoreCard
from app.services.logger import app_logger


class Scorer:
    """Calculate scores from evaluation results."""
    
    def __init__(self):
        """Initialize scorer."""
        self.logger = app_logger
    
    def calculate_overall_score(
        self,
        dimension_scores: Dict[str, float],
        weights: Optional[Dict[str, float]] = None
    ) -> float:
        """
        Calculate overall score from dimension scores.
        
        Args:
            dimension_scores: Dictionary of dimension -> score
            weights: Optional weights for each dimension (default: equal weights)
        
        Returns:
            Overall score (0.0 to 1.0)
        """
        if not dimension_scores:
            return 0.0
        
        # Default weights (equal)
        if weights is None:
            weights = {dim: 1.0 / len(dimension_scores) for dim in dimension_scores}
        
        # Normalize weights
        total_weight = sum(weights.get(dim, 0.0) for dim in dimension_scores)
        if total_weight == 0:
            total_weight = len(dimension_scores)
            weights = {dim: 1.0 / total_weight for dim in dimension_scores}
        
        # Calculate weighted average
        weighted_sum = sum(
            dimension_scores[dim] * weights.get(dim, 1.0 / len(dimension_scores))
            for dim in dimension_scores
        )
        
        overall_score = weighted_sum / total_weight if total_weight > 0 else 0.0
        
        # Ensure 0.0-1.0 range
        return max(0.0, min(1.0, overall_score))
    
    def create_scorecard(
        self,
        dimension: str,
        score: float,
        feedback: str,
        issues: Optional[List[str]] = None,
        suggestions: Optional[List[str]] = None
    ) -> ScoreCard:
        """
        Create a ScoreCard from evaluation results.
        
        Args:
            dimension: Dimension name (e.g., "brand_alignment")
            score: Score (0.0 to 1.0)
            feedback: Detailed feedback
            issues: List of issues
            suggestions: List of suggestions
        
        Returns:
            ScoreCard object
        """
        return ScoreCard(
            dimension=dimension,
            score=max(0.0, min(1.0, score)),
            feedback=feedback,
            issues=issues or [],
            suggestions=suggestions or []
        )
    
    def create_scorecards_from_evaluations(
        self,
        evaluations: Dict[str, Dict]
    ) -> List[ScoreCard]:
        """
        Create scorecards from multiple evaluation results.
        
        Args:
            evaluations: Dictionary of dimension -> evaluation result
        
        Returns:
            List of ScoreCard objects
        """
        scorecards = []
        
        for dimension, eval_result in evaluations.items():
            scorecard = self.create_scorecard(
                dimension=dimension,
                score=eval_result.get("score", 0.0),
                feedback=eval_result.get("feedback", ""),
                issues=eval_result.get("issues"),
                suggestions=eval_result.get("suggestions")
            )
            scorecards.append(scorecard)
        
        return scorecards
    
    def determine_pass_fail(
        self,
        overall_score: float,
        dimension_scores: Dict[str, float],
        min_overall: float = 0.6,
        min_dimension: float = 0.4
    ) -> bool:
        """
        Determine if ad passes or fails based on scores.
        
        Args:
            overall_score: Overall score
            dimension_scores: Dictionary of dimension -> score
            min_overall: Minimum overall score to pass
            min_dimension: Minimum score for any dimension
        
        Returns:
            True if passes, False if fails
        """
        # Check overall score
        if overall_score < min_overall:
            return False
        
        # Check all dimensions meet minimum
        for dim, score in dimension_scores.items():
            if score < min_dimension:
                return False
        
        return True


# Global scorer instance
scorer = Scorer()
