"""
Run status models for tracking ad generation workflow.
"""
from datetime import datetime, timezone
from enum import Enum
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field


class RunStatus(str, Enum):
    """Run status enumeration."""
    PENDING = "pending"
    BRAND_KIT_EXTRACTION = "brand_kit_extraction"
    GENERATION = "generation"
    CRITIQUE = "critique"
    REFINEMENT = "refinement"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class RunStage(BaseModel):
    """Individual stage tracking."""
    stage_name: str = Field(..., description="Name of the stage")
    status: RunStatus = Field(..., description="Status of this stage")
    started_at: Optional[datetime] = Field(None, description="Stage start timestamp")
    completed_at: Optional[datetime] = Field(None, description="Stage completion timestamp")
    error: Optional[str] = Field(None, description="Error message if stage failed")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional stage metadata")


class RunModel(BaseModel):
    """
    Complete run tracking model.
    
    Tracks the entire workflow from brand kit extraction
    through generation, critique, and refinement.
    """
    run_id: str = Field(..., description="Unique run identifier")
    status: RunStatus = Field(default=RunStatus.PENDING, description="Current run status")
    progress: float = Field(default=0.0, ge=0.0, le=100.0, description="Overall progress percentage")
    
    # Input data
    prompt: str = Field(..., description="User-provided prompt")
    media_type: str = Field(..., description="Media type: 'image' or 'video'")
    brand_website_url: Optional[str] = Field(None, description="Optional brand website URL")
    
    # Stage tracking
    stages: Dict[str, RunStage] = Field(default_factory=dict, description="Stage tracking")
    current_stage: Optional[str] = Field(None, description="Current active stage")
    
    # Results
    brand_kit_data: Optional[Dict[str, Any]] = Field(None, description="Extracted brand kit data")
    generated_ads: Optional[List[str]] = Field(None, description="Paths to generated ad files")
    critique_results: Optional[Dict[str, Any]] = Field(None, description="Critique evaluation results")
    final_ad_path: Optional[str] = Field(None, description="Path to final selected/refined ad")
    
    # Metadata
    retry_count: int = Field(default=0, description="Number of retry attempts")
    max_retries: int = Field(default=3, description="Maximum retry attempts allowed")
    error_message: Optional[str] = Field(None, description="Error message if run failed")
    
    # Timestamps
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Run creation timestamp")
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Last update timestamp")
    completed_at: Optional[datetime] = Field(None, description="Run completion timestamp")
    
    class Config:
        use_enum_values = True
        json_schema_extra = {
            "example": {
                "run_id": "run_1234567890",
                "status": "generation",
                "progress": 45.0,
                "prompt": "Create a vibrant ad showcasing our new running shoes",
                "media_type": "image",
                "current_stage": "generation",
                "retry_count": 0,
                "max_retries": 3
            }
        }
