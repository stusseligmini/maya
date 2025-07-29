"""
Test script for n8n integration with Maya AI.

This script runs basic tests against the n8n integration endpoints.
"""

import requests
import json
import time
import sys
import os
from typing import Dict, Any

# Make sure we can import from the Maya package
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from maya.config.settings import get_settings

settings = get_settings()

# Constants
API_BASE_URL = f"http://localhost:{settings.api_port}/api"
N8N_INTEGRATION_PATH = "/integrations/n8n"


def test_health_endpoint() -> bool:
    """Test the n8n health endpoint."""
    url = f"{API_BASE_URL}{N8N_INTEGRATION_PATH}/health"
    
    try:
        response = requests.get(url)
        if response.status_code == 200:
            print("✅ Health endpoint is working")
            return True
        else:
            print(f"❌ Health endpoint failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Health endpoint error: {str(e)}")
        return False


def test_webhook_endpoint() -> bool:
    """Test the n8n webhook endpoint."""
    url = f"{API_BASE_URL}{N8N_INTEGRATION_PATH}/webhook"
    
    # Test payload for content generation
    payload = {
        "action": "generate_content",
        "prompt": "Generate a test post about AI automation",
        "model_type": "openai",
        "max_tokens": 50,
        "temperature": 0.7
    }
    
    try:
        response = requests.post(
            url, 
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success", False):
                print("✅ Webhook endpoint is working")
                print(f"Generated content: {result.get('generated_content', '')}")
                return True
            else:
                print(f"❌ Webhook request failed: {result.get('error', 'Unknown error')}")
                return False
        else:
            print(f"❌ Webhook endpoint failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Webhook endpoint error: {str(e)}")
        return False


def test_task_submission() -> bool:
    """Test the n8n task submission endpoint."""
    url = f"{API_BASE_URL}{N8N_INTEGRATION_PATH}/task"
    
    # Test payload for task submission
    payload = {
        "task_type": "content_processing",
        "content": "This is a test content for processing",
        "options": {
            "analyze": True,
            "optimize": True
        }
    }
    
    try:
        response = requests.post(
            url, 
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 202:
            result = response.json()
            if result.get("success", False):
                print(f"✅ Task submission endpoint is working (Task ID: {result.get('task_id', 'Unknown')})")
                return True
            else:
                print(f"❌ Task submission failed: {result.get('error', 'Unknown error')}")
                return False
        else:
            print(f"❌ Task submission endpoint failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Task submission endpoint error: {str(e)}")
        return False


def test_platform_specs() -> bool:
    """Test the n8n platform specs endpoint."""
    url = f"{API_BASE_URL}{N8N_INTEGRATION_PATH}/platform-specs"
    
    try:
        response = requests.get(url)
        if response.status_code == 200:
            result = response.json()
            if result.get("success", False):
                print("✅ Platform specs endpoint is working")
                return True
            else:
                print(f"❌ Platform specs request failed: {result.get('error', 'Unknown error')}")
                return False
        else:
            print(f"❌ Platform specs endpoint failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Platform specs endpoint error: {str(e)}")
        return False


def run_all_tests():
    """Run all integration tests."""
    print("🧪 Running n8n integration tests...")
    
    results = {
        "health": test_health_endpoint(),
        "webhook": test_webhook_endpoint(),
        "task": test_task_submission(),
        "platform_specs": test_platform_specs()
    }
    
    # Print summary
    print("\n📊 Test Summary:")
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    # Overall result
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    
    print(f"\n🏁 Final Result: {passed}/{total} tests passed")
    
    return passed == total


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
