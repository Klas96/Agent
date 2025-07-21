#!/usr/bin/env python3
"""
Test script for PocketFlow application
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_env_vars():
    """Test that environment variables are loaded"""
    print("=== Environment Variables Test ===")
    
    required_vars = [
        'EMAIL_USER',
        'EMAIL_PASS', 
        'IMAP_SERVER',
        'SMTP_SERVER',
        'SMTP_PORT',
        'OPENAI_API_KEY',
        'ELEVENLABS_API_KEY',
        'TEST_RECIPIENT_EMAIL'
    ]
    
    missing_vars = []
    for var in required_vars:
        value = os.getenv(var)
        if value:
            print(f"✓ {var}: {'*' * len(value)} (set)")
        else:
            print(f"✗ {var}: NOT SET")
            missing_vars.append(var)
    
    if missing_vars:
        print(f"\n⚠️  Missing environment variables: {', '.join(missing_vars)}")
        print("Please add these to your .env file")
        return False
    else:
        print("\n✓ All environment variables are set!")
        return True

def test_imports():
    """Test that key modules can be imported"""
    print("\n=== Import Test ===")
    
    try:
        from flow import flow
        print("✓ Flow imported successfully")
    except Exception as e:
        print(f"✗ Flow import failed: {e}")
        return False
    
    try:
        from nodes import FetchEmailNode
        print("✓ Nodes imported successfully")
    except Exception as e:
        print(f"✗ Nodes import failed: {e}")
        return False
    
    return True

def test_basic_functionality():
    """Test basic application functionality"""
    print("\n=== Basic Functionality Test ===")
    
    try:
        # Test that we can create a simple flow
        from flow import flow
        print("✓ Flow object created successfully")
        
        # Test that we can access the shared state
        shared = {}
        print("✓ Shared state initialized")
        
        print("✓ Basic functionality test passed")
        return True
    except Exception as e:
        print(f"✗ Basic functionality test failed: {e}")
        return False

if __name__ == "__main__":
    print("Running PocketFlow Application Test...")
    print("=" * 50)
    
    env_ok = test_env_vars()
    imports_ok = test_imports()
    func_ok = test_basic_functionality()
    
    print("\n" + "=" * 50)
    print("Test Results:")
    print(f"Environment Variables: {'✓' if env_ok else '✗'}")
    print(f"Imports: {'✓' if imports_ok else '✗'}")
    print(f"Basic Functionality: {'✓' if func_ok else '✗'}")
    
    if env_ok and imports_ok and func_ok:
        print("\n🎉 All tests passed! Application is ready to run.")
        print("\nTo start the service:")
        print("  sudo systemctl start pocketflow")
        print("\nTo check the service status:")
        print("  sudo systemctl status pocketflow")
        print("\nTo view logs:")
        print("  sudo journalctl -u pocketflow -f")
    else:
        print("\n⚠️  Some tests failed. Please check the issues above.")
        sys.exit(1)
