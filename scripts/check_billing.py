#!/usr/bin/env python3
"""
Check GCP billing account status for the project.
"""
import sys
from pathlib import Path

backend_dir = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_dir))

from app.config import settings

print("=" * 60)
print("GCP Billing Account Check")
print("=" * 60)
print(f"Project ID: {settings.GCP_PROJECT_ID}")
print()
print("To check billing account:")
print(f"1. Go to: https://console.cloud.google.com/billing?project={settings.GCP_PROJECT_ID}")
print()
print("2. Or check in GCP Console:")
print("   - Navigate to: Billing → Account Management")
print(f"   - Look for project: {settings.GCP_PROJECT_ID}")
print()
print("3. Make sure:")
print("   - A billing account is linked to this project")
print("   - Billing is enabled")
print("   - You have $25 in credits available")
print()
print("4. Enable required APIs:")
print(f"   - Go to: https://console.cloud.google.com/apis/library?project={settings.GCP_PROJECT_ID}")
print("   - Enable: 'Generative Language API'")
print("   - Enable: 'Vertex AI API'")
print("=" * 60)

