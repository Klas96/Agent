#!/usr/bin/env python3
"""
Test script to manually trigger email processing.
"""

import os
import sys
from pathlib import Path

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from pocketflow.core.types import SharedState
from pocketflow.flows.manager import flow_manager
from pocketflow.utils.logging import setup_logging, get_logger

def test_manual_email_processing():
    """Manually trigger email processing to see what happens."""
    setup_logging(level="INFO", log_format="standard")
    logger = get_logger("ManualEmailTest")
    
    logger.info("=== Manual Email Processing Test ===")
    
    try:
        # Create shared state
        shared = SharedState()
        logger.info("Created SharedState")
        
        # Run the flow manager
        logger.info("Running flow manager...")
        result = flow_manager.run_auto_select(shared)
        
        logger.info(f"Flow result: {result}")
        
        # Check what's in the shared state
        logger.info("Shared state contents:")
        for key, value in shared.__dict__.items():
            if key.startswith('_'):
                continue
            logger.info(f"  {key}: {value}")
        
        return True
        
    except Exception as e:
        logger.error(f"Manual email processing failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_manual_email_processing()
    if success:
        print("✅ Manual email processing test completed")
    else:
        print("❌ Manual email processing test failed")
        sys.exit(1) 