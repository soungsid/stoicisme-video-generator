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

def test_queue_stats():
    """Test GET /api/queue/stats endpoint"""
    print("\n🔍 Testing Queue Stats...")
    try:
        response = requests.get(f"{API_BASE}/queue/stats", timeout=10)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 200:
            data = response.json()
            
            # Should have required fields
            required_fields = ["queued", "processing", "completed_today", "max_concurrent", "available_slots"]
            if all(field in data for field in required_fields):
                print("✅ Queue stats endpoint working")
                print(f"   Queued jobs: {data['queued']}")
                print(f"   Processing jobs: {data['processing']}")
                print(f"   Completed today: {data['completed_today']}")
                print(f"   Max concurrent: {data['max_concurrent']}")
                print(f"   Available slots: {data['available_slots']}")
                return True
            else:
                missing_fields = [field for field in required_fields if field not in data]
                print(f"❌ Queue stats missing required fields: {missing_fields}")
                return False
        else:
            print(f"❌ Queue stats failed - status code {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Queue stats failed - {str(e)}")
        return False

def test_job_status_nonexistent():
    """Test GET /api/queue/status/{idea_id} for non-existent job"""
    print("\n🔍 Testing Job Status for Non-existent Job...")
    try:
        # Use a random UUID that doesn't exist
        fake_idea_id = "00000000-0000-0000-0000-000000000000"
        response = requests.get(f"{API_BASE}/queue/status/{fake_idea_id}", timeout=10)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 200:
            data = response.json()
            
            # Should return has_job: false for non-existent job
            if "has_job" in data and data["has_job"] == False and "idea_id" in data:
                print("✅ Job status correctly returns no job for non-existent idea")
                print(f"   Has job: {data['has_job']}")
                print(f"   Idea ID: {data['idea_id']}")
                return True
            else:
                print("❌ Job status response structure incorrect for non-existent job")
                return False
        else:
            print(f"❌ Job status failed - status code {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Job status failed - {str(e)}")
        return False

def test_pipeline_generate_without_idea():
    """Test POST /api/pipeline/generate/{idea_id} with non-existent idea"""
    print("\n🔍 Testing Pipeline Generate with Non-existent Idea...")
    try:
        # Use a random UUID that doesn't exist
        fake_idea_id = "00000000-0000-0000-0000-000000000000"
        response = requests.post(f"{API_BASE}/pipeline/generate/{fake_idea_id}", timeout=10)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 404:
            try:
                data = response.json()
                print(f"Response: {data}")
                if "detail" in data and "not found" in data["detail"].lower():
                    print("✅ Pipeline correctly returns 404 for non-existent idea")
                    return True
                else:
                    print("❌ Pipeline 404 response missing proper error detail")
                    return False
            except:
                print("❌ Pipeline 404 response not valid JSON")
                return False
        else:
            print(f"❌ Pipeline should return 404 for non-existent idea, got {response.status_code}")
            try:
                print(f"Response: {response.json()}")
            except:
                print(f"Raw response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Pipeline generate test failed - {str(e)}")
        return False

def test_cancel_job_nonexistent():
    """Test POST /api/queue/cancel/{idea_id} with non-existent job"""
    print("\n🔍 Testing Cancel Job for Non-existent Job...")
    try:
        # Use a random UUID that doesn't exist
        fake_idea_id = "00000000-0000-0000-0000-000000000000"
        response = requests.post(f"{API_BASE}/queue/cancel/{fake_idea_id}", timeout=10)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 404:
            try:
                data = response.json()
                print(f"Response: {data}")
                if "detail" in data and "no job found" in data["detail"].lower():
                    print("✅ Cancel job correctly returns 404 for non-existent job")
                    return True
                else:
                    print("❌ Cancel job 404 response missing proper error detail")
                    return False
            except:
                print("❌ Cancel job 404 response not valid JSON")
                return False
        else:
            print(f"❌ Cancel job should return 404 for non-existent job, got {response.status_code}")
            try:
                print(f"Response: {response.json()}")
            except:
                print(f"Raw response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Cancel job test failed - {str(e)}")
        return False

def run_all_tests():
    """Run all backend tests"""
    print("=" * 80)
    print("🚀 STARTING BACKEND TESTS FOR YOUTUBE INTEGRATION & VIDEO QUEUE SYSTEM")
    print("=" * 80)
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
    
    # Test NEW Queue System endpoints
    print("\n" + "=" * 60)
    print("🎬 TESTING NEW VIDEO QUEUE SYSTEM")
    print("=" * 60)
    
    results["queue_stats"] = test_queue_stats()
    results["job_status_nonexistent"] = test_job_status_nonexistent()
    results["pipeline_generate_nonexistent"] = test_pipeline_generate_without_idea()
    results["cancel_job_nonexistent"] = test_cancel_job_nonexistent()
    
    # Summary
    print("\n" + "=" * 80)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 80)
    
    passed = 0
    total = len(results)
    
    # Group results by category
    youtube_tests = ["health_check", "youtube_config", "youtube_auth_url", "youtube_channel_info", "elevenlabs_config", "llm_config"]
    queue_tests = ["queue_stats", "job_status_nonexistent", "pipeline_generate_nonexistent", "cancel_job_nonexistent"]
    
    print("YouTube Integration Tests:")
    for test_name in youtube_tests:
        if test_name in results:
            status = "✅ PASS" if results[test_name] else "❌ FAIL"
            print(f"  {test_name.replace('_', ' ').title()}: {status}")
            if results[test_name]:
                passed += 1
    
    print("\nVideo Queue System Tests:")
    for test_name in queue_tests:
        if test_name in results:
            status = "✅ PASS" if results[test_name] else "❌ FAIL"
            print(f"  {test_name.replace('_', ' ').title()}: {status}")
            if results[test_name]:
                passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed!")
    else:
        print("⚠️  Some tests failed - check details above")
    
    return results

if __name__ == "__main__":
    run_all_tests()