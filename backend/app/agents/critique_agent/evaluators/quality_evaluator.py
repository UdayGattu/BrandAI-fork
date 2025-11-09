"""
Visual quality evaluator.
Evaluates blur, artifacts, composition, and overall visual quality.
"""
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from app.agents.critique_agent.evaluators.base_evaluator import BaseEvaluator
from app.agents.critique_agent.analyzers.image_processor import image_processor
from app.agents.critique_agent.analyzers.vision_analyzer import vision_analyzer
from app.services.logger import app_logger


class QualityEvaluator(BaseEvaluator):
    """Evaluate visual quality of generated ads."""
    
    def __init__(self):
        """Initialize quality evaluator."""
        super().__init__()
        self.image_processor = image_processor
        self.vision_analyzer = vision_analyzer
    
    def evaluate(
        self,
        ad_path: Path,
        brand_kit: Optional[Dict] = None,
        media_type: str = "image",
        **kwargs
    ) -> Dict:
        """
        Evaluate visual quality of ad.
        
        Args:
            ad_path: Path to generated ad
            brand_kit: Brand kit information (optional)
            media_type: 'image' or 'video'
            **kwargs: Additional parameters
        
        Returns:
            Evaluation result dictionary
        """
        self.logger.info(f"Evaluating visual quality for: {ad_path}")
        
        try:
            scores = []
            issues = []
            suggestions = []
            feedback_parts = []
            
            # 1. Blur detection
            blur_score, blur_feedback, blur_issues, blur_suggestions = self._evaluate_blur(
                ad_path, media_type
            )
            scores.append(blur_score)
            if blur_issues:
                issues.extend(blur_issues)
            if blur_suggestions:
                suggestions.extend(blur_suggestions)
            feedback_parts.append(blur_feedback)
            
            # 2. Artifact detection
            artifact_score, artifact_feedback, artifact_issues, artifact_suggestions = self._evaluate_artifacts(
                ad_path, media_type
            )
            scores.append(artifact_score)
            if artifact_issues:
                issues.extend(artifact_issues)
            if artifact_suggestions:
                suggestions.extend(artifact_suggestions)
            feedback_parts.append(artifact_feedback)
            
            # 3. Composition analysis
            composition_score, composition_feedback, composition_issues = self._evaluate_composition(
                ad_path, media_type
            )
            scores.append(composition_score)
            if composition_issues:
                issues.extend(composition_issues)
            feedback_parts.append(composition_feedback)
            
            # Calculate overall quality score
            overall_score = sum(scores) / len(scores) if scores else 0.0
            
            # Combine feedback
            feedback = " | ".join(feedback_parts)
            
            return self.create_result(
                score=overall_score,
                feedback=feedback,
                issues=issues if issues else None,
                suggestions=suggestions if suggestions else None,
                metadata={
                    "blur_score": blur_score,
                    "artifact_score": artifact_score,
                    "composition_score": composition_score
                }
            )
        except Exception as e:
            self.logger.error(f"Error evaluating visual quality: {e}")
            return self.create_result(
                score=0.0,
                feedback=f"Error during quality evaluation: {str(e)}",
                issues=[f"Evaluation error: {str(e)}"]
            )
    
    def _evaluate_blur(
        self,
        ad_path: Path,
        media_type: str
    ) -> Tuple[float, str, List[str], List[str]]:
        """Evaluate blur in image/video."""
        try:
            if media_type == "image":
                image = self.image_processor.load_image(ad_path)
                if image is None:
                    return 0.0, "Failed to load image", ["Image load error"], []
                blur_result = self.image_processor.detect_blur(image)
            else:
                # For video, check first frame
                frame = self.image_processor.extract_frame_from_video(ad_path)
                if frame is None:
                    return 0.0, "Failed to extract frame", ["Frame extraction error"], []
                blur_result = self.image_processor.detect_blur(frame)
            
            blur_score_value = blur_result.get("blur_score", 0.0)
            is_blurry = blur_result.get("is_blurry", True)
            threshold = blur_result.get("threshold", 100.0)
            
            # Convert blur score to quality score (higher blur_score = better quality)
            # Normalize: blur_score / threshold, capped at 1.0
            quality_score = min(1.0, blur_score_value / threshold)
            
            if not is_blurry:
                feedback = f"Image is sharp (blur score: {blur_score_value:.1f})"
                issues = []
                suggestions = []
            elif quality_score >= 0.7:
                feedback = f"Minor blur detected (blur score: {blur_score_value:.1f})"
                issues = []
                suggestions = ["Consider sharpening the image"]
            elif quality_score >= 0.4:
                feedback = f"Moderate blur detected (blur score: {blur_score_value:.1f})"
                issues = ["Image appears blurry"]
                suggestions = ["Apply sharpening filter", "Regenerate with higher quality settings"]
            else:
                feedback = f"Significant blur detected (blur score: {blur_score_value:.1f})"
                issues = ["Image is too blurry"]
                suggestions = ["Regenerate with better quality", "Apply aggressive sharpening"]
            
            return quality_score, feedback, issues, suggestions
        except Exception as e:
            self.logger.error(f"Error evaluating blur: {e}")
            return 0.5, "Blur evaluation error", [str(e)], []
    
    def _evaluate_artifacts(
        self,
        ad_path: Path,
        media_type: str
    ) -> Tuple[float, str, List[str], List[str]]:
        """Evaluate artifacts in image/video."""
        try:
            if media_type == "image":
                image = self.image_processor.load_image(ad_path)
                if image is None:
                    return 0.0, "Failed to load image", ["Image load error"], []
                quality_result = self.image_processor.check_basic_quality(image)
            else:
                # For video, check first frame
                frame = self.image_processor.extract_frame_from_video(ad_path)
                if frame is None:
                    return 0.0, "Failed to extract frame", ["Frame extraction error"], []
                quality_result = self.image_processor.check_basic_quality(frame)
            
            has_artifacts = quality_result.get("has_artifacts", False)
            contrast = quality_result.get("contrast", 0.0)
            
            # Score based on artifact detection and contrast
            # Low contrast might indicate artifacts
            if has_artifacts:
                score = 0.3
                feedback = "Artifacts detected in image"
                issues = ["Visual artifacts present"]
                suggestions = ["Regenerate with different settings", "Apply denoising"]
            elif contrast < 20:
                score = 0.6
                feedback = "Low contrast may indicate quality issues"
                issues = ["Low contrast detected"]
                suggestions = ["Increase contrast", "Check for compression artifacts"]
            else:
                score = 1.0
                feedback = "No significant artifacts detected"
                issues = []
                suggestions = []
            
            return score, feedback, issues, suggestions
        except Exception as e:
            self.logger.error(f"Error evaluating artifacts: {e}")
            return 0.5, "Artifact evaluation error", [str(e)], []
    
    def _evaluate_composition(
        self,
        ad_path: Path,
        media_type: str
    ) -> Tuple[float, str, List[str]]:
        """Evaluate composition of image/video."""
        try:
            if media_type == "image":
                image = self.image_processor.load_image(ad_path)
                if image is None:
                    return 0.0, "Failed to load image", ["Image load error"]
                quality_result = self.image_processor.check_basic_quality(image)
            else:
                frame = self.image_processor.extract_frame_from_video(ad_path)
                if frame is None:
                    return 0.0, "Failed to extract frame", ["Frame extraction error"]
                quality_result = self.image_processor.check_basic_quality(frame)
            
            resolution = quality_result.get("resolution", (0, 0))
            aspect_ratio = quality_result.get("aspect_ratio", 0.0)
            
            # Evaluate composition based on resolution and aspect ratio
            width, height = resolution
            
            # Check resolution (minimum quality threshold)
            min_resolution = 512  # Minimum dimension
            if width < min_resolution or height < min_resolution:
                score = 0.4
                feedback = f"Low resolution ({width}x{height})"
                issues = ["Resolution too low for professional use"]
            # Check aspect ratio (common ad ratios: 16:9, 9:16, 1:1)
            elif 0.5 <= aspect_ratio <= 2.0:  # Reasonable range
                score = 0.8
                feedback = f"Good composition (aspect ratio: {aspect_ratio:.2f})"
                issues = []
            else:
                score = 0.6
                feedback = f"Unusual aspect ratio ({aspect_ratio:.2f})"
                issues = ["Aspect ratio may not be optimal for ads"]
            
            return score, feedback, issues
        except Exception as e:
            self.logger.error(f"Error evaluating composition: {e}")
            return 0.5, "Composition evaluation error", [str(e)]


# Global quality evaluator instance
quality_evaluator = QualityEvaluator()
