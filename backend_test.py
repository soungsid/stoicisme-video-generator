#!/usr/bin/env python3
"""
Backend Testing Suite for YouTube Integration
Tests all YouTube API endpoints and configuration endpoints
"""

import requests
import json
import os
from urllib.parse import urlparse, parse_qs

# Get backend URL from frontend .env
def get_backend_url():
    try:
        with open('/app/frontend/.env', 'r') as f:
            for line in f:
                if line.startswith('REACT_APP_BACKEND_URL='):
                    return line.split('=', 1)[1].strip()
    except Exception as e:
        print(f"Error reading frontend .env: {e}")
    return "https://stoictubemaker.preview.emergentagent.com"

BASE_URL = get_backend_url()
API_BASE = f"{BASE_URL}/api"

def test_health_check():
    """Test basic health check endpoint"""
    print("\n🔍 Testing Health Check...")
    try:
        response = requests.get(f"{API_BASE}/health", timeout=10)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "healthy":
                print("✅ Health check passed")
                return True
            else:
                print("❌ Health check failed - unexpected response")
                return False
        else:
            print(f"❌ Health check failed - status code {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check failed - {str(e)}")
        return False

def test_youtube_config():
    """Test GET /api/youtube/config endpoint"""
    print("\n🔍 Testing YouTube Config Endpoint...")
    try:
        response = requests.get(f"{API_BASE}/youtube/config", timeout=10)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 200:
            data = response.json()
            # Should have is_authenticated field
            if "is_authenticated" in data:
                print("✅ YouTube config endpoint working")
                print(f"   Authentication Status: {data['is_authenticated']}")
                if data.get("client_id"):
                    print(f"   Client ID configured: {data['client_id'][:10]}...")
                return True
            else:
                print("❌ YouTube config missing required fields")
                return False
        else:
            print(f"❌ YouTube config failed - status code {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ YouTube config failed - {str(e)}")
        return False

def test_youtube_auth_url():
    """Test GET /api/youtube/auth/url endpoint"""
    print("\n🔍 Testing YouTube Auth URL Generation...")
    try:
        response = requests.get(f"{API_BASE}/youtube/auth/url", timeout=10)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Response: {data}")
            
            if "auth_url" in data:
                auth_url = data["auth_url"]
                print(f"✅ Auth URL generated successfully")
                
                # Validate URL structure
                parsed_url = urlparse(auth_url)
                if parsed_url.netloc == "accounts.google.com":
                    print("   ✅ Valid Google OAuth URL")
                    
                    # Check for required parameters
                    query_params = parse_qs(parsed_url.query)
                    if "client_id" in query_params:
                        print(f"   ✅ Client ID present in URL")
                    else:
                        print("   ⚠️  Client ID missing from URL")
                    
                    if "scope" in query_params:
                        print(f"   ✅ Scopes present: {query_params['scope'][0]}")
                    
                    return True
                else:
                    print("   ❌ Invalid OAuth URL domain")
                    return False
            else:
                print("❌ Auth URL missing from response")
                return False
        else:
            print(f"❌ Auth URL generation failed - status code {response.status_code}")
            if response.status_code == 500:
                try:
                    error_data = response.json()
                    print(f"   Error details: {error_data.get('detail', 'No details')}")
                except:
                    print(f"   Raw response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Auth URL generation failed - {str(e)}")
        return False

def test_youtube_channel_info():
    """Test GET /api/youtube/channel-info endpoint"""
    print("\n🔍 Testing YouTube Channel Info...")
    try:
        response = requests.get(f"{API_BASE}/youtube/channel-info", timeout=10)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Response: {data}")
            
            # Should have channel information
            required_fields = ["id", "title", "subscriber_count", "video_count"]
            if all(field in data for field in required_fields):
                print("✅ Channel info retrieved successfully")
                print(f"   Channel: {data['title']}")
                print(f"   Subscribers: {data['subscriber_count']}")
                print(f"   Videos: {data['video_count']}")
                return True
            else:
                print("❌ Channel info missing required fields")
                return False
        elif response.status_code == 500:
            # Expected if not authenticated
            try:
                error_data = response.json()
                error_detail = error_data.get('detail', '')
                if "not authenticated" in error_detail.lower() or "oauth" in error_detail.lower():
                    print("✅ Correctly returns error when not authenticated")
                    print(f"   Error: {error_detail}")
                    return True
                else:
                    print(f"❌ Unexpected error: {error_detail}")
                    return False
            except:
                print(f"❌ Unexpected 500 error: {response.text}")
                return False
        else:
            print(f"❌ Channel info failed - status code {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Channel info failed - {str(e)}")
        return False

def test_elevenlabs_config():
    """Test GET /api/config/elevenlabs endpoint"""
    print("\n🔍 Testing ElevenLabs Config...")
    try:
        response = requests.get(f"{API_BASE}/config/elevenlabs", timeout=10)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 200:
            data = response.json()
            
            # Should have api_keys array and voice settings
            if "api_keys" in data and "voice_settings" in data:
                print("✅ ElevenLabs config endpoint working")
                print(f"   Total configured keys: {data.get('total_keys', 0)}")
                print(f"   Current voice: {data['voice_settings'].get('current_voice_name', 'Unknown')}")
                return True
            else:
                print("❌ ElevenLabs config missing required fields")
                return False
        else:
            print(f"❌ ElevenLabs config failed - status code {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ ElevenLabs config failed - {str(e)}")
        return False

def test_llm_config():
    """Test GET /api/config/llm endpoint"""
    print("\n🔍 Testing LLM Config...")
    try:
        response = requests.get(f"{API_BASE}/config/llm", timeout=10)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 200:
            data = response.json()
            
            # Should have provider and provider configs
            if "provider" in data and "deepseek" in data:
                print("✅ LLM config endpoint working")
                print(f"   Current provider: {data['provider']}")
                print(f"   DeepSeek configured: {data['deepseek'].get('configured', False)}")
                print(f"   OpenAI configured: {data['openai'].get('configured', False)}")
                print(f"   Gemini configured: {data['gemini'].get('configured', False)}")
                return True
            else:
                print("❌ LLM config missing required fields")
                return False
        else:
            print(f"❌ LLM config failed - status code {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ LLM config failed - {str(e)}")
        return False

def run_all_tests():
    """Run all backend tests"""
    print("=" * 60)
    print("🚀 STARTING BACKEND TESTS FOR YOUTUBE INTEGRATION")
    print("=" * 60)
    print(f"Backend URL: {BASE_URL}")
    print(f"API Base: {API_BASE}")
    
    results = {}
    
    # Test basic connectivity
    results["health_check"] = test_health_check()
    
    # Test YouTube endpoints
    results["youtube_config"] = test_youtube_config()
    results["youtube_auth_url"] = test_youtube_auth_url()
    results["youtube_channel_info"] = test_youtube_channel_info()
    
    # Test existing config endpoints
    results["elevenlabs_config"] = test_elevenlabs_config()
    results["llm_config"] = test_llm_config()
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name.replace('_', ' ').title()}: {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed!")
    else:
        print("⚠️  Some tests failed - check details above")
    
    return results

if __name__ == "__main__":
    run_all_tests()