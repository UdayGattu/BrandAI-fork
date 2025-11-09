"""
Request models for BrandAI API.
"""
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field, HttpUrl


class MediaType(str, Enum):
    """Media type for ad generation."""
    IMAGE = "image"
    VIDEO = "video"


class AdGenerationRequest(BaseModel):
    """
    Request model for ad generation.
    
    User provides:
    - Brand logo (file upload)
    - Product image (file upload)
    - Prompt describing the ad
    - Media type (image or video)
    - Optional brand website URL for scraping
    """
    prompt: str = Field(
        ...,
        description="Description of how the ad should be and what it should convey",
        min_length=10,
        max_length=1000
    )
    media_type: MediaType = Field(
        ...,
        description="Type of media to generate: 'image' or 'video'"
    )
    brand_website_url: Optional[HttpUrl] = Field(
        None,
        description="Optional brand website URL for scraping brand kit information"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "prompt": "Create a vibrant ad showcasing our new running shoes with dynamic motion, emphasizing comfort and style",
                "media_type": "image",
                "brand_website_url": "https://example.com"
            }
        }
