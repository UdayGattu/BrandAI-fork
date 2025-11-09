"""
Brand alignment evaluator.
Evaluates logo presence, color consistency, and tone matching.
"""
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from app.agents.critique_agent.evaluators.base_evaluator import BaseEvaluator
from app.agents.critique_agent.analyzers.image_processor import image_processor
from app.agents.critique_agent.analyzers.clip_analyzer import clip_analyzer
from app.agents.critique_agent.analyzers.vision_analyzer import vision_analyzer
from app.services.logger import app_logger


class BrandEvaluator(BaseEvaluator):
    """Evaluate brand alignment of generated ads."""
    
    def __init__(self):
        """Initialize brand evaluator."""
        super().__init__()
        self.image_processor = image_processor
        self.clip_analyzer = clip_analyzer
        self.vision_analyzer = vision_analyzer
    
    def evaluate(
        self,
        ad_path: Path,
        brand_kit: Optional[Dict] = None,
        media_type: str = "image",
        **kwargs
    ) -> Dict:
        """
        Evaluate brand alignment of ad.
        
        Args:
            ad_path: Path to generated ad
            brand_kit: Brand kit information
            media_type: 'image' or 'video'
            **kwargs: Additional parameters
        
        Returns:
            Evaluation result dictionary
        """
        self.logger.info(f"Evaluating brand alignment for: {ad_path}")
        
        if not brand_kit:
            return self.create_result(
                score=0.5,
                feedback="No brand kit provided for comparison",
                issues=["Missing brand kit data"]
            )
        
        try:
            scores = []
            issues = []
            suggestions = []
            feedback_parts = []
            
            # 1. Logo evaluation
            logo_score, logo_feedback, logo_issues = self._evaluate_logo(
                ad_path, brand_kit, media_type
            )
            scores.append(logo_score)
            if logo_issues:
                issues.extend(logo_issues)
            feedback_parts.append(logo_feedback)
            
            # 2. Color consistency evaluation
            color_score, color_feedback, color_issues, color_suggestions = self._evaluate_colors(
                ad_path, brand_kit, media_type
            )
            scores.append(color_score)
            if color_issues:
                issues.extend(color_issues)
            if color_suggestions:
                suggestions.extend(color_suggestions)
            feedback_parts.append(color_feedback)
            
            # 3. Tone evaluation (using Vision Analyzer)
            user_prompt = kwargs.get("user_prompt")
            tone_score, tone_feedback, tone_issues = self._evaluate_tone(
                ad_path, brand_kit, media_type, user_prompt=user_prompt
            )
            scores.append(tone_score)
            if tone_issues:
                issues.extend(tone_issues)
            feedback_parts.append(tone_feedback)
            
            # Calculate overall brand alignment score
            overall_score = sum(scores) / len(scores) if scores else 0.0
            
            # Combine feedback
            feedback = " | ".join(feedback_parts)
            
            return self.create_result(
                score=overall_score,
                feedback=feedback,
                issues=issues if issues else None,
                suggestions=suggestions if suggestions else None,
                metadata={
                    "logo_score": logo_score,
                    "color_score": color_score,
                    "tone_score": tone_score
                }
            )
        except Exception as e:
            self.logger.error(f"Error evaluating brand alignment: {e}")
            return self.create_result(
                score=0.0,
                feedback=f"Error during brand evaluation: {str(e)}",
                issues=[f"Evaluation error: {str(e)}"]
            )
    
    def _evaluate_logo(
        self,
        ad_path: Path,
        brand_kit: Dict,
        media_type: str
    ) -> Tuple[float, str, List[str]]:
        """Evaluate logo presence and matching."""
        logo_path = brand_kit.get("logo", {}).get("file_path")
        
        if not logo_path or not Path(logo_path).exists():
            return 0.5, "Logo reference not available", ["No logo reference provided"]
        
        try:
            # For videos, rely on Gemini Video API (handles logo detection)
            # For images, use CLIP for more accurate matching
            if media_type == "video":
                # Gemini Video will handle logo detection in comprehensive analysis
                # Return moderate score, let Gemini handle detailed evaluation
                return 0.7, "Logo detection handled by Gemini Video analysis", []
            else:
                # For images, use CLIP for accurate logo matching
                logo_match = clip_analyzer.match_logo(ad_path, Path(logo_path))
                
                similarity = logo_match.get("similarity_score", 0.0)
                logo_detected = logo_match.get("logo_detected", False)
                
                if logo_detected:
                    score = min(1.0, similarity * 1.2)  # Boost if detected
                    feedback = f"Logo detected (similarity: {similarity:.2f})"
                    issues = []
                else:
                    score = similarity * 0.5  # Penalize if not detected
                    feedback = f"Logo not clearly detected (similarity: {similarity:.2f})"
                    issues = ["Logo may not be visible or recognizable"]
                
                return score, feedback, issues
        except Exception as e:
            self.logger.error(f"Error evaluating logo: {e}")
            return 0.5, "Logo evaluation error", [str(e)]
    
    def _evaluate_colors(
        self,
        ad_path: Path,
        brand_kit: Dict,
        media_type: str
    ) -> Tuple[float, str, List[str], List[str]]:
        """Evaluate color consistency with brand."""
        brand_colors = brand_kit.get("colors", {}).get("color_palette", [])
        
        if not brand_colors:
            return 0.5, "No brand colors available", ["No brand color palette"], []
        
        try:
            # Extract colors from ad
            if media_type == "image":
                image = image_processor.load_image(ad_path)
                if image is None:
                    return 0.0, "Failed to load image", ["Image load error"], []
                ad_colors = image_processor.extract_colors(image)
            else:
                # For video, extract from first frame
                frame = image_processor.extract_frame_from_video(ad_path)
                if frame is None:
                    return 0.0, "Failed to extract video frame", ["Video frame error"], []
                ad_colors = image_processor.extract_colors(frame)
            
            ad_color_list = ad_colors.get("dominant_colors", [])
            
            if not ad_color_list:
                return 0.0, "No colors extracted from ad", ["Color extraction failed"], []
            
            # Compare colors (simple hex comparison)
            # Check if any brand colors appear in ad colors
            matches = 0
            for brand_color in brand_colors[:3]:  # Top 3 brand colors
                # Normalize hex codes (remove #, lowercase)
                brand_hex = brand_color.replace("#", "").lower()
                for ad_color in ad_color_list[:5]:  # Top 5 ad colors
                    ad_hex = ad_color.replace("#", "").lower()
                    # Check if colors are similar (within tolerance)
                    if self._colors_similar(brand_hex, ad_hex, tolerance=30):
                        matches += 1
                        break
            
            # Score based on matches
            max_matches = min(3, len(brand_colors))
            score = matches / max_matches if max_matches > 0 else 0.0
            
            if score >= 0.7:
                feedback = f"Good color consistency ({matches}/{max_matches} brand colors found)"
                issues = []
            elif score >= 0.4:
                feedback = f"Moderate color consistency ({matches}/{max_matches} brand colors found)"
                issues = ["Some brand colors may not be prominent"]
                suggestions = ["Consider using more brand colors from palette"]
            else:
                feedback = f"Poor color consistency ({matches}/{max_matches} brand colors found)"
                issues = ["Brand colors not well represented"]
                suggestions = ["Use brand color palette more prominently"]
            
            return score, feedback, issues, suggestions
        except Exception as e:
            self.logger.error(f"Error evaluating colors: {e}")
            return 0.0, "Color evaluation error", [str(e)], []
    
    def _colors_similar(self, hex1: str, hex2: str, tolerance: int = 30) -> bool:
        """Check if two hex colors are similar within tolerance."""
        try:
            # Convert hex to RGB
            r1, g1, b1 = int(hex1[0:2], 16), int(hex1[2:4], 16), int(hex1[4:6], 16)
            r2, g2, b2 = int(hex2[0:2], 16), int(hex2[2:4], 16), int(hex2[4:6], 16)
            
            # Calculate distance
            distance = ((r1 - r2) ** 2 + (g1 - g2) ** 2 + (b1 - b2) ** 2) ** 0.5
            
            return distance <= tolerance
        except:
            return False
    
    def _evaluate_tone(
        self,
        ad_path: Path,
        brand_kit: Dict,
        media_type: str,
        user_prompt: Optional[str] = None
    ) -> Tuple[float, str, List[str]]:
        """Evaluate tone matching using Vision Analyzer."""
        try:
            # Use Vision Analyzer to assess tone
            analysis = vision_analyzer.analyze_advertisement(
                ad_path, media_type, brand_kit, user_prompt=user_prompt
            )
            
            if not analysis.get("success"):
                return 0.5, "Tone evaluation unavailable", ["Vision analysis failed"]
            
            # Parse analysis for tone information
            analysis_data = analysis.get("analysis", {})
            raw_text = analysis.get("raw_text", "")
            
            # Simple heuristic: check if analysis mentions brand alignment
            tone_keywords = ["professional", "consistent", "aligned", "matches", "appropriate"]
            negative_keywords = ["inconsistent", "mismatch", "off-brand", "inappropriate"]
            
            tone_score = 0.7  # Default moderate score
            feedback = "Tone assessment completed"
            issues = []
            
            # Check for positive/negative indicators
            text_lower = raw_text.lower()
            positive_count = sum(1 for kw in tone_keywords if kw in text_lower)
            negative_count = sum(1 for kw in negative_keywords if kw in text_lower)
            
            if positive_count > negative_count:
                tone_score = min(1.0, 0.7 + (positive_count * 0.1))
                feedback = "Tone appears aligned with brand"
            elif negative_count > positive_count:
                tone_score = max(0.0, 0.7 - (negative_count * 0.2))
                feedback = "Tone may not align well with brand"
                issues.append("Tone mismatch detected")
            
            return tone_score, feedback, issues
        except Exception as e:
            self.logger.error(f"Error evaluating tone: {e}")
            return 0.5, "Tone evaluation error", [str(e)]


# Global brand evaluator instance
brand_evaluator = BrandEvaluator()
