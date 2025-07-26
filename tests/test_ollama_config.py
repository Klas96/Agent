#!/usr/bin/env python3
"""
Test script for Ollama configuration.
"""

import os
import sys
from pathlib import Path

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from pocketflow.config.settings import get_settings, get_llm_config
from pocketflow.utils.logging import setup_logging, get_logger

def test_ollama_config():
    """Test Ollama configuration."""
    setup_logging(level="INFO", log_format="standard")
    logger = get_logger("OllamaConfigTest")
    
    logger.info("=== Testing Ollama Configuration ===")
    
    try:
        # Get settings and LLM config
        settings = get_settings()
        llm_config = get_llm_config()
        
        logger.info("Ollama Configuration:")
        logger.info(f"  OLLAMA_HOST: {settings.OLLAMA_HOST}")
        logger.info(f"  OLLAMA_PORT: {settings.OLLAMA_PORT}")
        logger.info(f"  OLLAMA_MODEL: {settings.OLLAMA_MODEL}")
        logger.info(f"  LLM_MODEL: {settings.LLM_MODEL}")
        logger.info(f"  LLM_MAX_TOKENS: {settings.LLM_MAX_TOKENS}")
        logger.info(f"  LLM_TEMPERATURE: {settings.LLM_TEMPERATURE}")
        logger.info(f"  LLM_TIMEOUT: {settings.LLM_TIMEOUT}")
        
        logger.info("LLM Config Dictionary:")
        for key, value in llm_config.items():
            logger.info(f"  {key}: {value}")
        
        # Check if Ollama is configured
        if settings.OLLAMA_HOST and settings.OLLAMA_PORT:
            logger.info("✅ Ollama configuration is set up")
        else:
            logger.warning("⚠️ Ollama configuration is incomplete")
        
        return True
        
    except Exception as e:
        logger.error(f"Ollama config test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_ollama_config()
    if success:
        print("✅ Ollama config test completed")
    else:
        print("❌ Ollama config test failed")
        sys.exit(1) 