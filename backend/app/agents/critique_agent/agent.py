"""
Critique Agent - Orchestrates evaluation of generated ads.
Evaluates ads across 4 dimensions: Brand, Quality, Clarity, Safety.
"""
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime, timezone
from concurrent.futures import ThreadPoolExecutor, as_completed

from app.agents.base_agent import BaseAgent
from app.agents.critique_agent.evaluators.brand_evaluator import brand_evaluator
from app.agents.critique_agent.evaluators.quality_evaluator import quality_evaluator
from app.agents.critique_agent.evaluators.clarity_evaluator import clarity_evaluator
from app.agents.critique_agent.evaluators.safety_evaluator import safety_evaluator
from app.agents.critique_agent.scoring.scorer import scorer
from app.agents.critique_agent.scoring.comparator import variation_comparator
from app.agents.critique_agent.scoring.ranker import variation_ranker
from app.models.response import VariationResult, CritiqueReport, ScoreCard
from app.services.logger import app_logger


class CritiqueAgent(BaseAgent):
    """Agent for critiquing generated ad variations."""
    
    def __init__(self):
        """Initialize critique agent."""
        super().__init__()
        self.logger = app_logger
        self.brand_evaluator = brand_evaluator
        self.quality_evaluator = quality_evaluator
        self.clarity_evaluator = clarity_evaluator
        self.safety_evaluator = safety_evaluator
        self.scorer = scorer
        self.comparator = variation_comparator
        self.ranker = variation_ranker
    
    def execute(
        self,
        ad_paths: List[str],
        brand_kit: Optional[Dict] = None,
        media_type: str = "image",
        run_id: str = None,
        user_prompt: Optional[str] = None,
        **kwargs
    ) -> Dict:
        """
        Execute critique evaluation (implements BaseAgent interface).
        
        Args:
            ad_paths: List of paths to generated ad variations
            brand_kit: Brand kit information for comparison
            media_type: 'image' or 'video'
            run_id: Run ID for tracking
            user_prompt: Original user prompt for ad generation (for context)
            **kwargs: Additional arguments
        
        Returns:
            Standardized result dictionary
        """
        self.log_start("critique", run_id=run_id, num_variations=len(ad_paths))
        
        try:
            # Evaluate all variations
            critique_report = self.evaluate_variations(
                ad_paths=ad_paths,
                brand_kit=brand_kit,
                media_type=media_type,
                run_id=run_id,
                user_prompt=user_prompt
            )
            
            passed_count = critique_report.passed_variations
            total_count = critique_report.total_variations
            
            self.log_complete(
                "critique",
                variations_evaluated=total_count,
                passed=passed_count
            )
            
            return self.create_result(
                success=True,
                data={
                    "critique_report": critique_report,
                    "passed_count": passed_count,
                    "total_count": total_count
                },
                metadata={
                    "run_id": run_id,
                    "media_type": media_type
                }
            )
        except Exception as e:
            self.log_error("critique", e, run_id=run_id)
            return self.create_result(
                success=False,
                error=str(e)
            )
    
    def evaluate_variations(
        self,
        ad_paths: List[str],
        brand_kit: Optional[Dict] = None,
        media_type: str = "image",
        run_id: Optional[str] = None,
        user_prompt: Optional[str] = None
    ) -> CritiqueReport:
        """
        Evaluate all ad variations and generate critique report.
        Uses parallel processing for faster evaluation.
        
        Args:
            ad_paths: List of paths to generated ad variations
            brand_kit: Brand kit information
            media_type: 'image' or 'video'
            run_id: Run ID
            user_prompt: Original user prompt for ad generation (for context)
        
        Returns:
            CritiqueReport with all evaluation results
        """
        self.logger.info(f"Evaluating {len(ad_paths)} {media_type} variations (parallel processing)")
        
        variation_results = []
        
        # Evaluate each variation
        for i, ad_path_str in enumerate(ad_paths):
            variation_id = f"var_{i+1}"
            ad_path = Path(ad_path_str)
            
            if not ad_path.exists():
                self.logger.warning(f"Ad file not found: {ad_path}")
                continue
            
            self.logger.info(f"Evaluating variation {variation_id}: {ad_path.name}")
            
            # Run all evaluators in parallel
            with ThreadPoolExecutor(max_workers=4) as executor:
                # Submit all evaluators
                brand_future = executor.submit(
                    self.brand_evaluator.evaluate,
                    ad_path, brand_kit, media_type, user_prompt=user_prompt
                )
                quality_future = executor.submit(
                    self.quality_evaluator.evaluate,
                    ad_path, brand_kit, media_type, user_prompt=user_prompt
                )
                clarity_future = executor.submit(
                    self.clarity_evaluator.evaluate,
                    ad_path, brand_kit, media_type, user_prompt=user_prompt
                )
                safety_future = executor.submit(
                    self.safety_evaluator.evaluate,
                    ad_path, brand_kit, media_type, user_prompt=user_prompt
                )
                
                # Wait for all to complete and get results
                brand_result = brand_future.result()
                quality_result = quality_future.result()
                clarity_result = clarity_future.result()
                safety_result = safety_future.result()
            
            # Create scorecards
            scorecards = self.scorer.create_scorecards_from_evaluations({
                "brand_alignment": brand_result,
                "visual_quality": quality_result,
                "message_clarity": clarity_result,
                "safety_ethics": safety_result
            })
            
            # Calculate overall score
            dimension_scores = {
                "brand_alignment": brand_result["score"],
                "visual_quality": quality_result["score"],
                "message_clarity": clarity_result["score"],
                "safety_ethics": safety_result["score"]
            }
            
            overall_score = self.scorer.calculate_overall_score(dimension_scores)
            
            # Determine pass/fail
            passed = self.scorer.determine_pass_fail(overall_score, dimension_scores)
            
            # Create variation result
            variation_result = VariationResult(
                variation_id=variation_id,
                file_path=str(ad_path),
                overall_score=overall_score,
                scorecard=scorecards,
                passed=passed
            )
            
            variation_results.append(variation_result)
        
        # Rank variations
        ranked_variations = self.ranker.rank_variations(variation_results)
        
        # Get best variation
        best_variation = ranked_variations[0] if ranked_variations else None
        
        # Count passed/failed
        passed_count = sum(1 for v in variation_results if v.passed)
        failed_count = len(variation_results) - passed_count
        
        # Create critique report
        critique_report = CritiqueReport(
            run_id=run_id or "unknown",
            total_variations=len(variation_results),
            passed_variations=passed_count,
            failed_variations=failed_count,
            best_variation=best_variation,
            all_variations=ranked_variations,
            generated_at=datetime.now(timezone.utc)
        )
        
        self.logger.info(
            f"Critique complete: {passed_count}/{len(variation_results)} variations passed"
        )
        
        return critique_report
    
    def evaluate_single(
        self,
        ad_path: Path,
        brand_kit: Optional[Dict] = None,
        media_type: str = "image"
    ) -> Dict:
        """
        Evaluate a single ad variation.
        
        Args:
            ad_path: Path to ad file
            brand_kit: Brand kit information
            media_type: 'image' or 'video'
        
        Returns:
            Evaluation result dictionary
        """
        return self.evaluate_variations(
            ad_paths=[str(ad_path)],
            brand_kit=brand_kit,
            media_type=media_type
        )


# Global critique agent instance
critique_agent = CritiqueAgent()
