"""
Variation generator for creating multiple ad variations.
Handles parallel generation and storage of variations.
"""
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

from app.agents.generation_agent.providers.vertex_imagen import imagen_provider
from app.agents.generation_agent.providers.vertex_veo import veo_provider
from app.services.storage_service import storage_service
from app.services.logger import app_logger


class VariationGenerator:
    """Generate multiple ad variations."""
    
    def __init__(self):
        """Initialize variation generator."""
        self.logger = app_logger
    
    def generate_variations(
        self,
        prompts: List[str],
        media_type: str,
        run_id: str,
        num_variations: int = 3,
        **kwargs
    ) -> List[Dict]:
        """
        Generate multiple advertisement variations.
        
        Args:
            prompts: List of advertisement prompts (should be 3 variations)
            media_type: Media type ('image' or 'video')
            run_id: Run ID for organizing files
            num_variations: Number of variations to generate (default: 3)
        
        Returns:
            List of variation results:
            - variation_id: str
            - file_path: Path
            - success: bool
            - error: Optional[str]
        """
        self.logger.info(f"Generating {num_variations} {media_type} variations for run {run_id}")
        
        # Limit to requested number
        prompts = prompts[:num_variations]
        
        # Create output directory
        output_dir = storage_service.get_storage_path("ads") / run_id
        output_dir.mkdir(parents=True, exist_ok=True)
        
        results = []
        
        # Generate each variation
        for i, prompt in enumerate(prompts):
            variation_id = f"var_{i+1}"
            self.logger.info(f"Generating variation {variation_id}: {prompt[:50]}...")
            
            try:
                if media_type == "image":
                    result = imagen_provider.generate(prompt)
                elif media_type == "video":
                    # Generate 8 second advertisement videos (max for veo-3.1)
                    # Get logo/product images from kwargs if available
                    logo_image = kwargs.get("logo_image")
                    product_image = kwargs.get("product_image")
                    
                    result = veo_provider.generate(
                        prompt,
                        duration_seconds=8,  # 8 seconds (max for veo-3.1-generate-preview)
                        aspect_ratio="16:9",
                        logo_image=logo_image,
                        product_image=product_image
                    )
                else:
                    result = {
                        "success": False,
                        "error": f"Unsupported media type: {media_type}"
                    }
                
                if result.get("success"):
                    # Save the generated media
                    if media_type == "image":
                        file_path = output_dir / f"{variation_id}.png"
                        if "image_data" in result:
                            if storage_service.save_file(
                                result["image_data"],
                                f"{variation_id}.png",
                                subdirectory=f"ads/{run_id}",
                                create_unique=False
                            ):
                                result["file_path"] = file_path
                                result["variation_id"] = variation_id
                    elif media_type == "video":
                        file_path = output_dir / f"{variation_id}.mp4"
                        if "video_data" in result:
                            if storage_service.save_file(
                                result["video_data"],
                                f"{variation_id}.mp4",
                                subdirectory=f"ads/{run_id}",
                                create_unique=False
                            ):
                                result["file_path"] = file_path
                                result["variation_id"] = variation_id
                        elif "video_url" in result:
                            # Store URL if video data not available
                            result["file_path"] = None
                            result["video_url"] = result["video_url"]
                            result["variation_id"] = variation_id
                
                results.append({
                    "variation_id": variation_id,
                    "file_path": result.get("file_path"),
                    "success": result.get("success", False),
                    "error": result.get("error"),
                    "metadata": result.get("metadata", {})
                })
                
            except Exception as e:
                self.logger.error(f"Error generating variation {variation_id}: {e}")
                results.append({
                    "variation_id": variation_id,
                    "file_path": None,
                    "success": False,
                    "error": str(e)
                })
        
        successful = sum(1 for r in results if r["success"])
        self.logger.info(f"Generated {successful}/{num_variations} variations successfully")
        
        return results
    
    def generate_parallel(
        self,
        prompts: List[str],
        media_type: str,
        run_id: str,
        num_variations: int = 3
    ) -> List[Dict]:
        """
        Generate variations in parallel (if supported).
        
        Note: Vertex AI APIs may have rate limits, so this might
        still be sequential in practice.
        
        Args:
            prompts: List of prompts
            media_type: Media type
            run_id: Run ID
            num_variations: Number of variations
        
        Returns:
            List of variation results
        """
        # For now, use sequential generation
        # Can be enhanced with async/threading if needed
        return self.generate_variations(prompts, media_type, run_id, num_variations)


# Global variation generator instance
variation_generator = VariationGenerator()
