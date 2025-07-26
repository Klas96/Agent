#!/usr/bin/env python3
"""
Test script for production Ollama configuration.
"""

import os
import sys
from pathlib import Path

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from pocketflow.config.settings import get_settings
from pocketflow.utils.logging import setup_logging, get_logger

def test_production_ollama():
    """Test production Ollama configuration."""
    setup_logging(level="INFO", log_format="standard")
    logger = get_logger("ProductionOllamaTest")
    
    logger.info("=== Testing Production Ollama Configuration ===")
    
    try:
        # Get settings
        settings = get_settings()
        
        logger.info("Production Ollama Configuration:")
        logger.info(f"  OLLAMA_HOST: {settings.OLLAMA_HOST}")
        logger.info(f"  OLLAMA_PORT: {settings.OLLAMA_PORT}")
        logger.info(f"  OLLAMA_MODEL: {settings.OLLAMA_MODEL}")
        logger.info(f"  LLM_PROVIDER: {settings.LLM_MODEL}")
        
        # Check if Ollama is configured for production
        if settings.OLLAMA_HOST == "192.168.1.7":
            logger.info("✅ Production Ollama configuration detected")
        else:
            logger.warning("⚠️ Not using production Ollama configuration")
        
        return True
        
    except Exception as e:
        logger.error(f"Production Ollama test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_production_ollama()
    if success:
        print("✅ Production Ollama test completed")
    else:
        print("❌ Production Ollama test failed")
        sys.exit(1) 