#!/usr/bin/env python3
"""
Test script to verify personality editing functionality
"""

import requests
import json
import sys

def test_personality_editing():
    """Test the personality editing functionality."""
    base_url = "http://localhost:5000"
    
    # Test data
    test_email = "test@example.com"
    test_personality = "Be helpful and friendly"
    
    print("Testing personality editing functionality...")
    
    try:
        # First, let's check if the user exists
        response = requests.get(f"{base_url}/admin/api/users/{test_email}")
        if response.status_code == 404:
            print("Test user not found, creating one...")
            # Create a test user
            create_data = {
                "email": test_email,
                "name": "Test User",
                "personality": "Default personality",
                "initial_tokens": 10
            }
            response = requests.post(f"{base_url}/admin/api/users", json=create_data)
            if not response.json().get("success"):
                print(f"Failed to create test user: {response.json()}")
                return False
        
        # Now test updating the personality
        update_data = {
            "name": "Test User",
            "personality": test_personality,
            "tokens": 10
        }
        
        print(f"Updating personality for {test_email}...")
        response = requests.post(
            f"{base_url}/admin/users/{test_email}/edit",
            json=update_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                print("✅ Personality update successful!")
                print(f"Updated personality: {result.get('user', {}).get('personality')}")
                return True
            else:
                print(f"❌ Personality update failed: {result.get('error')}")
                return False
        else:
            print(f"❌ HTTP error: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to the server. Make sure it's running on localhost:5000")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = test_personality_editing()
    sys.exit(0 if success else 1) 