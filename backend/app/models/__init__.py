"""
Pydantic models for BrandAI API.
"""
from app.models.request import AdGenerationRequest, MediaType
from app.models.response import (
    GenerationResponse,
    StatusResponse,
    FinalResponse,
    CritiqueReport,
    VariationResult,
    ScoreCard
)
from app.models.run import RunModel, RunStatus, RunStage

__all__ = [
    # Request models
    "AdGenerationRequest",
    "MediaType",
    # Response models
    "GenerationResponse",
    "StatusResponse",
    "FinalResponse",
    "CritiqueReport",
    "VariationResult",
    "ScoreCard",
    # Run models
    "RunModel",
    "RunStatus",
    "RunStage",
]

