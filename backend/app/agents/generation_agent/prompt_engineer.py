"""
Prompt engineering for ad generation.
Creates optimized prompts with brand context and generates variations.
"""
from typing import Dict, List, Optional
import random

from app.services.logger import app_logger


class PromptEngineer:
    """Engineer prompts for ad generation."""
    
    def __init__(self):
        """Initialize prompt engineer."""
        self.logger = app_logger
    
    def create_prompt(
        self,
        base_prompt: str,
        brand_kit: Optional[Dict] = None,
        media_type: str = "image"
    ) -> str:
        """
        Create optimized prompt with brand context.
        
        Args:
            base_prompt: User-provided base prompt
            brand_kit: Brand kit information (colors, logo, etc.)
            media_type: Media type ('image' or 'video')
        
        Returns:
            Optimized prompt string
        """
        prompt_parts = []
        
        # Add base prompt
        prompt_parts.append(base_prompt)
        
        # Add brand context if available
        if brand_kit:
            # Add color context
            if brand_kit.get("colors"):
                colors = brand_kit["colors"]
                color_palette = colors.get("color_palette", [])
                primary_color = colors.get("primary_color")
                
                if color_palette:
                    color_desc = ", ".join(color_palette[:3])  # Top 3 colors
                    prompt_parts.append(f"Use brand colors: {color_desc}")
                    if primary_color:
                        prompt_parts.append(f"Primary color: {primary_color}")
            
            # Add brand name if available
            if brand_kit.get("website", {}).get("brand_name"):
                brand_name = brand_kit["website"]["brand_name"]
                prompt_parts.append(f"Brand: {brand_name}")
        
        # Add media-specific instructions
        if media_type == "video":
            prompt_parts.append("Create a dynamic, engaging video ad")
        else:
            prompt_parts.append("Create a high-quality, professional image ad")
        
        # Combine all parts
        optimized_prompt = ". ".join(prompt_parts)
        
        return optimized_prompt
    
    def generate_variations(
        self,
        base_prompt: str,
        brand_kit: Optional[Dict] = None,
        num_variations: int = 3,
        media_type: str = "image"
    ) -> List[str]:
        """
        Generate multiple advertisement prompt variations.
        
        Args:
            base_prompt: User-provided base prompt (product description, ad concept)
            brand_kit: Brand kit information
            num_variations: Number of variations to generate (default: 3)
            media_type: Media type ('image' or 'video')
        
        Returns:
            List of advertisement prompt variations
        """
        variations = []
        
        # Advertisement-specific style variations
        ad_styles = [
            "professional product advertisement with clear call-to-action",
            "lifestyle advertisement showcasing product in use",
            "bold and eye-catching advertisement with strong visual impact"
        ]
        
        # Advertisement composition approaches
        ad_compositions = [
            "product-focused composition with clear product visibility",
            "scene-based composition showing product in context",
            "minimalist composition with strong brand presence"
        ]
        
        # Advertisement mood/tone variations
        ad_tones = [
            "confident and trustworthy",
            "energetic and exciting",
            "sophisticated and premium"
        ]
        
        for i in range(num_variations):
            variation_parts = []
            
            # Start with advertisement context
            if media_type == "image":
                variation_parts.append("Create a professional advertisement image")
            else:
                variation_parts.append("Create a professional advertisement video")
            
            # Add base prompt (product/ad concept)
            variation_parts.append(base_prompt)
            
            # Add advertisement style
            if i < len(ad_styles):
                variation_parts.append(ad_styles[i])
            
            # Add composition approach
            if media_type == "image" and i < len(ad_compositions):
                variation_parts.append(ad_compositions[i])
            
            # Add tone
            if i < len(ad_tones):
                variation_parts.append(f"Tone: {ad_tones[i]}")
            
            # Add brand context
            if brand_kit:
                # Brand colors
                if brand_kit.get("colors"):
                    colors = brand_kit["colors"]
                    color_palette = colors.get("color_palette", [])
                    primary_color = colors.get("primary_color")
                    
                    if color_palette:
                        # Use different brand colors for each variation
                        color_idx = i % len(color_palette)
                        variation_parts.append(f"Use brand color: {color_palette[color_idx]}")
                        if primary_color and i == 0:
                            variation_parts.append(f"Primary brand color: {primary_color}")
                
                # Brand name
                if brand_kit.get("website", {}).get("brand_name"):
                    brand_name = brand_kit["website"]["brand_name"]
                    variation_parts.append(f"Brand: {brand_name}")
            
            # Add advertisement-specific requirements
            variation_parts.append("High quality, professional advertising content")
            variation_parts.append("Suitable for social media and marketing campaigns")
            
            # Add media-specific instructions
            if media_type == "video":
                video_styles = [
                    "5-10 second advertisement with smooth transitions",
                    "Dynamic video advertisement with engaging motion",
                    "Cinematic advertisement video with professional quality"
                ]
                if i < len(video_styles):
                    variation_parts.append(video_styles[i])
            
            # Combine variation
            variation = ". ".join(variation_parts)
            variations.append(variation)
        
        return variations
    
    def enhance_with_brand(
        self,
        prompt: str,
        brand_kit: Dict
    ) -> str:
        """
        Enhance prompt with specific brand elements.
        
        Args:
            prompt: Base prompt
            brand_kit: Brand kit information
        
        Returns:
            Enhanced prompt
        """
        enhancements = []
        
        # Logo mention
        if brand_kit.get("logo"):
            enhancements.append("Include brand logo prominently")
        
        # Color emphasis
        if brand_kit.get("colors"):
            colors = brand_kit["colors"]
            primary = colors.get("primary_color")
            if primary:
                enhancements.append(f"Use {primary} as the dominant color")
        
        # Brand description
        if brand_kit.get("website", {}).get("description"):
            desc = brand_kit["website"]["description"]
            enhancements.append(f"Brand essence: {desc[:100]}")
        
        if enhancements:
            enhanced = f"{prompt}. {' '.join(enhancements)}"
            return enhanced
        
        return prompt


# Global prompt engineer instance
prompt_engineer = PromptEngineer()
