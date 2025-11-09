"""
Gemini API Imagen provider for image generation.
Uses Gemini API with Nano Banana (gemini-2.5-flash-image) for high-quality image generation.
"""
from pathlib import Path
from typing import Dict, List, Optional
from io import BytesIO
from PIL import Image

from google import genai

from app.agents.generation_agent.providers.base_provider import BaseProvider
from app.config import settings
from app.services.logger import app_logger


class ImagenProvider(BaseProvider):
    """Provider for Imagen image generation via Gemini API (Nano Banana)."""
    
    def __init__(self):
        """Initialize Imagen provider."""
        super().__init__()
        # Use Nano Banana model for image generation
        self.model_name = "gemini-2.5-flash-image"
        self.client = None
        self._initialize()
    
    def _initialize(self):
        """Initialize Gemini API client."""
        try:
            if settings.GEMINI_API_KEY:
                self.client = genai.Client(api_key=settings.GEMINI_API_KEY)
                self.logger.info("Imagen provider initialized via Gemini API (Nano Banana)")
            else:
                self.logger.error("GEMINI_API_KEY not set")
        except Exception as e:
            self.logger.error(f"Error initializing Imagen provider: {e}")
    
    def generate(
        self,
        prompt: str,
        number_of_images: int = 1,
        aspect_ratio: str = "1:1",
        **kwargs
    ) -> Dict:
        """
        Generate image using Gemini API with Nano Banana.
        
        Args:
            prompt: Text prompt for image generation
            number_of_images: Number of images to generate (1-4)
            aspect_ratio: Image aspect ratio (1:1, 9:16, 16:9, 4:3, 3:4)
            **kwargs: Additional parameters
        
        Returns:
            Dictionary with generation results
        """
        if not self.validate_prompt(prompt):
            return {
                "success": False,
                "error": "Invalid prompt: must be at least 10 characters"
            }
        
        if not self.client:
            return {
                "success": False,
                "error": "Gemini API client not initialized"
            }
        
        try:
            self.logger.info(f"Generating image with prompt: {prompt[:50]}...")
            
            # Enhanced prompt for advertisement image generation
            image_prompt = f"Create a professional advertisement image: {prompt}. Aspect ratio: {aspect_ratio}. High-quality, photorealistic, suitable for marketing campaigns."
            
            # Generate image using Nano Banana model
            image_response = self.client.models.generate_content(
                model=self.model_name,
                contents=[image_prompt],
            )
            
            # Extract image from response
            # Response structure: response.candidates[0].content.parts[].inline_data
            # Note: Image may be in any part, not necessarily the first one
            image_data = None
            
            if (image_response.candidates and 
                len(image_response.candidates) > 0 and
                image_response.candidates[0].content and
                image_response.candidates[0].content.parts):
                
                # Check all parts for image data
                for part in image_response.candidates[0].content.parts:
                    if part.inline_data and part.inline_data.data:
                        image_data = part.inline_data.data
                        break
                    elif part.file_data and part.file_data.data:
                        image_data = part.file_data.data
                        break
                
                if image_data:
                    # Convert to PIL Image to verify and process
                    image = Image.open(BytesIO(image_data))
                    
                    self.logger.info(f"Image generated successfully: {image.size[0]}x{image.size[1]}")
                    
                    return {
                        "success": True,
                        "image_data": image_data,
                        "image": image,  # PIL Image object for easy saving
                        "metadata": {
                            "model": self.model_name,
                            "prompt": prompt,
                            "aspect_ratio": aspect_ratio,
                            "number_of_images": number_of_images,
                            "dimensions": f"{image.size[0]}x{image.size[1]}"
                        }
                    }
            
            return {
                "success": False,
                "error": "Image generation failed or no image data found in response."
            }
            
        except Exception as e:
            self.logger.error(f"Error generating image: {e}")
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
        Generate multiple image variations.
        
        Args:
            prompts: List of prompts
            output_dir: Directory to save images
            **kwargs: Additional parameters
        
        Returns:
            List of generation result dictionaries
        """
        results = []
        
        for i, prompt in enumerate(prompts):
            self.logger.info(f"Generating variation {i+1}/{len(prompts)}")
            
            result = self.generate(prompt, **kwargs)
            
            # Save if output directory provided
            if result.get("success") and output_dir:
                variation_id = f"var_{i+1}"
                output_path = output_dir / f"{variation_id}.png"
                
                # Use PIL Image to save
                if result.get("image"):
                    result["image"].save(output_path)
                    result["file_path"] = output_path
                    result["variation_id"] = variation_id
                    self.logger.info(f"Saved image to: {output_path}")
                elif result.get("image_data"):
                    # Fallback: save raw bytes
                    if self.save_result(result["image_data"], output_path):
                        result["file_path"] = output_path
                        result["variation_id"] = variation_id
            
            results.append(result)
        
        return results
    
    def save_result(
        self,
        image_data: bytes,
        output_path: Path,
        format: str = "PNG"
    ) -> bool:
        """
        Save generated image to file.
        
        Args:
            image_data: Image data as bytes
            output_path: Path to save file
            format: Image format (PNG, JPEG, etc.)
        
        Returns:
            True if saved successfully
        """
        try:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Save image using PIL
            image = Image.open(BytesIO(image_data))
            image.save(output_path, format=format)
            
            self.logger.info(f"Saved generated image to: {output_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error saving image: {e}")
            return False


# Global Imagen provider instance
imagen_provider = ImagenProvider()
