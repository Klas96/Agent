#!/usr/bin/env python3
"""
Test script to set up and test Ollama configuration.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Set environment variables for Ollama
os.environ['OLLAMA_HOST'] = 'localhost'
os.environ['OLLAMA_PORT'] = '11434'
os.environ['OLLAMA_MODEL'] = 'llama3:latest'

try:
    # Test the LLM service directly
    from pocketflow.services.llm_service import LLMService
    
    print("=== Testing LLM Service with Ollama ===")
    
    # Create LLM service
    llm_service = LLMService()
    
    print(f"Ollama Host: {llm_service.settings.OLLAMA_HOST}")
    print(f"Ollama Port: {llm_service.settings.OLLAMA_PORT}")
    print(f"Ollama Model: {llm_service.settings.OLLAMA_MODEL}")
    
    # Test a simple message
    test_messages = [
        {"role": "user", "content": "Hello, how are you?"}
    ]
    
    print(f"\nTesting LLM call (Ollama is now the default provider)")
    
    print("✅ Using Ollama as default provider")
    try:
        response = llm_service.call_llm(test_messages)
        print(f"✅ LLM Response: {response[:100]}...")
    except Exception as e:
        print(f"❌ LLM call failed: {e}")
        print("This might be because Ollama is not running or not accessible")
        
except Exception as e:
    print(f"❌ Error testing LLM service: {e}")
    import traceback
    traceback.print_exc() 