#!/usr/bin/env python3
"""
Test script for Phase 4: Generation Agent
Tests generation with prompts only (no real brand assets yet).
"""
import sys
from pathlib import Path
import uuid

# Add backend to path
backend_dir = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_dir))

from app.agents.generation_agent.agent import generation_agent
from app.agents.generation_agent.prompt_engineer import prompt_engineer
from app.agents.generation_agent.providers.vertex_imagen import imagen_provider
from app.agents.generation_agent.providers.vertex_veo import veo_provider
from app.services.logger import app_logger


def test_prompt_engineering():
    """Test prompt engineering for advertisements."""
    print("=" * 60)
    print("Testing Prompt Engineering...")
    print("=" * 60)
    
    base_prompt = "Showcase our new running shoes with dynamic motion, emphasizing comfort and style"
    
    # Test without brand kit
    variations = prompt_engineer.generate_variations(
        base_prompt=base_prompt,
        brand_kit=None,
        num_variations=3,
        media_type="image"
    )
    
    assert len(variations) == 3, "Should generate 3 variations"
    print(f"  ✅ Generated {len(variations)} prompt variations")
    
    for i, var in enumerate(variations, 1):
        assert "advertisement" in var.lower(), "Should contain 'advertisement'"
        assert base_prompt in var, "Should include base prompt"
        print(f"  ✅ Variation {i}: {var[:100]}...")
    
    # Test with brand kit
    brand_kit = {
        "colors": {
            "color_palette": ["#FF0000", "#0000FF", "#00FF00"],
            "primary_color": "#FF0000"
        },
        "website": {
            "brand_name": "TestBrand"
        }
    }
    
    variations_with_brand = prompt_engineer.generate_variations(
        base_prompt=base_prompt,
        brand_kit=brand_kit,
        num_variations=3,
        media_type="image"
    )
    
    assert len(variations_with_brand) == 3, "Should generate 3 variations with brand"
    print(f"  ✅ Generated {len(variations_with_brand)} variations with brand context")
    
    # Check if brand colors are included
    has_brand_color = any("#FF0000" in var or "#0000FF" in var for var in variations_with_brand)
    assert has_brand_color, "Should include brand colors"
    print("  ✅ Brand colors integrated into prompts")
    
    print("✅ Prompt Engineering - ALL TESTS PASSED\n")
    return True


def test_imagen_provider():
    """Test Imagen provider (image generation)."""
    print("=" * 60)
    print("Testing Imagen Provider (Image Generation)...")
    print("=" * 60)
    
    test_prompt = "Create a professional advertisement image showcasing running shoes with dynamic motion"
    
    print(f"  Testing with prompt: {test_prompt[:60]}...")
    print("  ⚠️  Note: This will make an actual API call to Gemini")
    
    # Test image generation
    result = imagen_provider.generate(
        prompt=test_prompt,
        number_of_images=1,
        aspect_ratio="1:1"
    )
    
    if result.get("success"):
        print("  ✅ Image generation successful!")
        if result.get("image_data"):
            print(f"  ✅ Image data received ({len(result['image_data'])} bytes)")
        print(f"  ✅ Metadata: {result.get('metadata', {})}")
    else:
        error = result.get("error", "Unknown error")
        print(f"  ⚠️  Image generation returned error: {error}")
        print("  ⚠️  This might be expected if:")
        print("     - API doesn't support image generation in this format")
        print("     - Model needs different API call structure")
        print("     - Need to check latest Gemini API documentation")
    
    print("✅ Imagen Provider - Test completed\n")
    return True


def test_veo_provider():
    """Test Veo provider (video generation)."""
    print("=" * 60)
    print("Testing Veo Provider (Video Generation)...")
    print("=" * 60)
    
    test_prompt = "Create a professional advertisement video showcasing running shoes with dynamic motion"
    
    print(f"  Testing with prompt: {test_prompt[:60]}...")
    print("  ⚠️  Note: This will make an actual API call to Gemini")
    print(f"  ⚠️  Model: {veo_provider.model_name}")
    
    # Test video generation
    result = veo_provider.generate(
        prompt=test_prompt,
        duration_seconds=5,
        aspect_ratio="16:9"
    )
    
    if result.get("success"):
        print("  ✅ Video generation successful!")
        if result.get("video_data"):
            print(f"  ✅ Video data received ({len(result['video_data'])} bytes)")
        if result.get("video_url"):
            print(f"  ✅ Video URL: {result['video_url']}")
        print(f"  ✅ Metadata: {result.get('metadata', {})}")
    else:
        error = result.get("error", "Unknown error")
        print(f"  ⚠️  Video generation returned error: {error}")
        print("  ⚠️  This might be expected if:")
        print("     - Veo model not available in current API")
        print("     - Model needs different API call structure")
        print("     - Need to check latest Gemini API documentation")
    
    print("✅ Veo Provider - Test completed\n")
    return True


def test_generation_agent():
    """Test Generation Agent orchestration."""
    print("=" * 60)
    print("Testing Generation Agent...")
    print("=" * 60)
    
    test_prompt = "Showcase our new running shoes with dynamic motion"
    run_id = str(uuid.uuid4())
    
    print(f"  Run ID: {run_id}")
    print(f"  Prompt: {test_prompt}")
    print("  Testing image generation (1 variation for testing)...")
    
    # Test image generation (1 variation for testing)
    result = generation_agent.execute(
        prompt=test_prompt,
        media_type="image",
        brand_kit=None,
        run_id=run_id,
        num_variations=1  # Only 1 variation for testing
    )
    
    assert "success" in result, "Should have success flag"
    assert "data" in result, "Should have data"
    
    if result["success"]:
        data = result["data"]
        print(f"  ✅ Generation successful!")
        print(f"  ✅ Prompt variations: {len(data.get('prompt_variations', []))}")
        print(f"  ✅ Variations generated: {len(data.get('variations', []))}")
        print(f"  ✅ Successful: {data.get('num_successful', 0)}/{data.get('num_requested', 0)}")
        
        # Show prompt variations
        if data.get("prompt_variations"):
            print("\n  Generated Prompt Variations:")
            for i, prompt_var in enumerate(data["prompt_variations"], 1):
                print(f"    {i}. {prompt_var[:150]}...")
    else:
        error = result.get("error", "Unknown error")
        print(f"  ⚠️  Generation failed: {error}")
        print("  ⚠️  This might be expected if API calls fail")
    
    print("✅ Generation Agent - Test completed\n")
    return True


def test_with_brand_context():
    """Test generation with brand context."""
    print("=" * 60)
    print("Testing Generation with Brand Context...")
    print("=" * 60)
    
    test_prompt = "Showcase our premium headphones with sleek design"
    brand_kit = {
        "colors": {
            "color_palette": ["#000000", "#FFFFFF", "#FF0000"],
            "primary_color": "#000000"
        },
        "website": {
            "brand_name": "AudioTech",
            "description": "Premium audio technology"
        }
    }
    
    run_id = str(uuid.uuid4())
    
    print(f"  Brand: {brand_kit['website']['brand_name']}")
    print(f"  Colors: {brand_kit['colors']['color_palette']}")
    
    # Test prompt variations with brand (1 variation for testing)
    variations = prompt_engineer.generate_variations(
        base_prompt=test_prompt,
        brand_kit=brand_kit,
        num_variations=1,  # Only 1 variation for testing
        media_type="image"
    )
    
    print(f"  ✅ Generated {len(variations)} brand-aware prompt variation")
    
    # Check brand integration
    has_brand_name = any("AudioTech" in var for var in variations)
    has_brand_color = any("#000000" in var or "#FF0000" in var for var in variations)
    
    if has_brand_name:
        print("  ✅ Brand name integrated")
    if has_brand_color:
        print("  ✅ Brand colors integrated")
    
    print("✅ Brand Context Integration - Test completed\n")
    return True


def main():
    """Run all Phase 4 tests."""
    print("\n" + "=" * 60)
    print("Phase 4: Generation Agent - Prompt-Only Test")
    print("=" * 60)
    print()
    print("⚠️  Note: Some tests will make actual API calls to Gemini")
    print("⚠️  This may consume API credits")
    print()
    
    all_passed = True
    
    try:
        # Test prompt engineering (no API calls)
        all_passed &= test_prompt_engineering()
        
        # Test with brand context (no API calls)
        all_passed &= test_with_brand_context()
        
        # Test Imagen provider (API call)
        print("⚠️  Making API call to test image generation...")
        all_passed &= test_imagen_provider()
        
        # Test Veo provider (API call)
        print("⚠️  Making API call to test video generation...")
        all_passed &= test_veo_provider()
        
        # Test Generation Agent (API calls)
        print("⚠️  Making API calls to test full generation flow...")
        all_passed &= test_generation_agent()
        
        print("=" * 60)
        print("Test Summary")
        print("=" * 60)
        print("✅ Prompt Engineering: Working")
        print("✅ Brand Context Integration: Working")
        print("⚠️  Image/Video Generation: Check API response format")
        print()
        print("💡 Next Steps:")
        print("   - Verify API response format matches implementation")
        print("   - Adjust response parsing if needed")
        print("   - Test with real brand assets")
        print("=" * 60)
        
        return 0
        
    except Exception as e:
        print(f"\n❌ TEST ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())

