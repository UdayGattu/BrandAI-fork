"""
Gemini Vision API analyzer for image and video analysis.
Uses Gemini 1.5 Pro Vision for comprehensive ad analysis.
"""
from pathlib import Path
from typing import Dict, List, Optional
import base64
import json

import google.generativeai as genai

from app.config import settings
from app.services.logger import app_logger


class VisionAnalyzer:
    """Analyze images and videos using Gemini Vision API."""
    
    def __init__(self):
        """Initialize Gemini Vision analyzer."""
        self.logger = app_logger
        self.api_key = None
        self.model_name = "gemini-2.5-pro"  # Use gemini-2.5-pro for vision tasks
        self.model = None
        self._initialized = False
        self._initialize()
    
    def _initialize(self):
        """Initialize Gemini API client."""
        try:
            if settings.GEMINI_API_KEY:
                self.api_key = settings.GEMINI_API_KEY
                genai.configure(api_key=self.api_key)
                
                # Try to get the model
                try:
                    self.model = genai.GenerativeModel(self.model_name)
                    self._initialized = True
                    self.logger.info(f"Gemini Vision analyzer initialized (model: {self.model_name})")
                except Exception as model_error:
                    # Try alternative model names
                    alternative_models = [
                        "gemini-2.5-pro",
                        "gemini-1.5-flash",
                        "gemini-1.5-pro-vision"
                    ]
                    
                    for alt_model in alternative_models:
                        try:
                            self.model = genai.GenerativeModel(alt_model)
                            self.model_name = alt_model
                            self._initialized = True
                            self.logger.info(f"Gemini Vision analyzer initialized (model: {alt_model})")
                            break
                        except:
                            continue
                    
                    if not self._initialized:
                        self.logger.warning(f"Could not initialize Gemini model: {model_error}")
            else:
                self.logger.error("GEMINI_API_KEY not set")
                self._initialized = False
        except Exception as e:
            self.logger.error(f"Error initializing Gemini Vision analyzer: {e}")
            self._initialized = False
    
    def _encode_image(self, image_path: Path) -> Optional[Dict]:
        """
        Encode image to base64 for Gemini API.
        
        Args:
            image_path: Path to image file
        
        Returns:
            Dictionary with image data, or None if error
        """
        try:
            image_bytes = image_path.read_bytes()
            image_data = base64.b64encode(image_bytes).decode('utf-8')
            
            # Detect MIME type
            ext = image_path.suffix.lower()
            mime_type = "image/png"
            if ext in ['.jpg', '.jpeg']:
                mime_type = "image/jpeg"
            elif ext == '.png':
                mime_type = "image/png"
            
            return {
                "mime_type": mime_type,
                "data": image_data
            }
        except Exception as e:
            self.logger.error(f"Error encoding image: {e}")
            return None
    
    def analyze_image(
        self,
        image_path: Path,
        analysis_prompt: str
    ) -> Dict:
        """
        Analyze image using Gemini Vision API.
        
        Args:
            image_path: Path to image file
            analysis_prompt: Prompt describing what to analyze
        
        Returns:
            Dictionary with analysis results
        """
        if not self._initialized:
            return {
                "success": False,
                "error": "Gemini Vision not initialized"
            }
        
        try:
            # Encode image
            image_data = self._encode_image(image_path)
            if not image_data:
                return {
                    "success": False,
                    "error": "Failed to encode image"
                }
            
            # Create content with image and prompt
            content = [
                {
                    "mime_type": image_data["mime_type"],
                    "data": image_data["data"]
                },
                analysis_prompt
            ]
            
            # Generate analysis
            response = self.model.generate_content(content)
            
            # Parse response
            analysis_text = response.text if hasattr(response, 'text') else str(response)
            
            # Try to parse as JSON if possible
            try:
                analysis_json = json.loads(analysis_text)
                return {
                    "success": True,
                    "analysis": analysis_json,
                    "raw_text": analysis_text
                }
            except json.JSONDecodeError:
                # Return as text if not JSON
                return {
                    "success": True,
                    "analysis": {"text": analysis_text},
                    "raw_text": analysis_text
                }
        except Exception as e:
            self.logger.error(f"Error analyzing image: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _encode_video(self, video_path: Path) -> Optional[Dict]:
        """
        Encode video to base64 for Gemini API.
        
        Args:
            video_path: Path to video file
        
        Returns:
            Dictionary with video data, or None if error
        """
        try:
            video_bytes = video_path.read_bytes()
            video_data = base64.b64encode(video_bytes).decode('utf-8')
            
            # Detect MIME type
            ext = video_path.suffix.lower()
            mime_type = "video/mp4"
            if ext == '.mp4':
                mime_type = "video/mp4"
            elif ext == '.mov':
                mime_type = "video/quicktime"
            elif ext == '.avi':
                mime_type = "video/x-msvideo"
            elif ext == '.webm':
                mime_type = "video/webm"
            
            return {
                "mime_type": mime_type,
                "data": video_data
            }
        except Exception as e:
            self.logger.error(f"Error encoding video: {e}")
            return None
    
    def analyze_video(
        self,
        video_path: Path,
        analysis_prompt: str
    ) -> Dict:
        """
        Analyze full video using Gemini Video Understanding API.
        
        Args:
            video_path: Path to video file
            analysis_prompt: Prompt describing what to analyze
        
        Returns:
            Dictionary with analysis results
        """
        if not self._initialized:
            return {
                "success": False,
                "error": "Gemini Vision not initialized"
            }
        
        try:
            # Encode video
            video_data = self._encode_video(video_path)
            if not video_data:
                return {
                    "success": False,
                    "error": "Failed to encode video"
                }
            
            # Create content with video and prompt
            content = [
                {
                    "mime_type": video_data["mime_type"],
                    "data": video_data["data"]
                },
                analysis_prompt
            ]
            
            # Generate analysis
            response = self.model.generate_content(content)
            
            # Parse response
            analysis_text = response.text if hasattr(response, 'text') else str(response)
            
            # Try to parse as JSON if possible
            try:
                analysis_json = json.loads(analysis_text)
                return {
                    "success": True,
                    "analysis": analysis_json,
                    "raw_text": analysis_text
                }
            except json.JSONDecodeError:
                # Return as text if not JSON
                return {
                    "success": True,
                    "analysis": {"text": analysis_text},
                    "raw_text": analysis_text
                }
        except Exception as e:
            self.logger.error(f"Error analyzing video: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def analyze_video_frame(
        self,
        frame_path: Path,
        analysis_prompt: str
    ) -> Dict:
        """
        Analyze a single video frame (fallback method).
        
        Args:
            frame_path: Path to extracted video frame
            analysis_prompt: Prompt describing what to analyze
        
        Returns:
            Dictionary with analysis results
        """
        return self.analyze_image(frame_path, analysis_prompt)
    
    def analyze_advertisement(
        self,
        ad_path: Path,
        media_type: str = "image",
        brand_kit: Optional[Dict] = None,
        user_prompt: Optional[str] = None
    ) -> Dict:
        """
        Analyze advertisement (image or video) comprehensively.
        
        Args:
            ad_path: Path to ad file (image or video)
            media_type: 'image' or 'video'
            brand_kit: Brand kit information for context
            user_prompt: Original user prompt for ad generation (for context)
        
        Returns:
            Dictionary with comprehensive analysis
        """
        if media_type == "image":
            # Analyze image directly
            prompt = self._create_ad_analysis_prompt(brand_kit, user_prompt, media_type)
            return self.analyze_image(ad_path, prompt)
        else:
            # For video, analyze full video using Gemini video understanding
            prompt = self._create_ad_analysis_prompt(brand_kit, user_prompt, media_type)
            return self.analyze_video(ad_path, prompt)
    
    def _create_ad_analysis_prompt(
        self,
        brand_kit: Optional[Dict] = None,
        user_prompt: Optional[str] = None,
        media_type: str = "image"
    ) -> str:
        """
        Create context-aware analysis prompt for advertisement evaluation.
        
        Args:
            brand_kit: Brand kit information
            user_prompt: Original user prompt for ad generation
            media_type: 'image' or 'video'
        
        Returns:
            Context-aware analysis prompt string
        """
        # Base prompt structure
        media_context = "video" if media_type == "video" else "image"
        prompt = f"""Analyze this advertisement {media_context} and provide a detailed evaluation in JSON format:

{{
  "brand_alignment": {{
    "logo_present": true/false,
    "color_consistency": "description",
    "tone_match": "description"
  }},
  "visual_quality": {{
    "blur_level": "description",
    "composition": "description",
    "artifacts": "description"
  }},
  "message_clarity": {{
    "product_visible": true/false,
    "tagline_clear": true/false,
    "message_understood": "description"
  }},
  "safety_ethics": {{
    "harmful_content": false,
    "stereotypes": false,
    "misleading": false
  }},
  "overall_assessment": "description"
}}

Be specific and objective in your analysis."""
        
        # Add brand context
        if brand_kit:
            brand_name = brand_kit.get("website", {}).get("brand_name", "")
            colors = brand_kit.get("colors", {}).get("color_palette", [])
            primary_color = brand_kit.get("colors", {}).get("primary_color", "")
            
            if brand_name:
                prompt += f"\n\nBrand: {brand_name}"
            if colors:
                prompt += f"\nBrand color palette: {', '.join(colors[:5])}"
            if primary_color:
                prompt += f"\nPrimary brand color: {primary_color}"
        
        # Add user prompt context (ad intent)
        if user_prompt:
            prompt += f"\n\nAd Intent/Context: {user_prompt}"
            prompt += "\nEvaluate if the ad effectively communicates this intent."
        
        # Add media-specific instructions
        if media_type == "video":
            prompt += "\n\nNote: This is a video advertisement. Consider temporal elements, movement, audio, and overall video quality in your evaluation."
        
        return prompt


# Global vision analyzer instance
vision_analyzer = VisionAnalyzer()
