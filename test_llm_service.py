#!/usr/bin/env python3
"""
Test script to verify LLM service with Ollama configuration.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    # Test the LLM service directly
    from pocketflow.services.llm_service import LLMService
    
    print("=== Testing LLM Service with Ollama ===")
    
    # Create LLM service
    llm_service = LLMService()
    
    print(f"LLM Provider: {llm_service.settings.LLM_PROVIDER}")
    print(f"Ollama Host: {llm_service.settings.OLLAMA_HOST}")
    print(f"Ollama Port: {llm_service.settings.OLLAMA_PORT}")
    print(f"Ollama Model: {llm_service.settings.OLLAMA_MODEL}")
    
    # Test a simple message
    test_messages = [
        {"role": "user", "content": "Hello, how are you?"}
    ]
    
    print(f"\nTesting LLM call with provider: {llm_service.settings.LLM_PROVIDER}")
    
    if llm_service.settings.LLM_PROVIDER == "ollama":
        print("✅ Using Ollama as primary provider")
        try:
            response = llm_service.call_llm(test_messages)
            print(f"✅ LLM Response: {response[:100]}...")
        except Exception as e:
            print(f"❌ LLM call failed: {e}")
    else:
        print(f"⚠️ Using {llm_service.settings.LLM_PROVIDER} instead of Ollama")
        print("Set LLM_PROVIDER=ollama to use Ollama")
        
except Exception as e:
    print(f"❌ Error testing LLM service: {e}")
    import traceback
    traceback.print_exc() 