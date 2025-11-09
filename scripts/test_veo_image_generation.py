#!/usr/bin/env python3
"""
Test script for Veo 3.1 image-to-video generation.
Tests logo/product image input support.
"""
import sys
from pathlib import Path
import time

# Add backend to path
backend_dir = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_dir))

from app.agents.generation_agent.providers.vertex_veo import veo_provider
from app.services.logger import app_logger


def test_text_only():
    """Test text-to-video (T2V) mode."""
    print("=" * 70)
    print("Test 1: Text-to-Video (T2V) Mode")
    print("=" * 70)
    print()
    
    test_prompt = "A professional advertisement video showcasing running shoes with dynamic motion on a track"
    
    print(f"Prompt: {test_prompt}")
    print(f"Model: {veo_provider.model_name}")
    print(f"Mode: Text-to-Video (no images)")
    print()
    print("Starting video generation...")
    print("-" * 70)
    
    start_time = time.time()
    
    result = veo_provider.generate(
        prompt=test_prompt,
        duration_seconds=8,
        aspect_ratio="16:9"
    )
    
    elapsed_time = time.time() - start_time
    
    print()
    print("=" * 70)
    print("Results")
    print("=" * 70)
    print(f"Time elapsed: {elapsed_time:.1f} seconds")
    print(f"Success: {result.get('success')}")
    
    if result.get("success"):
        print("✅ Video generation successful!")
        metadata = result.get("metadata", {})
        print(f"   Mode: {metadata.get('mode', 'N/A')}")
        print(f"   Has images: {metadata.get('has_images', False)}")
        if result.get("video_data"):
            print(f"   Video size: {len(result['video_data'])} bytes")
    else:
        print(f"❌ Error: {result.get('error')}")
    
    print()
    return result.get("success", False)


def test_with_logo_and_product(logo_path: Path, product_path: Path):
    """Test image-to-video (I2V) mode with both logo and product images."""
    print("=" * 70)
    print("Test 2: Image-to-Video (I2V) Mode - Logo + Product")
    print("=" * 70)
    print()
    
    if not logo_path.exists():
        print(f"❌ Logo file not found: {logo_path}")
        return False
    
    if not product_path.exists():
        print(f"❌ Product file not found: {product_path}")
        return False
    
    # Nike-specific advertisement prompt
    test_prompt = "Create a dynamic Nike advertisement video showcasing the KILLSHOT 2 LEATHER sneakers with smooth motion, professional lighting, and energetic movement. Show the shoes in action with dynamic camera angles."
    
    print(f"Logo: {logo_path.name}")
    print(f"Product: {product_path.name}")
    print(f"Prompt: {test_prompt}")
    print(f"Model: {veo_provider.model_name}")
    print(f"Mode: Image-to-Video (with logo + product)")
    print()
    print("Starting video generation...")
    print("-" * 70)
    
    start_time = time.time()
    
    result = veo_provider.generate(
        prompt=test_prompt,
        duration_seconds=8,
        aspect_ratio="16:9",
        logo_image=logo_path,
        product_image=product_path
    )
    
    elapsed_time = time.time() - start_time
    
    print()
    print("=" * 70)
    print("Results")
    print("=" * 70)
    print(f"Time elapsed: {elapsed_time:.1f} seconds")
    print(f"Success: {result.get('success')}")
    
    if result.get("success"):
        print("✅ Video generation successful!")
        metadata = result.get("metadata", {})
        print(f"   Mode: {metadata.get('mode', 'N/A')}")
        print(f"   Has images: {metadata.get('has_images', False)}")
        if result.get("video_data"):
            print(f"   Video size: {len(result['video_data'])} bytes")
            # Save test video
            output_path = Path(__file__).parent.parent / "data" / "storage" / "test_veo_i2v_nike.mp4"
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_bytes(result["video_data"])
            print(f"   ✅ Video saved to: {output_path}")
    else:
        print(f"❌ Error: {result.get('error')}")
        error_msg = result.get('error', '')
        if 'image' in error_msg.lower():
            print("   ⚠️  Image input may not be supported or image format issue")
    
    print()
    return result.get("success", False)


def main():
    """Run all tests."""
    print("\n" + "=" * 70)
    print("Veo 3.1 Image-to-Video (I2V) Test")
    print("=" * 70)
    print()
    print("⚠️  Note: Video generation can take several minutes")
    print("⚠️  This will consume GCP credits")
    print()
    
    # Test 1: Text-only (should work)
    print("\n" + "=" * 70)
    success_t2v = test_text_only()
    
    # Test 2: With logo and product images (Nike)
    print("\n" + "=" * 70)
    uploads_dir = Path(__file__).parent.parent / "data" / "storage" / "uploads"
    logo_path = uploads_dir / "Nike-Logo.jpg"
    product_path = uploads_dir / "KILLSHOT+2+LEATHER.png"
    
    if logo_path.exists() and product_path.exists():
        success_i2v = test_with_logo_and_product(logo_path, product_path)
    else:
        print("⚠️  Nike images not found. Skipping I2V test.")
        print(f"   Expected logo: {logo_path}")
        print(f"   Expected product: {product_path}")
        success_i2v = None
    
    # Summary
    print("\n" + "=" * 70)
    print("Test Summary")
    print("=" * 70)
    print(f"Text-to-Video (T2V): {'✅ PASSED' if success_t2v else '❌ FAILED'}")
    if success_i2v is not None:
        print(f"Image-to-Video (I2V): {'✅ PASSED' if success_i2v else '❌ FAILED'}")
    else:
        print(f"Image-to-Video (I2V): ⚠️  SKIPPED (no test image)")
    print("=" * 70)


if __name__ == "__main__":
    main()

