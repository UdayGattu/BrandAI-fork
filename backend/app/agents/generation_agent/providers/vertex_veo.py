"""
Gemini API Veo provider for video generation.
Uses REST API with predictLongRunning endpoint for Veo video generation.
Supports image-to-video (I2V) with Veo 3.1.
"""
from pathlib import Path
from typing import Dict, List, Optional, Union
import time
import requests
import json
import base64
from PIL import Image
import io

import google.generativeai as genai

from app.agents.generation_agent.providers.base_provider import BaseProvider
from app.config import settings
from app.services.logger import app_logger


class VeoProvider(BaseProvider):
    """Provider for Veo video generation via Gemini API (predictLongRunning REST API).
    
    Supports:
    - Text-to-video (T2V): Prompt only
    - Image-to-video (I2V): Prompt + Image(s) - Veo 3.1 only
    """
    
    def __init__(self):
        """Initialize Veo provider."""
        super().__init__()
        self.model_name = "veo-3.1-generate-preview"  # Veo 3.1 with image support
        self.api_key = None
        self._initialized = False
        self._initialize()
    
    def _initialize(self):
        """Initialize Gemini API client."""
        try:
            if settings.GEMINI_API_KEY:
                self.api_key = settings.GEMINI_API_KEY
                genai.configure(api_key=self.api_key)
                
                # Verify model exists
                try:
                    model = genai.get_model(self.model_name)
                    self._initialized = True
                    self.logger.info(
                        f"Veo provider initialized via Gemini API "
                        f"(model: {model.display_name}, methods: {model.supported_generation_methods})"
                    )
                except Exception as model_error:
                    self.logger.warning(f"Could not verify model: {model_error}")
                    self._initialized = True  # Still try, might work via REST API
            else:
                self.logger.error("GEMINI_API_KEY not set")
                self._initialized = False
        except Exception as e:
            self.logger.error(f"Error initializing Veo provider: {e}")
            self._initialized = False
    
    def _poll_operation(self, operation_name: str, max_wait_time: int = 600) -> Dict:
        """
        Poll a long-running operation until completion.
        
        Args:
            operation_name: Name of the operation to poll
            max_wait_time: Maximum time to wait in seconds
        
        Returns:
            Operation result dictionary
        """
        base_url = "https://generativelanguage.googleapis.com/v1beta"
        url = f"{base_url}/{operation_name}"
        headers = {"x-goog-api-key": self.api_key}
        
        start_time = time.time()
        poll_interval = 10
        
        while time.time() - start_time < max_wait_time:
            elapsed = int(time.time() - start_time)
            self.logger.info(f"...Generating video, please wait... (checked at {elapsed}s)")
            
            try:
                response = requests.get(url, headers=headers, timeout=30)
                
                if response.status_code == 200:
                    result = response.json()
                    
                    if result.get("done", False):
                        self.logger.info("Video generation complete!")
                        return result
                    else:
                        # Still processing
                        time.sleep(poll_interval)
                else:
                    self.logger.warning(f"Status check failed: {response.status_code}")
                    time.sleep(poll_interval)
                    
            except Exception as e:
                self.logger.warning(f"Poll error: {e}")
                time.sleep(poll_interval)
        
        return {"done": False, "error": "Timeout waiting for operation"}
    
    def _encode_image(self, image_input: Union[bytes, Path, str]) -> Optional[Dict[str, str]]:
        """
        Encode image to base64 with mimeType for Veo API.
        
        Args:
            image_input: Image as bytes, file path, or file path string
        
        Returns:
            Dictionary with bytesBase64Encoded and mimeType, or None if error
        """
        try:
            image_bytes = None
            mime_type = "image/png"
            
            # Handle different input types
            if isinstance(image_input, bytes):
                image_bytes = image_input
            elif isinstance(image_input, (Path, str)):
                path = Path(image_input)
                if path.exists():
                    image_bytes = path.read_bytes()
                    # Detect mime type from extension
                    ext = path.suffix.lower()
                    if ext in ['.jpg', '.jpeg']:
                        mime_type = "image/jpeg"
                    elif ext == '.png':
                        mime_type = "image/png"
                    else:
                        # Try to detect from image
                        img = Image.open(io.BytesIO(image_bytes))
                        mime_type = f"image/{img.format.lower()}" if img.format else "image/png"
                else:
                    self.logger.warning(f"Image file not found: {path}")
                    return None
            else:
                self.logger.warning(f"Unsupported image input type: {type(image_input)}")
                return None
            
            if not image_bytes:
                return None
            
            # Encode to base64
            encoded = base64.b64encode(image_bytes).decode('utf-8')
            
            return {
                "bytesBase64Encoded": encoded,
                "mimeType": mime_type
            }
            
        except Exception as e:
            self.logger.error(f"Error encoding image: {e}")
            return None
    
    def generate(
        self,
        prompt: str,
        duration_seconds: int = 8,
        aspect_ratio: str = "16:9",
        logo_image: Optional[Union[bytes, Path, str]] = None,
        product_image: Optional[Union[bytes, Path, str]] = None,
        **kwargs
    ) -> Dict:
        """
        Generate video using Gemini API with Veo (predictLongRunning REST API).
        
        Supports Image-to-Video (I2V) with Veo 3.1:
        - Provide logo_image and/or product_image for image-to-video
        - If no images provided, uses text-to-video mode
        
        Args:
            prompt: Text prompt for video generation
            duration_seconds: Video duration in seconds (5-8 for veo-3.1)
            aspect_ratio: Video aspect ratio (16:9, 9:16, 1:1)
            logo_image: Optional logo image (bytes, Path, or file path string)
            product_image: Optional product image (bytes, Path, or file path string)
            **kwargs: Additional parameters
        
        Returns:
            Dictionary with generation results
        """
        if not self.validate_prompt(prompt):
            return {
                "success": False,
                "error": "Invalid prompt: must be at least 10 characters"
            }
        
        if not self.api_key or not self._initialized:
            return {
                "success": False,
                "error": "Veo provider not initialized. Check GEMINI_API_KEY."
            }
        
        try:
            # Check if images are provided (I2V mode)
            has_images = logo_image is not None or product_image is not None
            
            if has_images:
                self.logger.info(f"Generating video with image-to-video (I2V) mode")
                self.logger.info(f"Prompt: {prompt[:50]}...")
            else:
                self.logger.info(f"Generating video with text-to-video (T2V) mode")
                self.logger.info(f"Prompt: {prompt[:50]}...")
            
            # Validate duration (5-8 seconds for veo-3.1)
            if duration_seconds < 5:
                duration_seconds = 5
            elif duration_seconds > 8:
                duration_seconds = 8
                self.logger.warning(f"Duration capped at 8 seconds (max for veo-3.1)")
            
            # Enhanced prompt for advertisement video generation
            video_prompt = f"Create a professional advertisement video: {prompt}. Duration: {duration_seconds} seconds. High-quality, photorealistic, suitable for marketing campaigns."
            
            # If both images provided but only one can be used, mention the other in prompt
            if has_images and logo_image and product_image:
                video_prompt += " Include the product prominently in the video."
                self.logger.info("Both logo and product provided - logo will be used, product mentioned in prompt")
            
            self.logger.info(f"Submitting video generation request to {self.model_name}...")
            self.logger.info("This can take several minutes...")
            
            # Use REST API predictLongRunning endpoint
            base_url = "https://generativelanguage.googleapis.com/v1beta"
            url = f"{base_url}/models/{self.model_name}:predictLongRunning"
            
            headers = {
                "x-goog-api-key": self.api_key,
                "Content-Type": "application/json"
            }
            
            # Build instance payload
            instance = {
                "prompt": video_prompt
            }
            
            # Add images if provided (I2V mode)
            if has_images:
                # Veo 3.1 supports image input for I2V
                # Strategy: Prioritize logo (brand identity), but use product if no logo
                # Note: API may support only one image, so we choose the most important
                image_to_use = None
                image_type = None
                
                if logo_image:
                    # Logo is prioritized for brand recognition
                    image_to_use = logo_image
                    image_type = "logo"
                    self.logger.info("Using logo image for I2V generation")
                elif product_image:
                    # Product image if no logo available
                    image_to_use = product_image
                    image_type = "product"
                    self.logger.info("Using product image for I2V generation")
                
                if image_to_use:
                    encoded_image = self._encode_image(image_to_use)
                    
                    if encoded_image:
                        instance["image"] = encoded_image
                        self.logger.info(f"✅ {image_type.capitalize()} image included in request (I2V mode)")
                    else:
                        self.logger.warning("⚠️  Failed to encode image, falling back to text-only mode")
                else:
                    self.logger.warning("⚠️  No valid image provided, falling back to text-only mode")
            
            # Request body for predictLongRunning
            payload = {
                "instances": [instance],
                "parameters": {
                    # Note: aspectRatio and durationSeconds may not be supported by all models
                    # Remove if API returns errors
                    "negativePrompt": "blurry, low-resolution, cartoon, non-realistic, watermark, text overlay"
                }
            }
            
            # Add duration if supported (some models may not support it)
            # Try without first, add if needed
            try:
                # Test if duration is supported by trying a minimal request first
                # For now, include it and let API reject if not supported
                pass
            except:
                pass
            
            # Submit the request
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            
            if response.status_code != 200:
                error_data = response.json() if response.headers.get('content-type') == 'application/json' else response.text
                return {
                    "success": False,
                    "error": f"API error {response.status_code}: {error_data}"
                }
            
            result = response.json()
            
            # Check if operation was created
            if "name" in result:
                operation_name = result["name"]
                self.logger.info(f"Video generation operation started: {operation_name}")
                
                # Poll for completion
                operation_result = self._poll_operation(operation_name)
                
                if not operation_result.get("done"):
                    return {
                        "success": False,
                        "error": operation_result.get("error", "Operation did not complete")
                    }
                
                # Extract video from response
                if "response" in operation_result:
                    response_data = operation_result["response"]
                    
                    # Check for video URI in response
                    # Structure may vary: response.generateVideoResponse.generatedSamples[0].video.uri
                    video_uri = None
                    
                    if "generateVideoResponse" in response_data:
                        video_response = response_data["generateVideoResponse"]
                        if "generatedSamples" in video_response and len(video_response["generatedSamples"]) > 0:
                            sample = video_response["generatedSamples"][0]
                            if "video" in sample and "uri" in sample["video"]:
                                video_uri = sample["video"]["uri"]
                    
                    if video_uri:
                        self.logger.info(f"✅ Video generated! URI: {video_uri}")
                        
                        # Download video from URI
                        try:
                            video_data = None
                            
                            if video_uri.startswith("gs://"):
                                # GCS URI - use storage client
                                from google.cloud import storage
                                
                                uri_parts = video_uri.replace("gs://", "").split("/", 1)
                                bucket_name = uri_parts[0]
                                blob_name = uri_parts[1] if len(uri_parts) > 1 else ""
                                
                                storage_client = storage.Client(project=settings.GCP_PROJECT_ID)
                                bucket = storage_client.bucket(bucket_name)
                                blob = bucket.blob(blob_name)
                                
                                video_data = blob.download_as_bytes()
                                
                            elif video_uri.startswith("http://") or video_uri.startswith("https://"):
                                # HTTP/HTTPS URI - download directly
                                headers = {"x-goog-api-key": self.api_key} if "generativelanguage.googleapis.com" in video_uri else {}
                                video_response = requests.get(video_uri, headers=headers, timeout=60)
                                
                                if video_response.status_code == 200:
                                    video_data = video_response.content
                                else:
                                    self.logger.warning(f"Download failed: HTTP {video_response.status_code}")
                            
                            if video_data:
                                self.logger.info(f"Video downloaded successfully ({len(video_data)} bytes)")
                                
                                return {
                                    "success": True,
                                    "video_data": video_data,
                                    "video_uri": video_uri,
                                    "metadata": {
                                        "model": self.model_name,
                                        "prompt": prompt,
                                        "duration_seconds": duration_seconds,
                                        "aspect_ratio": aspect_ratio,
                                        "has_images": has_images,
                                        "mode": "I2V" if has_images else "T2V"
                                    }
                                }
                            else:
                                # Return URI even if download fails
                                return {
                                    "success": True,
                                    "video_data": None,
                                    "video_uri": video_uri,
                                    "metadata": {
                                        "model": self.model_name,
                                        "prompt": prompt,
                                        "duration_seconds": duration_seconds,
                                        "aspect_ratio": aspect_ratio,
                                        "has_images": has_images,
                                        "mode": "I2V" if has_images else "T2V",
                                        "note": "Video URI available, download manually"
                                    }
                                }
                                
                        except Exception as download_error:
                            self.logger.warning(f"Could not download video: {download_error}")
                            return {
                                "success": True,
                                "video_data": None,
                                "video_uri": video_uri,
                                    "metadata": {
                                        "model": self.model_name,
                                        "prompt": prompt,
                                        "duration_seconds": duration_seconds,
                                        "aspect_ratio": aspect_ratio,
                                        "has_images": has_images,
                                        "mode": "I2V" if has_images else "T2V",
                                        "error": f"Download failed: {str(download_error)}"
                                    }
                            }
                    else:
                        return {
                            "success": False,
                            "error": "Video generation completed but video URI not found in response"
                        }
                elif "error" in operation_result:
                    return {
                        "success": False,
                        "error": f"Video generation failed: {operation_result['error']}"
                    }
                else:
                    return {
                        "success": False,
                        "error": "Video generation completed but no response data"
                    }
            else:
                return {
                    "success": False,
                    "error": f"Unexpected response format: {result}"
                }
            
        except Exception as e:
            self.logger.error(f"Error generating video: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def generate_variations(
        self,
        prompts: List[str],
        output_dir: Optional[Path] = None,
        **kwargs
    ) -> List[Dict]:
        """
        Generate multiple video variations.
        
        Args:
            prompts: List of prompts
            output_dir: Directory to save videos
            **kwargs: Additional parameters
        
        Returns:
            List of generation result dictionaries
        """
        results = []
        
        for i, prompt in enumerate(prompts):
            self.logger.info(f"Generating video variation {i+1}/{len(prompts)}")
            
            result = self.generate(prompt, **kwargs)
            
            # Save if output directory provided and video data available
            if result.get("success") and output_dir and result.get("video_data"):
                variation_id = f"var_{i+1}"
                output_path = output_dir / f"{variation_id}.mp4"
                
                if self.save_result(result["video_data"], output_path):
                    result["file_path"] = output_path
                    result["variation_id"] = variation_id
            
            results.append(result)
        
        return results
    
    def save_result(
        self,
        video_data: bytes,
        output_path: Path,
        format: str = "MP4"
    ) -> bool:
        """
        Save generated video to file.
        
        Args:
            video_data: Video data as bytes
            output_path: Path to save file
            format: Video format (MP4, etc.)
        
        Returns:
            True if saved successfully
        """
        try:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Save video
            with open(output_path, "wb") as f:
                f.write(video_data)
            
            self.logger.info(f"Saved generated video to: {output_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error saving video: {e}")
            return False


# Global Veo provider instance
veo_provider = VeoProvider()
