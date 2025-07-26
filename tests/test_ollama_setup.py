#!/usr/bin/env python3
"""
Test script for Ollama setup.
"""

import os
import sys
from pathlib import Path

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from pocketflow.config.settings import get_settings
from pocketflow.utils.logging import setup_logging, get_logger

def test_ollama_setup():
    """Test Ollama setup configuration."""
    setup_logging(level="INFO", log_format="standard")
    logger = get_logger("OllamaSetupTest")
    
    logger.info("=== Testing Ollama Setup ===")
    
    try:
        # Get settings
        settings = get_settings()
        
        logger.info("Ollama Setup Configuration:")
        logger.info(f"  OLLAMA_HOST: {settings.OLLAMA_HOST}")
        logger.info(f"  OLLAMA_PORT: {settings.OLLAMA_PORT}")
        logger.info(f"  OLLAMA_MODEL: {settings.OLLAMA_MODEL}")
        logger.info(f"  LLM_MODEL: {settings.LLM_MODEL}")
        
        # Check if Ollama is properly configured
        if settings.OLLAMA_HOST and settings.OLLAMA_PORT:
            logger.info("✅ Ollama configuration is set up")
        else:
            logger.warning("⚠️ Ollama configuration is incomplete")
        
        return True
        
    except Exception as e:
        logger.error(f"Ollama setup test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_ollama_setup()
    if success:
        print("✅ Ollama setup test completed")
    else:
        print("❌ Ollama setup test failed")
        sys.exit(1) 