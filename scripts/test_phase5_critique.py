"""
Test script for Phase 5: Critique Agent
Tests the critique agent with generated ads (images and videos).
"""
import sys
import os
from pathlib import Path
from typing import List, Dict

# Add backend to path
backend_dir = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_dir))

# Set environment variables if needed
os.environ.setdefault("APP_ENV", "development")

from app.agents.critique_agent.agent import critique_agent
from app.agents.brand_kit_agent.agent import BrandKitAgent
from app.services.logger import app_logger
from app.config import settings


def test_critique_agent():
    """Test the critique agent with generated ads."""
    
    print("=" * 70)
    print("Phase 5: Critique Agent - Test")
    print("=" * 70)
    print()
    
    # Test data paths
    test_dir = Path(__file__).parent.parent / "data" / "storage" / "test_generation"
    images_dir = test_dir / "images"
    videos_dir = test_dir / "videos"
    
    # Brand kit data (using Nike as example)
    brand_kit = {
        "logo": {
            "file_path": str(Path(__file__).parent.parent / "data" / "storage" / "uploads" / "Nike-Logo.jpg")
        },
        "product": {
            "file_path": str(Path(__file__).parent.parent / "data" / "storage" / "uploads" / "KILLSHOT+2+LEATHER.png")
        },
        "colors": {
            "color_palette": ["#000000", "#FFFFFF", "#FF0000"]  # Black, White, Red
        },
        "website": {
            "brand_name": "Nike"
        }
    }
    
    # Check if brand assets exist
    logo_path = Path(brand_kit["logo"]["file_path"])
    product_path = Path(brand_kit["product"]["file_path"])
    
    if not logo_path.exists():
        print(f"⚠️  Logo not found: {logo_path}")
        print("   Using mock brand kit without logo reference")
        brand_kit["logo"]["file_path"] = None
    
    if not product_path.exists():
        print(f"⚠️  Product image not found: {product_path}")
        print("   Using mock brand kit without product reference")
        brand_kit["product"]["file_path"] = None
    
    print(f"📁 Test directory: {test_dir}")
    print()
    
    # Test 1: Image critique (test only 1 image)
    print("-" * 70)
    print("TEST 1: Image Critique (Single Image)")
    print("-" * 70)
    print()
    
    image_files = list(images_dir.glob("*.png")) + list(images_dir.glob("*.jpg"))
    
    if image_files:
        print(f"Found {len(image_files)} image(s) available:")
        for img in image_files:
            print(f"  - {img.name}")
        print()
        
        # Test critique on only 1 image (production-like testing)
        image_paths = [str(image_files[0])]  # Test only first image
        
        print(f"Evaluating 1 image variation (production test)...")
        print()
        
        try:
            # Test with user prompt for context
            user_prompt = "Create a dynamic advertisement for Nike running shoes"
            
            result = critique_agent.execute(
                ad_paths=image_paths,
                brand_kit=brand_kit,
                media_type="image",
                run_id="test_image_critique",
                user_prompt=user_prompt
            )
            
            if result.get("success"):
                critique_report = result["data"]["critique_report"]
                
                print("✅ Critique completed successfully!")
                print()
                print(f"📊 Report Summary:")
                print(f"   Total variations: {critique_report.total_variations}")
                print(f"   Passed: {critique_report.passed_variations}")
                print(f"   Failed: {critique_report.failed_variations}")
                print()
                
                if critique_report.best_variation:
                    print(f"🏆 Best Variation: {critique_report.best_variation.variation_id}")
                    print(f"   Overall Score: {critique_report.best_variation.overall_score:.2f}")
                    print(f"   Passed: {critique_report.best_variation.passed}")
                    print()
                
                # Show detailed scores for each variation
                print("📋 Detailed Scores:")
                print()
                for var in critique_report.all_variations:
                    print(f"   Variation: {var.variation_id}")
                    print(f"   File: {Path(var.file_path).name}")
                    print(f"   Overall Score: {var.overall_score:.2f}")
                    print(f"   Rank: {var.rank}")
                    print(f"   Passed: {var.passed}")
                    print()
                    print(f"   Dimension Scores:")
                    for scorecard in var.scorecard:
                        print(f"     - {scorecard.dimension}: {scorecard.score:.2f}")
                        print(f"       Feedback: {scorecard.feedback[:80]}...")
                        if scorecard.issues:
                            print(f"       Issues: {', '.join(scorecard.issues[:2])}")
                    print()
            else:
                print(f"❌ Critique failed: {result.get('error')}")
        except Exception as e:
            print(f"❌ Error during image critique: {e}")
            import traceback
            traceback.print_exc()
    else:
        print("⚠️  No image files found in test directory")
    
    print()
    print("-" * 70)
    print("TEST 2: Video Critique (Single Video)")
    print("-" * 70)
    print()
    
    video_files = list(videos_dir.glob("*.mp4")) + list(videos_dir.glob("*.mov"))
    
    if video_files:
        print(f"Found {len(video_files)} video(s) available:")
        for vid in video_files:
            print(f"  - {vid.name}")
        print()
        
        # Test critique on only 1 video (production-like testing)
        video_paths = [str(video_files[0])]  # Test only first video
        
        print(f"Evaluating 1 video variation (production test)...")
        print("(Note: Full video analysis with Gemini Video API)")
        print()
        
        try:
            # Test with user prompt for context
            user_prompt = "Create a dynamic video advertisement for Nike running shoes"
            
            result = critique_agent.execute(
                ad_paths=video_paths,
                brand_kit=brand_kit,
                media_type="video",
                run_id="test_video_critique",
                user_prompt=user_prompt
            )
            
            if result.get("success"):
                critique_report = result["data"]["critique_report"]
                
                print("✅ Critique completed successfully!")
                print()
                print(f"📊 Report Summary:")
                print(f"   Total variations: {critique_report.total_variations}")
                print(f"   Passed: {critique_report.passed_variations}")
                print(f"   Failed: {critique_report.failed_variations}")
                print()
                
                if critique_report.best_variation:
                    print(f"🏆 Best Variation: {critique_report.best_variation.variation_id}")
                    print(f"   Overall Score: {critique_report.best_variation.overall_score:.2f}")
                    print(f"   Passed: {critique_report.best_variation.passed}")
                    print()
                
                # Show detailed scores
                print("📋 Detailed Scores:")
                print()
                for var in critique_report.all_variations:
                    print(f"   Variation: {var.variation_id}")
                    print(f"   File: {Path(var.file_path).name}")
                    print(f"   Overall Score: {var.overall_score:.2f}")
                    print(f"   Passed: {var.passed}")
                    print()
                    print(f"   Dimension Scores:")
                    for scorecard in var.scorecard:
                        print(f"     - {scorecard.dimension}: {scorecard.score:.2f}")
                        print(f"       Feedback: {scorecard.feedback[:80]}...")
                        if scorecard.issues:
                            print(f"       Issues: {', '.join(scorecard.issues[:2])}")
                    print()
            else:
                print(f"❌ Critique failed: {result.get('error')}")
        except Exception as e:
            print(f"❌ Error during video critique: {e}")
            import traceback
            traceback.print_exc()
    else:
        print("⚠️  No video files found in test directory")
    
    print()
    print("=" * 70)
    print("Phase 5 Critique Agent Test Complete!")
    print("=" * 70)


if __name__ == "__main__":
    test_critique_agent()

