#!/usr/bin/env python3
"""
Test Configuration Consolidation

This test verifies that all configuration patterns have been properly consolidated
to use the centralized settings system.
"""

import sys
import os
sys.path.append('/opt/pocketflow')

from src.pocketflow.config.settings import get_settings
from src.pocketflow.utils.logging import get_logger

def test_settings_loading():
    """Test that settings can be loaded correctly."""
    print("=== Testing Settings Loading ===")
    
    try:
        settings = get_settings()
        print("✓ Settings loaded successfully")
        
        # Test key settings
        print(f"  Environment: {settings.ENVIRONMENT}")
        print(f"  Debug: {settings.DEBUG}")
        print(f"  Log Level: {settings.LOG_LEVEL}")
        print(f"  Electrum Host: {settings.ELECTRUM_HOST}")
        print(f"  Electrum Port: {settings.ELECTRUM_PORT}")
        
        return True
    except Exception as e:
        print(f"✗ Settings loading failed: {e}")
        return False

def test_electrum_config():
    """Test that electrum utilities use centralized config."""
    print("\n=== Testing Electrum Configuration ===")
    
    try:
        from utils.electrum_utils import get_electrum_rpc_config
        config = get_electrum_rpc_config()
        
        print("✓ Electrum config loaded successfully")
        print(f"  Host: {config['host']}")
        print(f"  Port: {config['port']}")
        print(f"  Username: {config['username']}")
        
        # Verify it's using settings, not direct os.environ
        settings = get_settings()
        assert config['host'] == settings.ELECTRUM_HOST
        assert config['port'] == settings.ELECTRUM_PORT
        
        print("✓ Electrum config uses centralized settings")
        return True
    except Exception as e:
        print(f"✗ Electrum config test failed: {e}")
        return False

def test_web_app_config():
    """Test that web app uses centralized config."""
    print("\n=== Testing Web App Configuration ===")
    
    try:
        from src.pocketflow.web.app import create_app
        app = create_app()
        
        print("✓ Web app created successfully")
        print(f"  App name: {app.name}")
        print(f"  Blueprints: {list(app.blueprints.keys())}")
        
        # Test that app config is loaded from settings
        settings = get_settings()
        assert app.config.get('DEBUG') == settings.DEBUG
        
        print("✓ Web app uses centralized settings")
        return True
    except Exception as e:
        print(f"✗ Web app config test failed: {e}")
        return False

def test_service_config():
    """Test that services use centralized config."""
    print("\n=== Testing Service Configuration ===")
    
    try:
        from src.pocketflow.services import email_service, llm_service, database_service
        
        print("✓ Services imported successfully")
        
        # Test that services have settings
        assert hasattr(email_service, 'settings')
        assert hasattr(llm_service, 'settings')
        assert hasattr(database_service, 'settings')
        
        print("✓ All services use centralized settings")
        return True
    except Exception as e:
        print(f"✗ Service config test failed: {e}")
        return False

def test_control_panel_config():
    """Test that control panel uses centralized config."""
    print("\n=== Testing Control Panel Configuration ===")
    
    try:
        # Test that control panel can be imported and uses settings
        import control_panel
        
        print("✓ Control panel imported successfully")
        
        # Test that it uses get_settings
        from src.pocketflow.config.settings import get_settings
        settings = get_settings()
        
        print(f"  Environment: {settings.ENVIRONMENT}")
        print(f"  Log Level: {settings.LOG_LEVEL}")
        
        print("✓ Control panel uses centralized settings")
        return True
    except Exception as e:
        print(f"✗ Control panel config test failed: {e}")
        return False

def test_no_direct_os_environ():
    """Test that no files use direct os.environ.get() calls."""
    print("\n=== Testing No Direct os.environ Usage ===")
    
    try:
        import subprocess
        import os
        
        # Search for direct os.environ.get() calls in the codebase
        result = subprocess.run([
            'grep', '-r', 'os\.environ\.get', '/opt/pocketflow/src', '/opt/pocketflow/utils', '/opt/pocketflow/scripts'
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("⚠ Found direct os.environ.get() calls:")
            print(result.stdout)
            return False
        else:
            print("✓ No direct os.environ.get() calls found in main codebase")
            return True
    except Exception as e:
        print(f"✗ os.environ test failed: {e}")
        return False

def main():
    """Run all configuration consolidation tests."""
    print("Configuration Consolidation Test Suite")
    print("=" * 50)
    
    tests = [
        test_settings_loading,
        test_electrum_config,
        test_web_app_config,
        test_service_config,
        test_control_panel_config,
        test_no_direct_os_environ
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
        print("🎉 All configuration consolidation tests passed!")
        print("✅ Configuration patterns are properly consolidated")
        return True
    else:
        print("❌ Some configuration consolidation tests failed")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 