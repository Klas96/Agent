#!/usr/bin/env python3
"""
Debug script to test the users route.
"""

import requests
import json

def test_users_route():
    """Test the users route directly."""
    try:
        # Test the API endpoint
        response = requests.get("http://localhost:5001/admin/api/users")
        print("API Response Status:", response.status_code)
        if response.status_code == 200:
            data = response.json()
            print("API Users Count:", len(data.get("users", [])))
            print("API Users:", data.get("users", [])[:2])  # Show first 2 users
        
        # Test the web endpoint
        response = requests.get("http://localhost:5001/admin/users")
        print("\nWeb Response Status:", response.status_code)
        
        # Check if the response contains user data
        content = response.text
        if "No users found" in content:
            print("❌ Web page shows 'No users found'")
        else:
            print("✅ Web page shows users")
        
        # Check for specific user emails in the response
        test_emails = ["test5@example.com", "test4@example.com", "test3@example.com"]
        found_emails = []
        for email in test_emails:
            if email in content:
                found_emails.append(email)
        
        if found_emails:
            print(f"✅ Found user emails in web response: {found_emails}")
        else:
            print("❌ No user emails found in web response")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_users_route() 