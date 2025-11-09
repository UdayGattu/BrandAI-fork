#!/usr/bin/env python3
"""
Test script to check if Veo models support image inputs.
Tests Veo 3.1 for image-to-video capability.
"""
import sys
from pathlib import Path
import base64
import requests

# Add backend to path
backend_dir = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_dir))

from app.config import settings

print("=" * 70)
print("Testing Veo Models for Image Input Support")
print("=" * 70)
print()

api_key = settings.GEMINI_API_KEY
base_url = "https://generativelanguage.googleapis.com/v1beta"

# Create a simple test image (1x1 pixel PNG)
test_image_bytes = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xdb\x00\x00\x00\x00IEND\xaeB`\x82'
test_image_b64 = base64.b64encode(test_image_bytes).decode('utf-8')

# Test models - focus on Veo 3.1 which should support images
test_models = [
    'veo-2.0-generate-001',
    'veo-3.0-generate-001',
    'veo-3.1-generate-preview',
]

for model_name in test_models:
    print(f"Testing: {model_name}")
    print("-" * 70)
    
    url = f"{base_url}/models/{model_name}:predictLongRunning"
    headers = {
        "x-goog-api-key": api_key,
        "Content-Type": "application/json"
    }
    
    # Test: Image in instances (with mimeType as API requires)
    print("  Test: Image + Prompt in instances...")
    payload = {
        "instances": [{
            "prompt": "A test video with image input",
            "image": {
                "bytesBase64Encoded": test_image_b64,
                "mimeType": "image/png"
            }
        }],
        "parameters": {}
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            if "name" in result:
                print(f"    ✅ SUCCESS! Image input accepted!")
                print(f"    Operation: {result['name'][:60]}...")
                print(f"    ⚠️  Note: This will consume credits if you poll it")
        elif response.status_code == 400:
            error_data = response.json()
            error_msg = error_data.get("error", {}).get("message", "")
            
            if "image" in error_msg.lower() and ("not supported" in error_msg.lower() or "unknown" in error_msg.lower()):
                print(f"    ❌ Image input NOT supported")
                print(f"    Error: {error_msg[:80]}")
            elif "quota" in error_msg.lower() or "billing" in error_msg.lower():
                print(f"    ✅ Image input ACCEPTED! (quota/billing issue, not code)")
                print(f"    This means the API accepts image input!")
            else:
                print(f"    ⚠️  Other error: {error_msg[:80]}")
        else:
            print(f"    ⚠️  HTTP {response.status_code}: {response.text[:80]}")
            
    except Exception as e:
        print(f"    ❌ Error: {str(e)[:80]}")
    
    print()

print("=" * 70)
print("Summary:")
print("=" * 70)
print("According to Google documentation:")
print("  ✅ Veo 3.1 supports image-to-video (I2V)")
print("  ✅ Can accept: prompt + image inputs")
print("  ✅ Features: First/Last frame, Ingredients to Video")
print()
print("If test shows 'Image input ACCEPTED' above, you can use it!")
print("=" * 70)

