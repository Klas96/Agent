#!/usr/bin/env python3
"""
Simple test script to verify Ollama configuration without importing the full package.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    # Import only the settings module
    from pocketflow.config.settings import get_settings, get_llm_config
    
    print("=== Testing Consolidated Ollama Configuration ===")
    settings = get_settings()
    llm_config = get_llm_config()
    
    print(f"LLM Provider: {settings.LLM_PROVIDER}")
    print(f"Ollama Host: {settings.OLLAMA_HOST}")
    print(f"Ollama Port: {settings.OLLAMA_PORT}")
    print(f"Ollama Model: {settings.OLLAMA_MODEL}")
    print(f"LLM Model: {settings.LLM_MODEL}")
    print(f"LLM Max Tokens: {settings.LLM_MAX_TOKENS}")
    print(f"LLM Temperature: {settings.LLM_TEMPERATURE}")
    print(f"LLM Timeout: {settings.LLM_TIMEOUT}")
    
    print("\nLLM Config Dictionary:")
    for key, value in llm_config.items():
        print(f"  {key}: {value}")
    
    if settings.LLM_PROVIDER == "ollama":
        print("\n✅ Configuration set to use Ollama as primary provider")
    else:
        print(f"\n⚠️ Configuration using {settings.LLM_PROVIDER}, set LLM_PROVIDER=ollama to use Ollama")
        
except Exception as e:
    print(f"❌ Error testing configuration: {e}")
    import traceback
    traceback.print_exc() 