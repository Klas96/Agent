#!/usr/bin/env python3
"""
Web debugging script for personality editing
"""

import requests
import json
import sys

def test_personality_editing():
    """Test the personality editing functionality via web requests."""
    base_url = "http://localhost:5001"
    
    print("Testing personality editing via web interface...")
    
    # Test data
    test_email = "test@example.com"
    test_personality = "Be helpful and friendly"
    
    try:
        # 1. Test GET request to edit page
        print(f"\n1. Testing GET /admin/users/{test_email}/edit")
        response = requests.get(f"{base_url}/admin/users/{test_email}/edit")
        print(f"   Status: {response.status_code}")
        print(f"   Content-Type: {response.headers.get('content-type', 'unknown')}")
        
        # 2. Test POST request with JSON data (what the JavaScript sends)
        print(f"\n2. Testing POST /admin/users/{test_email}/edit with JSON")
        json_data = {
            "name": "Test User",
            "personality": test_personality,
            "tokens": 100
        }
        response = requests.post(
            f"{base_url}/admin/users/{test_email}/edit",
            json=json_data,
            headers={"Content-Type": "application/json"}
        )
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text[:200]}...")
        
        # 3. Test POST request with form data (fallback)
        print(f"\n3. Testing POST /admin/users/{test_email}/edit with form data")
        form_data = {
            "name": "Test User",
            "personality": test_personality,
            "tokens": "100"
        }
        response = requests.post(
            f"{base_url}/admin/users/{test_email}/edit",
            data=form_data
        )
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text[:200]}...")
        
        # 4. Test the API endpoint that loads user data
        print(f"\n4. Testing GET /admin/api/users/{test_email}")
        response = requests.get(f"{base_url}/admin/api/users/{test_email}")
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            user_data = response.json()
            print(f"   User data: {user_data}")
        
    except requests.exceptions.ConnectionError:
        print("❌ Error: Cannot connect to the server. Make sure the application is running.")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    return True

if __name__ == "__main__":
    test_personality_editing() 