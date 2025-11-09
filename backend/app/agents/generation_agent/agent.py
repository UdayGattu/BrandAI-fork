"""
Generation Agent for creating ad variations.
Orchestrates prompt engineering, variation generation, and storage.
"""
from pathlib import Path
from typing import Dict, List, Optional

from app.agents.base_agent import BaseAgent
from app.agents.generation_agent.prompt_engineer import prompt_engineer
from app.agents.generation_agent.variation_generator import variation_generator
from app.services.logger import app_logger
from app.services.storage_service import storage_service


class GenerationAgent(BaseAgent):
    """Agent for generating ad variations."""
    
    def __init__(self):
        """Initialize generation agent."""
        super().__init__()
        self.logger = app_logger
        self.prompt_engineer = prompt_engineer
        self.variation_generator = variation_generator
    
    def execute(
        self,
        prompt: str,
        media_type: str,
        brand_kit: Optional[Dict] = None,
        run_id: str = None,
        num_variations: int = 1,
        **kwargs
    ) -> Dict:
        """
        Execute ad generation (implements BaseAgent interface).
        
        Args:
            prompt: User-provided prompt
            media_type: Media type ('image' or 'video')
            brand_kit: Brand kit information
            run_id: Run ID for organizing files
            num_variations: Number of variations to generate (default: 1)
            **kwargs: Additional arguments
        
        Returns:
            Standardized result dictionary
        """
        self.log_start("ad_generation", run_id=run_id, media_type=media_type)
        
        try:
            # Generate advertisement prompt (single variation)
            self.logger.info("Creating advertisement prompt")
            prompt_variations = self.prompt_engineer.generate_variations(
                base_prompt=prompt,
                brand_kit=brand_kit,
                num_variations=num_variations,
                media_type=media_type
            )
            
            self.logger.info(f"Generated {len(prompt_variations)} prompt variation(s)")
            
            # Generate ad (single variation)
            self.logger.info(f"Generating {num_variations} {media_type} ad")
            
            # Extract logo/product images from brand_kit if available
            logo_image = None
            product_image = None
            if brand_kit:
                # Get logo path if available
                if brand_kit.get("logo", {}).get("file_path"):
                    logo_path = Path(brand_kit["logo"]["file_path"])
                    if logo_path.exists():
                        logo_image = logo_path
                        self.logger.info(f"Using logo from brand_kit: {logo_path}")
                
                # Get product image path if available
                # Check if product image was stored in brand_kit
                if brand_kit.get("product", {}).get("file_path"):
                    product_path = Path(brand_kit["product"]["file_path"])
                    if product_path.exists():
                        product_image = product_path
                        self.logger.info(f"Using product image from brand_kit: {product_path}")
                
                # Also check kwargs for product image (if passed separately)
                if not product_image and kwargs.get("product_image"):
                    product_image = kwargs.get("product_image")
                    self.logger.info(f"Using product image from kwargs")
            
            variation_results = self.variation_generator.generate_variations(
                prompts=prompt_variations,
                media_type=media_type,
                run_id=run_id,
                num_variations=num_variations,
                logo_image=logo_image,
                product_image=product_image
            )
            
            # Extract successful variations
            successful_variations = [
                v for v in variation_results if v.get("success")
            ]
            
            # Get file paths
            ad_paths = [
                str(v["file_path"]) for v in successful_variations
                if v.get("file_path")
            ]
            
            self.log_complete(
                "ad_generation",
                variations_generated=len(successful_variations),
                total_requested=num_variations
            )
            
            return self.create_result(
                success=len(successful_variations) > 0,
                data={
                    "variations": variation_results,
                    "ad_paths": ad_paths,
                    "prompt_variations": prompt_variations,
                    "num_successful": len(successful_variations),
                    "num_requested": num_variations
                },
                metadata={
                    "media_type": media_type,
                    "run_id": run_id
                }
            )
            
        except Exception as e:
            self.log_error("ad_generation", e, run_id=run_id)
            return self.create_result(
                success=False,
                error=str(e)
            )
    
    def generate_ads(
        self,
        prompt: str,
        media_type: str,
        brand_kit: Optional[Dict] = None,
        run_id: str = None,
        num_variations: int = 3
    ) -> Dict:
        """
        Generate ad variations.
        
        Args:
            prompt: User-provided prompt
            media_type: Media type ('image' or 'video')
            brand_kit: Brand kit information
            run_id: Run ID for organizing files
            num_variations: Number of variations to generate
        
        Returns:
            Dictionary with generation results
        """
        return self.execute(
            prompt=prompt,
            media_type=media_type,
            brand_kit=brand_kit,
            run_id=run_id,
            num_variations=num_variations
        )


# Global generation agent instance
generation_agent = GenerationAgent()
