#!/usr/bin/env python3
"""
Test script for PocketFlow application
"""

import os
import sys
from src.pocketflow.config.settings import get_settings

def test_env_vars():
    """Test that environment variables are loaded"""
    print("=== Environment Variables Test ===")
    
    try:
        settings = get_settings()
        print("✓ Settings loaded successfully")
        
        # Check key settings
        required_settings = [
            'EMAIL_USERNAME',
            'EMAIL_PASSWORD', 
            'EMAIL_HOST',
            'EMAIL_PORT',
            'OPENAI_API_KEY'
        ]
        
        missing_settings = []
        for setting_name in required_settings:
            value = getattr(settings, setting_name, None)
            if value:
                print(f"✓ {setting_name}: {'*' * len(str(value))} (set)")
            else:
                print(f"✗ {setting_name}: NOT SET")
                missing_settings.append(setting_name)
        
        if missing_settings:
            print(f"\n⚠️  Missing settings: {', '.join(missing_settings)}")
            print("Please add these to your .env file")
            return False
        else:
            print("\n✓ All required settings are set!")
            return True
            
    except Exception as e:
        print(f"✗ Settings loading failed: {e}")
        return False

def test_imports():
    """Test that key modules can be imported"""
    print("\n=== Import Test ===")
    
    try:
        from src.pocketflow.flows.manager import flow_manager
        print("✓ Flow manager imported successfully")
    except Exception as e:
        print(f"✗ Flow manager import failed: {e}")
        return False
    
    try:
        from src.pocketflow.nodes import FetchEmailNode
        print("✓ Nodes imported successfully")
    except Exception as e:
        print(f"✗ Nodes import failed: {e}")
        return False
    
    return True

def test_basic_functionality():
    """Test basic application functionality"""
    print("\n=== Basic Functionality Test ===")
    
    try:
        # Test that we can create a flow manager
        from src.pocketflow.flows.manager import flow_manager
        print("✓ Flow manager created successfully")
        
        # Test that we can access the shared state
        from src.pocketflow.core.types import SharedState
        shared = SharedState()
        print("✓ Shared state initialized")
        
        # Test that we can get available flows
        flows = flow_manager.get_available_flows()
        print(f"✓ Available flows: {len(flows)} flows found")
        
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
