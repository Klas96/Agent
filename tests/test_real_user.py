#!/usr/bin/env python3
"""
Test personality editing with real user
"""

import requests
import json

def test_real_user_edit():
    """Test personality editing with the real user."""
    base_url = "http://localhost:5001"
    email = "klas0holmgren@gmail.com"
    
    print(f"Testing personality editing for user: {email}")
    
    # Test data
    new_personality = "Be helpful and friendly"
    
    try:
        # 1. Get current user data
        print(f"\n1. Getting current user data...")
        response = requests.get(f"{base_url}/admin/api/users/{email}")
        if response.status_code == 200:
            user_data = response.json()
            print(f"   Current personality: {user_data['user']['personality']}")
        
        # 2. Test POST request with JSON data
        print(f"\n2. Testing personality update...")
        json_data = {
            "name": "Klas Holmgren",
            "personality": new_personality,
            "tokens": 0
        }
        response = requests.post(
            f"{base_url}/admin/users/{email}/edit",
            json=json_data,
            headers={"Content-Type": "application/json"}
        )
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text[:500]}...")
        
        # 3. Verify the update
        print(f"\n3. Verifying update...")
        response = requests.get(f"{base_url}/admin/api/users/{email}")
        if response.status_code == 200:
            user_data = response.json()
            print(f"   New personality: {user_data['user']['personality']}")
            if user_data['user']['personality'] == new_personality:
                print("   ✅ SUCCESS: Personality updated correctly!")
            else:
                print("   ❌ FAILED: Personality not updated")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    return True

if __name__ == "__main__":
    test_real_user_edit() 