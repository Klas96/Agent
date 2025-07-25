#!/usr/bin/env python3
"""
Test script to verify Ollama configuration in production.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    # Test the LLM service directly
    from pocketflow.services.llm_service import LLMService
    
    print("=== Testing Production Ollama Configuration ===")
    
    # Create LLM service
    llm_service = LLMService()
    
    print(f"Ollama Host: {llm_service.settings.OLLAMA_HOST}")
    print(f"Ollama Port: {llm_service.settings.OLLAMA_PORT}")
    print(f"Ollama Model: {llm_service.settings.OLLAMA_MODEL}")
    
    # Test a simple message
    test_messages = [
        {"role": "user", "content": "Test message for production deployment"}
    ]
    
    print(f"\nTesting LLM call in production environment")
    
    try:
        response = llm_service.call_llm(test_messages)
        print(f"✅ Production LLM Response: {response[:100]}...")
        print("✅ Ollama is working correctly in production!")
    except Exception as e:
        print(f"❌ Production LLM call failed: {e}")
        
except Exception as e:
    print(f"❌ Error testing production configuration: {e}")
    import traceback
    traceback.print_exc() 