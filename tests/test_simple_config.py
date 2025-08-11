#!/usr/bin/env python3
"""
Test script for simple configuration.
"""

import os
import sys
from pathlib import Path

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from pocketflow.config.settings import get_settings
from pocketflow.utils.logging import setup_logging, get_logger

def test_simple_config():
    """Test simple configuration loading."""
    setup_logging(level="INFO", log_format="standard")
    logger = get_logger("SimpleConfigTest")
    
    logger.info("=== Testing Simple Configuration ===")
    
    try:
        # Get settings
        settings = get_settings()
        
        logger.info("Simple Configuration:")
        logger.info(f"  ENVIRONMENT: {settings.ENVIRONMENT}")
        logger.info(f"  DEBUG: {settings.DEBUG}")
        logger.info(f"  LOG_LEVEL: {settings.LOG_LEVEL}")
        
        # Check if basic configuration is loaded
        if settings.ENVIRONMENT:
            logger.info("✅ Basic configuration is loaded")
        else:
            logger.warning("⚠️ Basic configuration is not loaded")
        
        return True
        
    except Exception as e:
        logger.error(f"Simple config test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_simple_config()
    if success:
        print("✅ Simple config test completed")
    else:
        print("❌ Simple config test failed")
        sys.exit(1) 