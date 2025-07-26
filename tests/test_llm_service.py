#!/usr/bin/env python3
"""
Test script for LLM service.
"""

import os
import sys
from pathlib import Path

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from pocketflow.services.llm_service import LLMService
from pocketflow.utils.logging import setup_logging, get_logger

def test_llm_service():
    """Test LLM service functionality."""
    setup_logging(level="INFO", log_format="standard")
    logger = get_logger("LLMServiceTest")
    
    logger.info("=== Testing LLM Service ===")
    
    try:
        # Create LLM service
        llm_service = LLMService()
        logger.info("LLMService created successfully")
        
        # Test simple prompt
        prompt = "What is 2 + 2?"
        logger.info(f"Testing with prompt: {prompt}")
        
        response = llm_service.call_llm([{"role": "user", "content": prompt}])
        logger.info(f"LLM response: {response}")
        
        return True
        
    except Exception as e:
        logger.error(f"LLM service test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_llm_service()
    if success:
        print("✅ LLM service test completed")
    else:
        print("❌ LLM service test failed")
        sys.exit(1) 