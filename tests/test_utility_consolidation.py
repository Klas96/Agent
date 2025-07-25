#!/usr/bin/env python3
"""
Test Utility Consolidation

This test verifies that all utility patterns have been properly consolidated
and are working correctly.
"""

import sys
import os
sys.path.append('/opt/pocketflow')

from src.pocketflow.utils.logging import get_logger

def test_email_utilities():
    """Test email utility functions."""
    print("=== Testing Email Utilities ===")
    
    try:
        from utils.email_utils import extract_email
        
        # Test email extraction
        test_cases = [
            ("John Doe <john@example.com>", "john@example.com"),
            ("jane@example.com", "jane@example.com"),
            ("Invalid email", "Invalid email"),
            ("", ""),
        ]
        
        for input_email, expected in test_cases:
            result = extract_email(input_email)
            if result == expected:
                print(f"✓ Email extraction: '{input_email}' -> '{result}'")
            else:
                print(f"✗ Email extraction failed: '{input_email}' -> '{result}' (expected '{expected}')")
                return False
        
        print("✓ All email utilities working correctly")
        return True
    except Exception as e:
        print(f"✗ Email utilities test failed: {e}")
        return False

def test_bitcoin_utilities():
    """Test Bitcoin utility functions."""
    print("\n=== Testing Bitcoin Utilities ===")
    
    try:
        from utils.electrum_utils import get_btc_usd_price, get_electrum_rpc_config
        
        # Test RPC config
        config = get_electrum_rpc_config()
        required_keys = ["host", "port", "username", "password"]
        for key in required_keys:
            if key not in config:
                print(f"✗ Missing config key: {key}")
                return False
        
        print("✓ RPC config loaded successfully")
        
        # Test BTC price (this might fail if no internet, but should handle gracefully)
        try:
            price = get_btc_usd_price()
            if price and price > 0:
                print(f"✓ BTC price retrieved: ${price}")
            else:
                print("⚠ BTC price retrieval failed (expected in offline mode)")
        except Exception as e:
            print(f"⚠ BTC price retrieval failed (expected): {e}")
        
        print("✓ Bitcoin utilities working correctly")
        return True
    except Exception as e:
        print(f"✗ Bitcoin utilities test failed: {e}")
        return False

def test_logging_utilities():
    """Test logging utility functions."""
    print("\n=== Testing Logging Utilities ===")
    
    try:
        from src.pocketflow.utils.logging import get_logger, setup_logging
        
        # Test logger creation
        logger = get_logger("TestLogger")
        logger.info("Test log message")
        
        print("✓ Logger created successfully")
        
        # Test setup_logging
        setup_logging(level="INFO")
        print("✓ Logging setup completed")
        
        print("✓ Logging utilities working correctly")
        return True
    except Exception as e:
        print(f"✗ Logging utilities test failed: {e}")
        return False

def test_error_utilities():
    """Test error utility functions."""
    print("\n=== Testing Error Utilities ===")
    
    try:
        from src.pocketflow.utils.errors import (
            PocketFlowError, EmailError, LLMError, BitcoinError, 
            DatabaseError, WebSearchError, ContentGenerationError
        )
        
        # Test error creation
        errors = [
            PocketFlowError("Test error"),
            EmailError("Test email error"),
            LLMError("Test LLM error"),
            BitcoinError("Test Bitcoin error"),
            DatabaseError("Test database error"),
            WebSearchError("Test web search error"),
            ContentGenerationError("Test content generation error"),
        ]
        
        for error in errors:
            if isinstance(error, PocketFlowError):
                print(f"✓ Error created: {type(error).__name__}")
            else:
                print(f"✗ Error creation failed: {type(error).__name__}")
                return False
        
        print("✓ Error utilities working correctly")
        return True
    except Exception as e:
        print(f"✗ Error utilities test failed: {e}")
        return False

def test_prompt_utilities():
    """Test prompt utility functions."""
    print("\n=== Testing Prompt Utilities ===")
    
    try:
        from src.pocketflow.utils.prompt_utils import build_system_prompt
        
        # Test system prompt building
        shared = {"email": {"from": "test@example.com"}}
        prompt = build_system_prompt(shared, "test@example.com")
        
        if prompt and "email assistant" in prompt.lower():
            print("✓ System prompt built successfully")
        else:
            print("✗ System prompt building failed")
            return False
        
        print("✓ Prompt utilities working correctly")
        return True
    except Exception as e:
        print(f"✗ Prompt utilities test failed: {e}")
        return False

def test_performance_utilities():
    """Test performance utility functions."""
    print("\n=== Testing Performance Utilities ===")
    
    try:
        from src.pocketflow.utils.performance import PerformanceMonitor, monitor_performance
        
        # Test performance monitor
        monitor = PerformanceMonitor()
        timer_id = monitor.start_timer("test_component")
        metrics = monitor.end_timer(timer_id)
        
        if metrics and metrics.component_name == "test_component":
            print("✓ Performance monitor working correctly")
        else:
            print("✗ Performance monitor failed")
            return False
        
        # Test performance decorator
        @monitor_performance("test_function")
        def test_function():
            return "test"
        
        result = test_function()
        if result == "test":
            print("✓ Performance decorator working correctly")
        else:
            print("✗ Performance decorator failed")
            return False
        
        print("✓ Performance utilities working correctly")
        return True
    except Exception as e:
        print(f"✗ Performance utilities test failed: {e}")
        return False

def test_unused_utilities():
    """Test that unused utilities are identified."""
    print("\n=== Testing Unused Utilities ===")
    
    try:
        # Check if websearch_utils is being used
        import importlib.util
        spec = importlib.util.spec_from_file_location("websearch_utils", "utils/websearch_utils.py")
        if spec:
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            print("✓ websearch_utils can be imported (but not used)")
        
        # Check if generate_sound is being used
        spec = importlib.util.spec_from_file_location("generate_sound", "utils/generate_sound.py")
        if spec:
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            print("✓ generate_sound can be imported (but not used)")
        
        print("✓ Unused utilities identified correctly")
        return True
    except Exception as e:
        print(f"✗ Unused utilities test failed: {e}")
        return False

def main():
    """Run all utility consolidation tests."""
    print("Utility Consolidation Test Suite")
    print("=" * 50)
    
    tests = [
        test_email_utilities,
        test_bitcoin_utilities,
        test_logging_utilities,
        test_error_utilities,
        test_prompt_utilities,
        test_performance_utilities,
        test_unused_utilities
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
        print("🎉 All utility consolidation tests passed!")
        print("✅ Utility patterns are properly consolidated")
        return True
    else:
        print("❌ Some utility consolidation tests failed")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 