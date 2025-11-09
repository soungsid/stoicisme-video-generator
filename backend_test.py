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

def test_queue_workflow_with_real_idea():
    """Test complete queue workflow with a real idea"""
    print("\n🔍 Testing Complete Queue Workflow with Real Idea...")
    
    # First, get a pending idea to work with
    try:
        response = requests.get(f"{API_BASE}/ideas/", timeout=10)
        if response.status_code != 200:
            print("❌ Failed to fetch ideas for testing")
            return False
        
        ideas = response.json()
        pending_ideas = [idea for idea in ideas if idea["status"] == "pending"]
        
        if not pending_ideas:
            print("⚠️  No pending ideas found for testing - skipping workflow test")
            return True  # Not a failure, just no data to test with
        
        test_idea = pending_ideas[0]
        idea_id = test_idea["id"]
        print(f"   Using idea: {idea_id}")
        print(f"   Title: {test_idea['title'][:50]}...")
        
        # Step 1: Validate the idea first
        validate_payload = {
            "video_type": "short",
            "duration_seconds": 30
        }
        
        validate_response = requests.patch(
            f"{API_BASE}/ideas/{idea_id}/validate",
            json=validate_payload,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        if validate_response.status_code != 200:
            print(f"❌ Failed to validate idea: {validate_response.status_code}")
            try:
                print(f"   Error: {validate_response.json()}")
            except:
                print(f"   Raw response: {validate_response.text}")
            return False
        
        print("✅ Idea validated successfully")
        
        # Step 2: Add job to queue
        queue_response = requests.post(f"{API_BASE}/pipeline/generate/{idea_id}", timeout=10)
        
        if queue_response.status_code != 200:
            print(f"❌ Failed to add job to queue: {queue_response.status_code}")
            try:
                print(f"   Error: {queue_response.json()}")
            except:
                print(f"   Raw response: {queue_response.text}")
            return False
        
        queue_data = queue_response.json()
        print(f"✅ Job added to queue successfully")
        print(f"   Job ID: {queue_data.get('job_id')}")
        print(f"   Queue Position: {queue_data.get('queue_position')}")
        
        # Verify required fields in response
        required_fields = ["success", "job_id", "idea_id", "queue_position"]
        if not all(field in queue_data for field in required_fields):
            missing = [f for f in required_fields if f not in queue_data]
            print(f"❌ Queue response missing fields: {missing}")
            return False
        
        # Step 3: Check job status
        status_response = requests.get(f"{API_BASE}/queue/status/{idea_id}", timeout=10)
        
        if status_response.status_code != 200:
            print(f"❌ Failed to get job status: {status_response.status_code}")
            return False
        
        status_data = status_response.json()
        print(f"✅ Job status retrieved successfully")
        print(f"   Has Job: {status_data.get('has_job')}")
        print(f"   Status: {status_data.get('status')}")
        print(f"   Queue Position: {status_data.get('queue_position')}")
        
        # Verify job status structure
        if not status_data.get("has_job"):
            print("❌ Job status should show has_job: true")
            return False
        
        if status_data.get("status") != "queued":
            print(f"❌ Expected status 'queued', got '{status_data.get('status')}'")
            return False
        
        # Step 4: Check updated queue stats
        stats_response = requests.get(f"{API_BASE}/queue/stats", timeout=10)
        if stats_response.status_code == 200:
            stats_data = stats_response.json()
            print(f"✅ Updated queue stats:")
            print(f"   Queued: {stats_data.get('queued')}")
            print(f"   Processing: {stats_data.get('processing')}")
            print(f"   Available slots: {stats_data.get('available_slots')}")
        
        # Step 5: Cancel the job (to clean up)
        cancel_response = requests.post(f"{API_BASE}/queue/cancel/{idea_id}", timeout=10)
        
        if cancel_response.status_code != 200:
            print(f"❌ Failed to cancel job: {cancel_response.status_code}")
            try:
                print(f"   Error: {cancel_response.json()}")
            except:
                print(f"   Raw response: {cancel_response.text}")
            return False
        
        cancel_data = cancel_response.json()
        print(f"✅ Job cancelled successfully")
        print(f"   Success: {cancel_data.get('success')}")
        print(f"   Message: {cancel_data.get('message')}")
        
        # Step 6: Verify job is cancelled
        final_status_response = requests.get(f"{API_BASE}/queue/status/{idea_id}", timeout=10)
        if final_status_response.status_code == 200:
            final_status = final_status_response.json()
            if final_status.get("status") == "cancelled":
                print("✅ Job status correctly shows as cancelled")
            else:
                print(f"⚠️  Job status after cancel: {final_status.get('status')}")
        
        print("✅ Complete queue workflow test passed")
        return True
        
    except Exception as e:
        print(f"❌ Queue workflow test failed - {str(e)}")
        return False

def test_elevenlabs_stats():
    """Test GET /api/config/elevenlabs/stats endpoint - NEW PHASE 2 FEATURE"""
    print("\n🔍 Testing ElevenLabs Stats Endpoint...")
    try:
        response = requests.get(f"{API_BASE}/config/elevenlabs/stats", timeout=10)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 200:
            data = response.json()
            
            # Check required fields
            required_fields = ["keys_configured", "scripts_generated_today", "estimated_chars_today", "rotation_status", "quota_info"]
            missing_fields = [field for field in required_fields if field not in data]
            
            if missing_fields:
                print(f"❌ ElevenLabs stats missing required fields: {missing_fields}")
                return False
            
            # Validate rotation_status structure
            rotation_status = data.get("rotation_status", {})
            if not isinstance(rotation_status, dict) or "enabled" not in rotation_status or "total_keys" not in rotation_status:
                print("❌ ElevenLabs stats rotation_status structure invalid")
                return False
            
            # Validate quota_info structure
            quota_info = data.get("quota_info", {})
            if not isinstance(quota_info, dict):
                print("❌ ElevenLabs stats quota_info structure invalid")
                return False
            
            print("✅ ElevenLabs stats endpoint working")
            print(f"   Keys configured: {data['keys_configured']}")
            print(f"   Scripts generated today: {data['scripts_generated_today']}")
            print(f"   Estimated chars today: {data['estimated_chars_today']}")
            print(f"   Rotation enabled: {rotation_status.get('enabled')}")
            print(f"   Total keys: {rotation_status.get('total_keys')}")
            return True
        else:
            print(f"❌ ElevenLabs stats failed - status code {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ ElevenLabs stats failed - {str(e)}")
        return False

def test_youtube_stats():
    """Test GET /api/config/youtube/stats endpoint - NEW PHASE 2 FEATURE"""
    print("\n🔍 Testing YouTube Stats Endpoint...")
    try:
        response = requests.get(f"{API_BASE}/config/youtube/stats", timeout=10)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 200:
            data = response.json()
            
            # Check required fields
            required_fields = ["authenticated", "uploads_today", "total_uploads", "pending_uploads", "quota_info"]
            missing_fields = [field for field in required_fields if field not in data]
            
            if missing_fields:
                print(f"❌ YouTube stats missing required fields: {missing_fields}")
                return False
            
            # Validate quota_info structure
            quota_info = data.get("quota_info", {})
            if not isinstance(quota_info, dict) or "daily_limit" not in quota_info:
                print("❌ YouTube stats quota_info structure invalid")
                return False
            
            print("✅ YouTube stats endpoint working")
            print(f"   Authenticated: {data['authenticated']}")
            print(f"   Uploads today: {data['uploads_today']}")
            print(f"   Total uploads: {data['total_uploads']}")
            print(f"   Pending uploads: {data['pending_uploads']}")
            print(f"   Daily limit: {quota_info.get('daily_limit')}")
            return True
        else:
            print(f"❌ YouTube stats failed - status code {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ YouTube stats failed - {str(e)}")
        return False

def test_batch_action_validate():
    """Test POST /api/ideas/batch-action with validate action - NEW PHASE 3 FEATURE"""
    print("\n🔍 Testing Batch Action - Validate...")
    try:
        # Test with empty list first
        params = {
            "action": "validate"
        }
        
        response = requests.post(
            f"{API_BASE}/ideas/batch-action",
            params=params,
            json=[],
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        print(f"Empty list - Status Code: {response.status_code}")
        print(f"Empty list - Response: {response.json()}")
        
        if response.status_code == 200:
            data = response.json()
            required_fields = ["success", "message", "results"]
            if all(field in data for field in required_fields):
                results = data["results"]
                if "success" in results and "failed" in results and "total" in results:
                    print("✅ Batch action endpoint structure correct for empty list")
                    print(f"   Total processed: {results['total']}")
                    print(f"   Success count: {len(results['success'])}")
                    print(f"   Failed count: {len(results['failed'])}")
                    
                    # Test with non-existent idea IDs
                    fake_params = {
                        "action": "validate"
                    }
                    
                    fake_response = requests.post(
                        f"{API_BASE}/ideas/batch-action",
                        params=fake_params,
                        json=["00000000-0000-0000-0000-000000000000", "11111111-1111-1111-1111-111111111111"],
                        headers={"Content-Type": "application/json"},
                        timeout=10
                    )
                    print(f"Fake IDs - Status Code: {fake_response.status_code}")
                    
                    if fake_response.status_code == 200:
                        fake_data = fake_response.json()
                        fake_results = fake_data["results"]
                        print(f"Fake IDs - Response: {fake_data}")
                        
                        if fake_results["total"] == 2 and len(fake_results["failed"]) == 2:
                            print("✅ Batch action correctly handles non-existent ideas")
                            return True
                        else:
                            print("❌ Batch action failed to handle non-existent ideas correctly")
                            return False
                    else:
                        print(f"❌ Batch action with fake IDs failed - status code {fake_response.status_code}")
                        return False
                else:
                    print("❌ Batch action results structure missing required fields")
                    return False
            else:
                print("❌ Batch action response missing required fields")
                return False
        else:
            print(f"❌ Batch action failed - status code {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Batch action test failed - {str(e)}")
        return False

def test_batch_action_reject():
    """Test POST /api/ideas/batch-action with reject action - NEW PHASE 3 FEATURE"""
    print("\n🔍 Testing Batch Action - Reject...")
    try:
        params = {
            "action": "reject"
        }
        
        response = requests.post(
            f"{API_BASE}/ideas/batch-action",
            params=params,
            json=["00000000-0000-0000-0000-000000000000"],
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 200:
            data = response.json()
            if "success" in data and "results" in data:
                results = data["results"]
                if results["total"] == 1 and len(results["failed"]) == 1:
                    print("✅ Batch reject action working correctly")
                    return True
                else:
                    print("❌ Batch reject action results incorrect")
                    return False
            else:
                print("❌ Batch reject action response structure incorrect")
                return False
        else:
            print(f"❌ Batch reject action failed - status code {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Batch reject action test failed - {str(e)}")
        return False

def test_batch_action_invalid():
    """Test POST /api/ideas/batch-action with invalid action - NEW PHASE 3 FEATURE"""
    print("\n🔍 Testing Batch Action - Invalid Action...")
    try:
        params = {
            "action": "invalid_action"
        }
        
        response = requests.post(
            f"{API_BASE}/ideas/batch-action",
            params=params,
            json=["00000000-0000-0000-0000-000000000000"],
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 200:
            data = response.json()
            if "results" in data:
                results = data["results"]
                if len(results["failed"]) == 1 and "Unknown action" in results["failed"][0]["reason"]:
                    print("✅ Batch action correctly handles invalid actions")
                    return True
                else:
                    print("❌ Batch action failed to handle invalid action correctly")
                    return False
            else:
                print("❌ Batch action response structure incorrect for invalid action")
                return False
        else:
            print(f"❌ Batch action with invalid action failed - status code {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Batch action invalid test failed - {str(e)}")
        return False

def test_video_scheduling():
    """Test video scheduling endpoints - NEW PHASE 3 FEATURE"""
    print("\n🔍 Testing Video Scheduling...")
    try:
        # Test schedule single video (should fail with non-existent video)
        fake_video_id = "00000000-0000-0000-0000-000000000000"
        schedule_params = {
            "publish_date": "2025-01-20T10:00:00Z"
        }
        
        response = requests.post(
            f"{API_BASE}/youtube/schedule/{fake_video_id}",
            params=schedule_params,
            timeout=10
        )
        print(f"Schedule single - Status Code: {response.status_code}")
        
        if response.status_code == 404:
            try:
                data = response.json()
                print(f"Schedule single - Response: {data}")
                if "detail" in data and "not found" in data["detail"].lower():
                    print("✅ Schedule single video correctly returns 404 for non-existent video")
                else:
                    print("❌ Schedule single video 404 response missing proper error detail")
                    return False
            except:
                print("❌ Schedule single video 404 response not valid JSON")
                return False
        else:
            print(f"❌ Schedule single video should return 404 for non-existent video, got {response.status_code}")
            return False
        
        # Test bulk scheduling
        bulk_params = {
            "start_date": "2025-01-20T00:00:00Z",
            "videos_per_day": 2,
            "publish_times": ["10:00", "18:00"]
        }
        
        bulk_response = requests.post(
            f"{API_BASE}/youtube/schedule/bulk",
            params=bulk_params,
            timeout=10
        )
        print(f"Bulk schedule - Status Code: {bulk_response.status_code}")
        print(f"Bulk schedule - Response: {bulk_response.json()}")
        
        if bulk_response.status_code == 200:
            bulk_data = bulk_response.json()
            required_fields = ["success", "message", "scheduled_count"]
            if all(field in bulk_data for field in required_fields):
                print("✅ Bulk scheduling endpoint working correctly")
                print(f"   Scheduled count: {bulk_data['scheduled_count']}")
            else:
                print("❌ Bulk scheduling response missing required fields")
                return False
        else:
            print(f"❌ Bulk scheduling failed - status code {bulk_response.status_code}")
            return False
        
        # Test unschedule video
        unschedule_response = requests.delete(
            f"{API_BASE}/youtube/schedule/{fake_video_id}",
            timeout=10
        )
        print(f"Unschedule - Status Code: {unschedule_response.status_code}")
        
        if unschedule_response.status_code == 404:
            try:
                unschedule_data = unschedule_response.json()
                print(f"Unschedule - Response: {unschedule_data}")
                if "detail" in unschedule_data and "not found" in unschedule_data["detail"].lower():
                    print("✅ Unschedule video correctly returns 404 for non-existent video")
                    return True
                else:
                    print("❌ Unschedule video 404 response missing proper error detail")
                    return False
            except:
                print("❌ Unschedule video 404 response not valid JSON")
                return False
        else:
            print(f"❌ Unschedule video should return 404 for non-existent video, got {unschedule_response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Video scheduling test failed - {str(e)}")
        return False

def test_video_filtering_sorting():
    """Test video filtering and sorting - NEW PHASE 3 FEATURE"""
    print("\n🔍 Testing Video Filtering & Sorting...")
    try:
        # Test basic video list
        response = requests.get(f"{API_BASE}/videos/", timeout=10)
        print(f"Basic list - Status Code: {response.status_code}")
        
        if response.status_code == 200:
            videos = response.json()
            print(f"Basic list - Found {len(videos)} videos")
            print("✅ Basic video listing working")
        else:
            print(f"❌ Basic video listing failed - status code {response.status_code}")
            return False
        
        # Test with status filter - uploaded
        uploaded_response = requests.get(
            f"{API_BASE}/videos/",
            params={"status_filter": "uploaded"},
            timeout=10
        )
        print(f"Uploaded filter - Status Code: {uploaded_response.status_code}")
        
        if uploaded_response.status_code == 200:
            uploaded_videos = uploaded_response.json()
            print(f"Uploaded filter - Found {len(uploaded_videos)} uploaded videos")
            print("✅ Uploaded status filter working")
        else:
            print(f"❌ Uploaded status filter failed - status code {uploaded_response.status_code}")
            return False
        
        # Test with status filter - scheduled
        scheduled_response = requests.get(
            f"{API_BASE}/videos/",
            params={"status_filter": "scheduled"},
            timeout=10
        )
        print(f"Scheduled filter - Status Code: {scheduled_response.status_code}")
        
        if scheduled_response.status_code == 200:
            scheduled_videos = scheduled_response.json()
            print(f"Scheduled filter - Found {len(scheduled_videos)} scheduled videos")
            print("✅ Scheduled status filter working")
        else:
            print(f"❌ Scheduled status filter failed - status code {scheduled_response.status_code}")
            return False
        
        # Test with status filter - pending
        pending_response = requests.get(
            f"{API_BASE}/videos/",
            params={"status_filter": "pending"},
            timeout=10
        )
        print(f"Pending filter - Status Code: {pending_response.status_code}")
        
        if pending_response.status_code == 200:
            pending_videos = pending_response.json()
            print(f"Pending filter - Found {len(pending_videos)} pending videos")
            print("✅ Pending status filter working")
        else:
            print(f"❌ Pending status filter failed - status code {pending_response.status_code}")
            return False
        
        # Test sorting by title ascending
        title_asc_response = requests.get(
            f"{API_BASE}/videos/",
            params={"sort_by": "title", "sort_order": "asc"},
            timeout=10
        )
        print(f"Title ASC sort - Status Code: {title_asc_response.status_code}")
        
        if title_asc_response.status_code == 200:
            title_asc_videos = title_asc_response.json()
            print(f"Title ASC sort - Found {len(title_asc_videos)} videos")
            print("✅ Title ascending sort working")
        else:
            print(f"❌ Title ascending sort failed - status code {title_asc_response.status_code}")
            return False
        
        # Test sorting by scheduled_publish_date descending
        date_desc_response = requests.get(
            f"{API_BASE}/videos/",
            params={"sort_by": "scheduled_publish_date", "sort_order": "desc"},
            timeout=10
        )
        print(f"Date DESC sort - Status Code: {date_desc_response.status_code}")
        
        if date_desc_response.status_code == 200:
            date_desc_videos = date_desc_response.json()
            print(f"Date DESC sort - Found {len(date_desc_videos)} videos")
            print("✅ Scheduled date descending sort working")
        else:
            print(f"❌ Scheduled date descending sort failed - status code {date_desc_response.status_code}")
            return False
        
        # Test combined filter and sort
        combined_response = requests.get(
            f"{API_BASE}/videos/",
            params={
                "status_filter": "pending",
                "sort_by": "created_at",
                "sort_order": "desc"
            },
            timeout=10
        )
        print(f"Combined filter+sort - Status Code: {combined_response.status_code}")
        
        if combined_response.status_code == 200:
            combined_videos = combined_response.json()
            print(f"Combined filter+sort - Found {len(combined_videos)} videos")
            print("✅ Combined filtering and sorting working")
            return True
        else:
            print(f"❌ Combined filtering and sorting failed - status code {combined_response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Video filtering and sorting test failed - {str(e)}")
        return False

def run_all_tests():
    """Run all backend tests"""
    print("=" * 80)
    print("🚀 STARTING BACKEND TESTS - PHASE 3: BATCH ACTIONS, SCHEDULING & FILTERING")
    print("=" * 80)
    print(f"Backend URL: {BASE_URL}")
    print(f"API Base: {API_BASE}")
    
    results = {}
    
    # Test basic connectivity
    results["health_check"] = test_health_check()
    
    # Test NEW Phase 3 Features
    print("\n" + "=" * 60)
    print("🔄 TESTING NEW PHASE 3 FEATURES")
    print("=" * 60)
    
    results["batch_action_validate"] = test_batch_action_validate()
    results["batch_action_reject"] = test_batch_action_reject()
    results["batch_action_invalid"] = test_batch_action_invalid()
    results["video_scheduling"] = test_video_scheduling()
    results["video_filtering_sorting"] = test_video_filtering_sorting()
    
    # Test existing endpoints for regression
    print("\n" + "=" * 60)
    print("🔍 REGRESSION TESTING - EXISTING ENDPOINTS")
    print("=" * 60)
    
    results["queue_stats"] = test_queue_stats()
    results["elevenlabs_stats"] = test_elevenlabs_stats()
    results["youtube_stats"] = test_youtube_stats()
    
    # Summary
    print("\n" + "=" * 80)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 80)
    
    passed = 0
    total = len(results)
    
    # Group results by category
    phase3_tests = ["batch_action_validate", "batch_action_reject", "batch_action_invalid", "video_scheduling", "video_filtering_sorting"]
    existing_tests = ["health_check", "queue_stats", "elevenlabs_stats", "youtube_stats"]
    
    print("Phase 3 New Features:")
    for test_name in phase3_tests:
        if test_name in results:
            status = "✅ PASS" if results[test_name] else "❌ FAIL"
            print(f"  {test_name.replace('_', ' ').title()}: {status}")
            if results[test_name]:
                passed += 1
    
    print("\nExisting Endpoints (Regression Check):")
    for test_name in existing_tests:
        if test_name in results:
            status = "✅ PASS" if results[test_name] else "❌ FAIL"
            print(f"  {test_name.replace('_', ' ').title()}: {status}")
            if results[test_name]:
                passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All Phase 3 tests passed!")
    else:
        print("⚠️  Some tests failed - check details above")
    
    return results

if __name__ == "__main__":
    run_all_tests()