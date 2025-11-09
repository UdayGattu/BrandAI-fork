#!/usr/bin/env python3
"""
List available Gemini and Vertex AI models.
"""
import sys
from pathlib import Path

backend_dir = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_dir))

from app.config import settings
import google.generativeai as genai

print("=" * 60)
print("Available Models Check")
print("=" * 60)

# Configure Gemini
if settings.GEMINI_API_KEY:
    genai.configure(api_key=settings.GEMINI_API_KEY)
    
    print("\n📋 Listing Available Gemini Models:")
    print("-" * 60)
    try:
        models = genai.list_models()
        available_models = []
        for model in models:
            if 'generateContent' in model.supported_generation_methods:
                available_models.append(model.name)
                print(f"  ✅ {model.name}")
                if model.display_name:
                    print(f"     Display: {model.display_name}")
        
        print(f"\n📊 Total: {len(available_models)} models available")
        
        # Check for specific models we need
        print("\n🔍 Checking Required Models:")
        print("-" * 60)
        required_models = {
            "gemini-1.5-pro": "For critique text analysis",
            "gemini-1.5-pro-vision": "For critique image/video analysis",
            "gemini-1.5-flash": "For faster text analysis (optional)",
        }
        
        for model_name, purpose in required_models.items():
            # Check if model name exists in available models
            found = any(model_name in m for m in available_models)
            status = "✅" if found else "❌"
            print(f"{status} {model_name}: {purpose}")
            if not found:
                # Try to find similar model names
                similar = [m for m in available_models if model_name.split('-')[0] in m.lower()]
                if similar:
                    print(f"   Similar models found: {', '.join(similar[:3])}")
        
    except Exception as e:
        print(f"❌ Error listing models: {e}")
        print("\n💡 Try these model names manually:")
        print("   - gemini-1.5-pro")
        print("   - gemini-1.5-pro-vision")
        print("   - gemini-1.5-flash")
        print("   - gemini-pro")
else:
    print("⚠️  GEMINI_API_KEY not set")

print("\n" + "=" * 60)
print("Vertex AI Models (for Generation):")
print("-" * 60)
print("For Image Generation:")
print("  - imagegeneration@006 (Imagen 2)")
print("  - imagegeneration@005 (Imagen 2)")
print()
print("For Video Generation:")
print("  - videogeneration@006 (Veo)")
print("  - videogeneration@005 (Veo)")
print()
print("💡 Note: Vertex AI model names are accessed via API, not listed here")
print("=" * 60)

