#!/usr/bin/env python3
"""
Test PocketFlow Application

This test verifies that the PocketFlow application is properly configured and can run.
"""

import sys
import os
sys.path.append('/opt/pocketflow')

from src.pocketflow.config.settings import get_settings
from src.pocketflow.utils.logging import setup_logging, get_logger
from src.pocketflow.flows.manager import flow_manager
from src.pocketflow.core.types import SharedState

def test_environment_variables():
    """Test that all required environment variables are set."""
    print("=== Environment Variables Test ===")
    
    try:
        settings = get_settings()
        
        # Check that settings loaded successfully
        print("✓ Settings loaded successfully")
        
        # Check required settings
        required_settings = [
            ("EMAIL_USERNAME", settings.EMAIL_USERNAME),
            ("EMAIL_PASSWORD", settings.EMAIL_PASSWORD),
            ("EMAIL_HOST", settings.EMAIL_HOST),
            ("EMAIL_PORT", settings.EMAIL_PORT),
            ("OPENAI_API_KEY", settings.OPENAI_API_KEY),
        ]
        
        for name, value in required_settings:
            if value:
                # Mask sensitive values
                if "PASSWORD" in name or "KEY" in name:
                    masked_value = "*" * min(len(str(value)), 20)
                    print(f"✓ {name}: {masked_value} (set)")
                else:
                    print(f"✓ {name}: {value} (set)")
            else:
                print(f"✗ {name}: Not set")
                return False
        
        print("✓ All required settings are set!")
        return True
        
    except Exception as e:
        print(f"✗ Settings test failed: {e}")
        return False

def test_imports():
    """Test that all required modules can be imported."""
    print("\n=== Import Test ===")
    
    try:
        # Test flow manager import
        print("✓ Flow manager imported successfully")
        
        # Test basic imports
        from src.pocketflow.nodes.email import FetchEmailNode, SendEmailNode
        print("✓ Email nodes imported successfully")
        
        print("✓ All imports successful")
        return True
        
    except Exception as e:
        print(f"✗ Import test failed: {e}")
        return False

def test_basic_functionality():
    """Test basic application functionality."""
    print("\n=== Basic Functionality Test ===")
    
    try:
        # Test flow manager creation
        print("✓ Flow manager created successfully")
        
        # Test shared state initialization
        shared_state = SharedState()
        print("✓ Shared state initialized")
        
        # Test available flows
        available_flows = flow_manager.get_available_flows()
        print(f"✓ Available flows: {len(available_flows)} flows found")
        
        print("✓ Basic functionality test passed")
        return True
        
    except Exception as e:
        print(f"✗ Basic functionality test failed: {e}")
        return False

def main():
    """Run all application tests."""
    print("Running PocketFlow Application Test...")
    print("=" * 50)
    
    tests = [
        test_environment_variables,
        test_imports,
        test_basic_functionality
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
        print("🎉 All tests passed! Application is ready to run.")
        print()
        print("To start the service:")
        print("  sudo systemctl start pocketflow")
        print()
        print("To check the service status:")
        print("  sudo systemctl status pocketflow")
        print()
        print("To view logs:")
        print("  sudo journalctl -u pocketflow -f")
        return True
    else:
        print("❌ Some tests failed")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 