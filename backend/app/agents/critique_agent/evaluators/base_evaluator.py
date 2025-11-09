"""
Base evaluator class for critique agent.
All evaluators inherit from this base class.
"""
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, Optional

from app.services.logger import app_logger


class BaseEvaluator(ABC):
    """Base class for all evaluators."""
    
    def __init__(self):
        """Initialize base evaluator."""
        self.logger = app_logger
    
    @abstractmethod
    def evaluate(
        self,
        ad_path: Path,
        brand_kit: Optional[Dict] = None,
        **kwargs
    ) -> Dict:
        """
        Evaluate an ad variation.
        
        Args:
            ad_path: Path to generated ad (image or video)
            brand_kit: Brand kit information for comparison
            **kwargs: Additional parameters
        
        Returns:
            Dictionary with evaluation results:
            - score: float (0.0 to 1.0)
            - feedback: str
            - issues: List[str] (optional)
            - suggestions: List[str] (optional)
        """
        pass
    
    def create_result(
        self,
        score: float,
        feedback: str,
        issues: Optional[list] = None,
        suggestions: Optional[list] = None,
        metadata: Optional[Dict] = None
    ) -> Dict:
        """
        Create standardized evaluation result.
        
        Args:
            score: Evaluation score (0.0 to 1.0)
            feedback: Detailed feedback
            issues: List of issues found
            suggestions: List of suggestions
            metadata: Additional metadata
        
        Returns:
            Standardized result dictionary
        """
        # Clamp score to 0.0-1.0 range
        score = max(0.0, min(1.0, score))
        
        result = {
            "score": score,
            "feedback": feedback,
            "issues": issues or [],
            "suggestions": suggestions or [],
        }
        
        if metadata:
            result["metadata"] = metadata
        
        return result
