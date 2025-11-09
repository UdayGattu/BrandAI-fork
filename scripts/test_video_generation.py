#!/usr/bin/env python3
"""
Test script for video generation only.
Tests Veo provider with Vertex AI SDK.
"""
import sys
from pathlib import Path
import time

# Add backend to path
backend_dir = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_dir))

from app.agents.generation_agent.providers.vertex_veo import veo_provider
from app.services.logger import app_logger


def test_video_generation():
    """Test video generation with Veo."""
    print("=" * 60)
    print("Testing Video Generation (Veo Provider)")
    print("=" * 60)
    print()
    print("⚠️  Note: Video generation can take several minutes")
    print("⚠️  This will consume GCP credits")
    print()
    
    test_prompt = "A professional advertisement video showcasing running shoes with dynamic motion on a track"
    
    print(f"Prompt: {test_prompt}")
    print(f"Model: {veo_provider.model_name}")
    print(f"Provider initialized: {veo_provider._initialized}")
    print()
    print("Starting video generation...")
    print("-" * 60)
    
    start_time = time.time()
    
    result = veo_provider.generate(
        prompt=test_prompt,
        duration_seconds=8,  # 8 seconds (max for veo-2.0-generate-001)
        aspect_ratio="16:9"
    )
    
    elapsed_time = time.time() - start_time
    
    print()
    print("=" * 60)
    print("Test Results")
    print("=" * 60)
    print(f"Time elapsed: {elapsed_time:.1f} seconds")
    print(f"Success: {result.get('success')}")
    print()
    
    if result.get("success"):
        print("✅ Video generation successful!")
        print()
        
        if result.get("video_data"):
            video_size = len(result["video_data"])
            print(f"✅ Video downloaded: {video_size:,} bytes ({video_size / 1024 / 1024:.2f} MB)")
            
            # Save test video
            output_path = Path(__file__).parent.parent / "data" / "storage" / "test_video.mp4"
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_path, "wb") as f:
                f.write(result["video_data"])
            
            print(f"✅ Video saved to: {output_path}")
        elif result.get("video_uri"):
            print(f"✅ Video URI: {result['video_uri']}")
            print("   (Video is available at the GCS URI above)")
        
        print()
        print("Metadata:")
        for key, value in result.get("metadata", {}).items():
            print(f"  {key}: {value}")
    else:
        error = result.get("error", "Unknown error")
        print(f"❌ Video generation failed")
        print(f"Error: {error}")
        print()
        
        if "quota" in error.lower() or "429" in error:
            print("💡 This is a quota/rate limit error.")
            print("   Wait a minute and try again, or request quota increase.")
        elif "credentials" in error.lower():
            print("💡 Check your GCP credentials and project configuration.")
        elif "not found" in error.lower() or "404" in error:
            print("💡 Check if the Veo model is available in your region.")
    
    print()
    print("=" * 60)
    
    return result.get("success", False)


if __name__ == "__main__":
    try:
        success = test_video_generation()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Test error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

