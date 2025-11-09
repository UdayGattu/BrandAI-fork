"""
Base provider class for generation providers.
"""
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, Optional, List
from PIL import Image

from app.services.logger import app_logger


class BaseProvider(ABC):
    """Base class for all generation providers."""
    
    def __init__(self):
        """Initialize base provider."""
        self.logger = app_logger
    
    @abstractmethod
    def generate(
        self,
        prompt: str,
        **kwargs
    ) -> Dict:
        """
        Generate media (image or video) from prompt.
        
        Args:
            prompt: Generation prompt
            **kwargs: Additional generation parameters
        
        Returns:
            Dictionary with generation results:
            - success: bool
            - file_path: Optional[Path]
            - error: Optional[str]
            - metadata: Optional[Dict]
        """
        pass
    
    @abstractmethod
    def generate_variations(
        self,
        prompts: List[str],
        **kwargs
    ) -> List[Dict]:
        """
        Generate multiple variations.
        
        Args:
            prompts: List of prompts
            **kwargs: Additional parameters
        
        Returns:
            List of generation result dictionaries
        """
        pass
    
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
            
            # Save image
            with open(output_path, "wb") as f:
                f.write(image_data)
            
            self.logger.info(f"Saved generated image to: {output_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error saving image: {e}")
            return False
    
    def validate_prompt(self, prompt: str) -> bool:
        """
        Validate generation prompt.
        
        Args:
            prompt: Prompt to validate
        
        Returns:
            True if valid
        """
        if not prompt or len(prompt.strip()) < 10:
            return False
        return True
