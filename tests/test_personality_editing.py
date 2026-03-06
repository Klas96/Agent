#!/usr/bin/env python3
"""
Test Personality Editing

This test verifies that personality editing is working correctly in the dashboard.
"""

import sys
import os
sys.path.append('/opt/pocketflow')

from src.pocketflow.utils.logging import get_logger

def test_personality_editing():
    """Test personality editing functionality."""
    print("=== Testing Personality Editing ===")
    
    try:
        from src.pocketflow.services import database_service
        
        # Test user data
        test_email = "test@example.com"
        test_name = "Test User"
        test_personality = "Be helpful and friendly"
        test_tokens = 10
        
        print("✓ Database service imported successfully")
        
        # Test adding user with personality
        try:
            # Add test user
            user = database_service.create_user(
                email=test_email,
                name=test_name,
                personality=test_personality,
                tokens=test_tokens
            )
            
            if user:
                print("✓ User created with personality successfully")
            else:
                print("⚠ User may already exist (expected if test was run before)")
            
            # Test getting user with personality
            user = database_service.get_user_by_email(test_email)
            if user:
                print(f"✓ User retrieved: {user.email}")
                print(f"✓ Name: {user.name}")
                print(f"✓ Personality: {user.personality}")
                print(f"✓ Tokens: {user.tokens}")
                
                # Test updating personality
                new_personality = "Be very formal and academic"
                success = database_service.update_user_personality(
                    email=test_email,
                    personality=new_personality
                )
                
                if success:
                    print("✓ Personality updated successfully")
                    
                    # Verify the update
                    updated_user = database_service.get_user_by_email(test_email)
                    if updated_user and updated_user.personality == new_personality:
                        print("✓ Personality update verified")
                    else:
                        print("✗ Personality update verification failed")
                        return False
                else:
                    print("✗ Personality update failed")
                    return False
            else:
                print("✗ Could not retrieve user")
                return False
                
        except Exception as e:
            print(f"✗ Database operation failed: {e}")
            return False
        
        print("✓ All personality editing tests passed")
        return True
        
    except Exception as e:
        print(f"✗ Personality editing test failed: {e}")
        return False

def main():
    """Run all personality editing tests."""
    print("Personality Editing Test Suite")
    print("=" * 50)
    
    tests = [
        test_personality_editing
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 50)
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All personality editing tests passed!")
        print("✅ Personality editing is working correctly")
        return True
    else:
        print("❌ Some personality editing tests failed")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 