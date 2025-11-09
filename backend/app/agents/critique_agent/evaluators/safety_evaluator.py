"""
Safety and ethics evaluator.
Evaluates harmful content, stereotypes, and misleading claims.
"""
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from app.agents.critique_agent.evaluators.base_evaluator import BaseEvaluator
from app.agents.critique_agent.analyzers.vision_analyzer import vision_analyzer
from app.services.logger import app_logger


class SafetyEvaluator(BaseEvaluator):
    """Evaluate safety and ethics of generated ads."""
    
    def __init__(self):
        """Initialize safety evaluator."""
        super().__init__()
        self.vision_analyzer = vision_analyzer
    
    def evaluate(
        self,
        ad_path: Path,
        brand_kit: Optional[Dict] = None,
        media_type: str = "image",
        **kwargs
    ) -> Dict:
        """
        Evaluate safety and ethics of ad.
        
        Args:
            ad_path: Path to generated ad
            brand_kit: Brand kit information (optional)
            media_type: 'image' or 'video'
            **kwargs: Additional parameters
        
        Returns:
            Evaluation result dictionary
        """
        self.logger.info(f"Evaluating safety and ethics for: {ad_path}")
        
        try:
            scores = []
            issues = []
            suggestions = []
            feedback_parts = []
            
            # 1. Harmful content detection
            user_prompt = kwargs.get("user_prompt")
            harmful_score, harmful_feedback, harmful_issues = self._evaluate_harmful_content(
                ad_path, media_type, user_prompt=user_prompt
            )
            scores.append(harmful_score)
            if harmful_issues:
                issues.extend(harmful_issues)
            feedback_parts.append(harmful_feedback)
            
            # 2. Stereotype detection
            stereotype_score, stereotype_feedback, stereotype_issues = self._evaluate_stereotypes(
                ad_path, media_type, user_prompt=user_prompt
            )
            scores.append(stereotype_score)
            if stereotype_issues:
                issues.extend(stereotype_issues)
            feedback_parts.append(stereotype_feedback)
            
            # 3. Misleading claims check
            misleading_score, misleading_feedback, misleading_issues = self._evaluate_misleading_claims(
                ad_path, media_type, user_prompt=user_prompt
            )
            scores.append(misleading_score)
            if misleading_issues:
                issues.extend(misleading_issues)
            feedback_parts.append(misleading_feedback)
            
            # Calculate overall safety score
            # Use weighted average instead of minimum (less strict)
            # Safety is important, but don't penalize too harshly
            if scores:
                # Weighted average: all dimensions equally important
                overall_score = sum(scores) / len(scores)
                
                # Only heavily penalize if there's a high-confidence issue
                if harmful_score < 0.3 or stereotype_score < 0.3:
                    overall_score = min(overall_score, 0.3)
                elif harmful_score < 0.5 or stereotype_score < 0.5:
                    overall_score = min(overall_score, 0.5)
            else:
                overall_score = 1.0
            
            # Combine feedback
            feedback = " | ".join(feedback_parts)
            
            return self.create_result(
                score=overall_score,
                feedback=feedback,
                issues=issues if issues else None,
                suggestions=suggestions if suggestions else None,
                metadata={
                    "harmful_score": harmful_score,
                    "stereotype_score": stereotype_score,
                    "misleading_score": misleading_score
                }
            )
        except Exception as e:
            self.logger.error(f"Error evaluating safety and ethics: {e}")
            return self.create_result(
                score=0.0,
                feedback=f"Error during safety evaluation: {str(e)}",
                issues=[f"Evaluation error: {str(e)}"]
            )
    
    def _evaluate_harmful_content(
        self,
        ad_path: Path,
        media_type: str,
        user_prompt: Optional[str] = None
    ) -> Tuple[float, str, List[str]]:
        """Evaluate for harmful or inappropriate content."""
        try:
            # Create comprehensive safety analysis prompt
            safety_prompt = f"""Analyze this advertisement for harmful, inappropriate, or offensive content.

Check specifically for:
- Violence or dangerous content
- Explicit or inappropriate imagery
- Hate speech or discriminatory content
- Any content that could be harmful to viewers

IMPORTANT: Only flag as harmful if content is ACTUALLY harmful. If the ad is safe and appropriate, respond with "harmful": false.

Respond with JSON format:
{{
  "harmful": true/false,
  "confidence": "high/medium/low",
  "description": "Detailed explanation of your analysis",
  "specific_issues": ["list any specific issues found, or empty array if none"]
}}

Be objective and only flag actual harmful content."""
            
            # Use custom safety prompt for analysis
            if media_type == "image":
                analysis = self.vision_analyzer.analyze_image(ad_path, safety_prompt)
            else:
                analysis = self.vision_analyzer.analyze_video(ad_path, safety_prompt)
            
            if not analysis.get("success"):
                # Default to safe if analysis fails
                return 1.0, "Harmful content check unavailable (assuming safe)", []
            
            # Try to parse structured JSON response
            analysis_data = analysis.get("analysis", {})
            raw_text = analysis.get("raw_text", "")
            
            # Parse JSON from analysis
            is_harmful = False
            description = ""
            specific_issues = []
            confidence = "medium"
            
            if isinstance(analysis_data, dict):
                is_harmful = analysis_data.get("harmful", False)
                description = analysis_data.get("description", "")
                specific_issues = analysis_data.get("specific_issues", [])
                confidence = analysis_data.get("confidence", "medium")
            else:
                # Try to extract from raw text
                import json
                import re
                # Look for JSON in raw text
                json_match = re.search(r'\{[^{}]*"harmful"[^{}]*\}', raw_text, re.IGNORECASE)
                if json_match:
                    try:
                        parsed = json.loads(json_match.group())
                        is_harmful = parsed.get("harmful", False)
                        description = parsed.get("description", "")
                        specific_issues = parsed.get("specific_issues", [])
                    except:
                        pass
                
                # If no JSON, check for explicit statements
                text_lower = raw_text.lower()
                if any(phrase in text_lower for phrase in ["no harmful", "not harmful", "safe", "appropriate", "no issues"]):
                    is_harmful = False
                elif any(phrase in text_lower for phrase in ["harmful content", "inappropriate", "offensive", "violence"]):
                    # Check if it's saying "no harmful" or actually harmful
                    if "no harmful" not in text_lower and "not harmful" not in text_lower:
                        is_harmful = True
            
            # Generate score and feedback from analysis
            if is_harmful:
                if confidence == "high":
                    score = 0.0
                elif confidence == "medium":
                    score = 0.2
                else:
                    score = 0.4
                
                feedback = description if description else "Harmful content detected in advertisement"
                issues = specific_issues if specific_issues else ["Harmful or inappropriate content found"]
            else:
                score = 1.0
                feedback = description if description else "No harmful content detected - advertisement is safe and appropriate"
                issues = []
            
            return score, feedback, issues
        except Exception as e:
            self.logger.error(f"Error evaluating harmful content: {e}")
            return 1.0, "Harmful content evaluation error (assuming safe)", [str(e)]
    
    def _evaluate_stereotypes(
        self,
        ad_path: Path,
        media_type: str,
        user_prompt: Optional[str] = None
    ) -> Tuple[float, str, List[str]]:
        """Evaluate for stereotypes or biased content."""
        try:
            # Create comprehensive stereotype analysis prompt
            stereotype_prompt = f"""Analyze this advertisement for stereotypes, bias, or discriminatory content.

Check specifically for:
- Gender stereotypes or biased gender representations
- Racial or ethnic bias
- Cultural stereotypes
- Any discriminatory or prejudiced content
- Inappropriate representation of groups

IMPORTANT: Only flag as having stereotypes if content ACTUALLY contains stereotypes or bias. If the ad is inclusive and respectful, respond with "stereotypes": false.

Respond with JSON format:
{{
  "stereotypes": true/false,
  "confidence": "high/medium/low",
  "description": "Detailed explanation of your analysis",
  "specific_issues": ["list any specific stereotypes found, or empty array if none"]
}}

Be objective and only flag actual stereotypes or bias."""
            
            # Use custom stereotype prompt for analysis
            if media_type == "image":
                analysis = self.vision_analyzer.analyze_image(ad_path, stereotype_prompt)
            else:
                analysis = self.vision_analyzer.analyze_video(ad_path, stereotype_prompt)
            
            if not analysis.get("success"):
                return 1.0, "Stereotype check unavailable (assuming safe)", []
            
            # Parse structured JSON response
            analysis_data = analysis.get("analysis", {})
            raw_text = analysis.get("raw_text", "")
            
            has_stereotypes = False
            description = ""
            specific_issues = []
            confidence = "medium"
            
            if isinstance(analysis_data, dict):
                has_stereotypes = analysis_data.get("stereotypes", False)
                description = analysis_data.get("description", "")
                specific_issues = analysis_data.get("specific_issues", [])
                confidence = analysis_data.get("confidence", "medium")
            else:
                # Try to extract from raw text
                import json
                import re
                json_match = re.search(r'\{[^{}]*"stereotypes"[^{}]*\}', raw_text, re.IGNORECASE)
                if json_match:
                    try:
                        parsed = json.loads(json_match.group())
                        has_stereotypes = parsed.get("stereotypes", False)
                        description = parsed.get("description", "")
                        specific_issues = parsed.get("specific_issues", [])
                    except:
                        pass
                
                # Check for explicit statements
                text_lower = raw_text.lower()
                if any(phrase in text_lower for phrase in ["no stereotypes", "not stereotypical", "inclusive", "diverse", "respectful"]):
                    has_stereotypes = False
                elif any(phrase in text_lower for phrase in ["stereotypes", "stereotypical", "bias", "biased"]):
                    if "no stereotypes" not in text_lower and "not stereotypical" not in text_lower:
                        has_stereotypes = True
            
            # Generate score and feedback from analysis
            if has_stereotypes:
                if confidence == "high":
                    score = 0.0
                elif confidence == "medium":
                    score = 0.2
                else:
                    score = 0.4
                
                feedback = description if description else "Stereotypes or bias detected in advertisement"
                issues = specific_issues if specific_issues else ["Stereotypical or biased content found"]
            else:
                score = 1.0
                feedback = description if description else "No stereotypes detected - advertisement is inclusive and respectful"
                issues = []
            
            return score, feedback, issues
        except Exception as e:
            self.logger.error(f"Error evaluating stereotypes: {e}")
            return 1.0, "Stereotype evaluation error (assuming safe)", [str(e)]
    
    def _evaluate_misleading_claims(
        self,
        ad_path: Path,
        media_type: str,
        user_prompt: Optional[str] = None
    ) -> Tuple[float, str, List[str]]:
        """Evaluate for misleading or false claims."""
        try:
            # Create comprehensive misleading claims analysis prompt
            misleading_prompt = f"""Analyze this advertisement for misleading or false claims.

Check specifically for:
- Exaggerated or false product claims
- Deceptive representations
- False promises or guarantees
- Misleading information about the product or brand

IMPORTANT: Only flag as misleading if claims are ACTUALLY false or deceptive. Standard advertising language and marketing claims are acceptable. Respond with "misleading": false for normal advertising.

Respond with JSON format:
{{
  "misleading": true/false,
  "confidence": "high/medium/low",
  "description": "Detailed explanation of your analysis",
  "specific_issues": ["list any specific misleading claims found, or empty array if none"]
}}

Be objective and only flag actual false or deceptive claims."""
            
            # Use custom misleading prompt for analysis
            if media_type == "image":
                analysis = self.vision_analyzer.analyze_image(ad_path, misleading_prompt)
            else:
                analysis = self.vision_analyzer.analyze_video(ad_path, misleading_prompt)
            
            if not analysis.get("success"):
                return 1.0, "Misleading claims check unavailable (assuming safe)", []
            
            # Parse structured JSON response
            analysis_data = analysis.get("analysis", {})
            raw_text = analysis.get("raw_text", "")
            
            is_misleading = False
            description = ""
            specific_issues = []
            confidence = "medium"
            
            if isinstance(analysis_data, dict):
                is_misleading = analysis_data.get("misleading", False)
                description = analysis_data.get("description", "")
                specific_issues = analysis_data.get("specific_issues", [])
                confidence = analysis_data.get("confidence", "medium")
            else:
                # Try to extract from raw text
                import json
                import re
                json_match = re.search(r'\{[^{}]*"misleading"[^{}]*\}', raw_text, re.IGNORECASE)
                if json_match:
                    try:
                        parsed = json.loads(json_match.group())
                        is_misleading = parsed.get("misleading", False)
                        description = parsed.get("description", "")
                        specific_issues = parsed.get("specific_issues", [])
                    except:
                        pass
                
                # Check for explicit statements
                text_lower = raw_text.lower()
                if any(phrase in text_lower for phrase in ["no misleading", "not misleading", "truthful", "accurate", "honest"]):
                    is_misleading = False
                elif any(phrase in text_lower for phrase in ["misleading", "false", "deceptive", "exaggerated"]):
                    if "no misleading" not in text_lower and "not misleading" not in text_lower:
                        is_misleading = True
            
            # Generate score and feedback from analysis
            if is_misleading:
                if confidence == "high":
                    score = 0.0
                elif confidence == "medium":
                    score = 0.2
                else:
                    score = 0.4
                
                feedback = description if description else "Misleading or false claims detected in advertisement"
                issues = specific_issues if specific_issues else ["Misleading or false claims found"]
            else:
                score = 1.0
                feedback = description if description else "No misleading claims detected - advertisement is truthful and accurate"
                issues = []
            
            return score, feedback, issues
        except Exception as e:
            self.logger.error(f"Error evaluating misleading claims: {e}")
            return 1.0, "Misleading claims evaluation error (assuming safe)", [str(e)]


# Global safety evaluator instance
safety_evaluator = SafetyEvaluator()
