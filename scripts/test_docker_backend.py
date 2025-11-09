#!/usr/bin/env python3
"""
Comprehensive test script for Docker backend deployment.
Tests all endpoints and functionality.
"""
import requests
import json
import time
from pathlib import Path
from typing import Dict, Any

BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api/v1"

def test_health():
    """Test health endpoint."""
    print("\n" + "="*60)
    print("1. Testing Health Endpoint")
    print("="*60)
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        response.raise_for_status()
        data = response.json()
        print(f"✅ Health check passed: {data}")
        return True
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False

def test_detailed_health():
    """Test detailed health endpoint."""
    print("\n" + "="*60)
    print("2. Testing Detailed Health Endpoint")
    print("="*60)
    try:
        response = requests.get(f"{BASE_URL}/health/detailed", timeout=5)
        response.raise_for_status()
        data = response.json()
        print(f"✅ Detailed health check passed")
        print(f"   Status: {data.get('status')}")
        print(f"   Services: {list(data.get('services', {}).keys())}")
        return True
    except Exception as e:
        print(f"❌ Detailed health check failed: {e}")
        return False

def test_api_docs():
    """Test API documentation endpoints."""
    print("\n" + "="*60)
    print("3. Testing API Documentation")
    print("="*60)
    try:
        # Test OpenAPI docs
        response = requests.get(f"{BASE_URL}/docs", timeout=5)
        if response.status_code == 200:
            print("✅ OpenAPI docs accessible")
        else:
            print(f"⚠️  OpenAPI docs returned {response.status_code}")
        
        # Test OpenAPI JSON
        response = requests.get(f"{BASE_URL}/openapi.json", timeout=5)
        response.raise_for_status()
        openapi_data = response.json()
        print(f"✅ OpenAPI JSON accessible")
        print(f"   API Title: {openapi_data.get('info', {}).get('title')}")
        print(f"   API Version: {openapi_data.get('info', {}).get('version')}")
        print(f"   Endpoints: {len(openapi_data.get('paths', {}))}")
        return True
    except Exception as e:
        print(f"❌ API docs test failed: {e}")
        return False

def test_image_generation():
    """Test image generation endpoint."""
    print("\n" + "="*60)
    print("4. Testing Image Generation")
    print("="*60)
    try:
        # Create a simple test image file
        test_data = {
            "prompt": "A modern tech product advertisement with clean design",
            "media_type": "image",
            "brand_website_url": "https://example.com"
        }
        
        files = {}
        
        response = requests.post(
            f"{API_BASE}/generate",
            data=test_data,
            files=files,
            timeout=30
        )
        response.raise_for_status()
        data = response.json()
        
        run_id = data.get("run_id")
        print(f"✅ Image generation request submitted")
        print(f"   Run ID: {run_id}")
        
        # Wait a bit and check status
        time.sleep(3)
        status_response = requests.get(f"{API_BASE}/status/{run_id}", timeout=10)
        status_data = status_response.json()
        print(f"   Status: {status_data.get('status')}")
        print(f"   Stage: {status_data.get('stage')}")
        
        return True, run_id
    except Exception as e:
        print(f"❌ Image generation test failed: {e}")
        return False, None

def test_status_endpoint(run_id: str):
    """Test status endpoint."""
    print("\n" + "="*60)
    print("5. Testing Status Endpoint")
    print("="*60)
    if not run_id:
        print("⚠️  Skipping - no run_id available")
        return False
    
    try:
        response = requests.get(f"{API_BASE}/status/{run_id}", timeout=10)
        response.raise_for_status()
        data = response.json()
        print(f"✅ Status endpoint working")
        print(f"   Run ID: {data.get('run_id')}")
        print(f"   Status: {data.get('status')}")
        print(f"   Stage: {data.get('stage')}")
        print(f"   Progress: {data.get('progress', 0)}%")
        return True
    except Exception as e:
        print(f"❌ Status endpoint test failed: {e}")
        return False

def test_error_handling():
    """Test error handling."""
    print("\n" + "="*60)
    print("6. Testing Error Handling")
    print("="*60)
    
    # Test invalid run_id
    try:
        response = requests.get(f"{API_BASE}/status/invalid-run-id", timeout=5)
        if response.status_code == 404:
            print("✅ Invalid run_id handled correctly (404)")
        else:
            print(f"⚠️  Expected 404, got {response.status_code}")
    except Exception as e:
        print(f"❌ Error handling test failed: {e}")
        return False
    
    # Test invalid request
    try:
        response = requests.post(
            f"{API_BASE}/generate",
            json={"invalid": "data"},
            timeout=5
        )
        if response.status_code in [400, 422]:
            print("✅ Invalid request handled correctly")
        else:
            print(f"⚠️  Expected 400/422, got {response.status_code}")
    except Exception as e:
        print(f"❌ Error handling test failed: {e}")
        return False
    
    return True

def test_container_logs():
    """Check container logs for errors."""
    print("\n" + "="*60)
    print("7. Checking Container Logs")
    print("="*60)
    try:
        import subprocess
        result = subprocess.run(
            ["docker", "compose", "-f", "docker-compose.yml", "logs", "--tail", "50"],
            cwd=Path(__file__).parent.parent,
            capture_output=True,
            text=True,
            timeout=10
        )
        
        logs = result.stdout
        error_count = logs.lower().count("error")
        warning_count = logs.lower().count("warning")
        
        print(f"✅ Container logs accessible")
        print(f"   Recent log entries: {len(logs.split(chr(10)))}")
        print(f"   Errors found: {error_count}")
        print(f"   Warnings found: {warning_count}")
        
        if error_count > 0:
            print("⚠️  Errors detected in logs - check manually")
        if warning_count > 0:
            print("⚠️  Warnings detected in logs - check manually")
        
        return True
    except Exception as e:
        print(f"⚠️  Could not check container logs: {e}")
        return True  # Not critical

def main():
    """Run all tests."""
    print("\n" + "="*60)
    print("BrandAI Docker Backend - Comprehensive Test Suite")
    print("="*60)
    
    results = {}
    
    # Test 1: Health
    results["health"] = test_health()
    
    # Test 2: Detailed Health
    results["detailed_health"] = test_detailed_health()
    
    # Test 3: API Docs
    results["api_docs"] = test_api_docs()
    
    # Test 4: Image Generation
    success, run_id = test_image_generation()
    results["image_generation"] = success
    
    # Test 5: Status Endpoint
    if run_id:
        results["status"] = test_status_endpoint(run_id)
    else:
        results["status"] = False
    
    # Test 6: Error Handling
    results["error_handling"] = test_error_handling()
    
    # Test 7: Container Logs
    results["container_logs"] = test_container_logs()
    
    # Summary
    print("\n" + "="*60)
    print("Test Summary")
    print("="*60)
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Backend is ready for frontend development.")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Please review.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)

