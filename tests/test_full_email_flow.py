#!/usr/bin/env python3
"""
Test script to run the complete email flow including sending.
"""

import os
import sys
from pathlib import Path

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from pocketflow.core.types import SharedState
from pocketflow.flows.email_processor import email_processor_flow
from pocketflow.utils.logging import setup_logging, get_logger

def test_full_email_flow():
    """Run the complete email processing flow including sending."""
    setup_logging(level="INFO", log_format="standard")
    logger = get_logger("FullEmailFlowTest")
    
    logger.info("=== Full Email Flow Test ===")
    
    try:
        # Create shared state
        shared = SharedState()
        logger.info("Created SharedState")
        
        # Run the complete email processor flow
        logger.info("Running complete email processor flow...")
        result = email_processor_flow.run(shared)
        
        logger.info(f"Flow result: {result}")
        
        # Check what's in the shared state
        logger.info("Shared state contents:")
        for key, value in shared.__dict__.items():
            if key.startswith('_'):
                continue
            logger.info(f"  {key}: {value}")
        
        return True
        
    except Exception as e:
        logger.error(f"Full email flow failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_full_email_flow()
    if success:
        print("✅ Full email flow test completed")
    else:
        print("❌ Full email flow test failed")
        sys.exit(1) 