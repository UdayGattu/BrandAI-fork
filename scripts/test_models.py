#!/usr/bin/env python3
"""
Comprehensive test script for Phase 1.4: Basic Models
Tests all request, response, and run models.
"""
import sys
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_dir))

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
from datetime import datetime


def test_request_models():
    """Test request models."""
    print("Testing Request Models...")
    
    # Test valid request
    req1 = AdGenerationRequest(
        prompt="Create a vibrant ad showcasing our new running shoes",
        media_type=MediaType.IMAGE
    )
    assert req1.prompt == "Create a vibrant ad showcasing our new running shoes"
    assert req1.media_type == MediaType.IMAGE
    assert req1.brand_website_url is None
    print("  ✅ Valid request (no website) - PASSED")
    
    # Test request with website URL
    req2 = AdGenerationRequest(
        prompt="Test prompt",
        media_type=MediaType.VIDEO,
        brand_website_url="https://example.com"
    )
    assert req2.media_type == MediaType.VIDEO
    assert str(req2.brand_website_url) == "https://example.com/"
    print("  ✅ Valid request (with website) - PASSED")
    
    # Test validation (min length)
    try:
        req3 = AdGenerationRequest(
            prompt="short",  # Too short
            media_type=MediaType.IMAGE
        )
        print("  ❌ Should have failed validation - FAILED")
        return False
    except Exception:
        print("  ✅ Validation (min length) - PASSED")
    
    print("✅ Request Models - ALL TESTS PASSED\n")
    return True


def test_run_models():
    """Test run models."""
    print("Testing Run Models...")
    
    # Test RunStatus enum
    assert RunStatus.PENDING == "pending"
    assert RunStatus.COMPLETED == "completed"
    print("  ✅ RunStatus enum - PASSED")
    
    # Test RunStage
    stage = RunStage(
        stage_name="generation",
        status=RunStatus.GENERATION,
        started_at=datetime.utcnow()
    )
    assert stage.stage_name == "generation"
    assert stage.status == RunStatus.GENERATION
    print("  ✅ RunStage model - PASSED")
    
    # Test RunModel
    run = RunModel(
        run_id="test_123",
        prompt="Test prompt for ad",
        media_type="image"
    )
    assert run.run_id == "test_123"
    assert run.status == RunStatus.PENDING
    assert run.progress == 0.0
    assert run.retry_count == 0
    assert run.max_retries == 3
    print("  ✅ RunModel basic - PASSED")
    
    # Test RunModel with stages
    run.stages["brand_kit"] = RunStage(
        stage_name="brand_kit",
        status=RunStatus.COMPLETED,
        started_at=datetime.utcnow(),
        completed_at=datetime.utcnow()
    )
    assert len(run.stages) == 1
    print("  ✅ RunModel with stages - PASSED")
    
    # Test status update
    run.status = RunStatus.GENERATION
    run.progress = 50.0
    assert run.status == RunStatus.GENERATION
    assert run.progress == 50.0
    print("  ✅ RunModel status update - PASSED")
    
    print("✅ Run Models - ALL TESTS PASSED\n")
    return True


def test_response_models():
    """Test response models."""
    print("Testing Response Models...")
    
    # Test ScoreCard
    scorecard = ScoreCard(
        dimension="brand_alignment",
        score=0.85,
        feedback="Good brand alignment with logo and colors"
    )
    assert scorecard.dimension == "brand_alignment"
    assert scorecard.score == 0.85
    assert 0.0 <= scorecard.score <= 1.0
    print("  ✅ ScoreCard - PASSED")
    
    # Test VariationResult
    variation = VariationResult(
        variation_id="var_1",
        file_path="/path/to/ad.jpg",
        overall_score=0.90,
        scorecard=[scorecard],
        passed=True,
        rank=1
    )
    assert variation.variation_id == "var_1"
    assert variation.overall_score == 0.90
    assert variation.passed is True
    print("  ✅ VariationResult - PASSED")
    
    # Test CritiqueReport
    report = CritiqueReport(
        run_id="run_123",
        total_variations=3,
        passed_variations=2,
        failed_variations=1,
        best_variation=variation,
        all_variations=[variation]
    )
    assert report.run_id == "run_123"
    assert report.total_variations == 3
    assert report.passed_variations == 2
    print("  ✅ CritiqueReport - PASSED")
    
    # Test GenerationResponse
    gen_resp = GenerationResponse(
        run_id="run_123",
        status=RunStatus.PENDING,
        message="Generation started"
    )
    assert gen_resp.run_id == "run_123"
    assert gen_resp.status == RunStatus.PENDING
    print("  ✅ GenerationResponse - PASSED")
    
    # Test StatusResponse
    status_resp = StatusResponse(
        run_id="run_123",
        status=RunStatus.GENERATION,
        progress=45.0,
        current_stage="generation",
        message="Generating ads...",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    assert status_resp.progress == 45.0
    assert 0.0 <= status_resp.progress <= 100.0
    print("  ✅ StatusResponse - PASSED")
    
    # Test FinalResponse
    final_resp = FinalResponse(
        run_id="run_123",
        status=RunStatus.COMPLETED,
        success=True,
        critique_report=report,
        retry_count=0
    )
    assert final_resp.success is True
    assert final_resp.critique_report is not None
    print("  ✅ FinalResponse - PASSED")
    
    print("✅ Response Models - ALL TESTS PASSED\n")
    return True


def test_integration():
    """Test models working together."""
    print("Testing Model Integration...")
    
    # Create a complete workflow
    req = AdGenerationRequest(
        prompt="Test ad generation",
        media_type=MediaType.IMAGE
    )
    
    run = RunModel(
        run_id="run_123",
        prompt=req.prompt,
        media_type=req.media_type.value
    )
    
    gen_resp = GenerationResponse(
        run_id=run.run_id,
        status=run.status,
        message="Generation started"
    )
    
    assert gen_resp.run_id == run.run_id
    assert gen_resp.status == run.status
    print("  ✅ Request -> Run -> Response flow - PASSED")
    
    print("✅ Model Integration - ALL TESTS PASSED\n")
    return True


def main():
    """Run all tests."""
    print("=" * 60)
    print("Phase 1.4: Basic Models - Comprehensive Test")
    print("=" * 60)
    print()
    
    all_passed = True
    
    try:
        all_passed &= test_request_models()
        all_passed &= test_run_models()
        all_passed &= test_response_models()
        all_passed &= test_integration()
        
        print("=" * 60)
        if all_passed:
            print("✅ ALL TESTS PASSED - Phase 1.4 is complete!")
        else:
            print("❌ SOME TESTS FAILED - Please review errors above")
        print("=" * 60)
        
        return 0 if all_passed else 1
        
    except Exception as e:
        print(f"\n❌ TEST ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())

