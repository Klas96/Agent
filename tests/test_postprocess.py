#!/usr/bin/env python3
"""
Test for postprocess functionality.
"""

import os
import sys
from pathlib import Path

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from pocketflow.core.types import SharedState
from pocketflow.nodes.email.postprocess import PostProcessNode
from pocketflow.utils.logging import setup_logging, get_logger

def test_postprocess():
    """Test postprocess functionality."""
    setup_logging(level="INFO", log_format="standard")
    logger = get_logger("PostProcessTest")
    
    logger.info("=== Testing PostProcess ===")
    
    try:
        # Create shared state
        shared = SharedState()
        
        # Set up test data
        shared.email = {
            'id': '123',
            'subject': 'Test Subject',
            'from': 'test@example.com',
            'body': 'Test body',
            'date': '2025-07-26 19:00:00',
            'message_id': '<test-message-123@example.com>',
            'thread_id': 'test-thread-123',
            'in_reply_to': '<original-message-456@example.com>',
            'references': '<original-message-456@example.com> <test-message-123@example.com>'
        }
        
        shared.user = 'test@example.com'
        shared.reply_body = 'This is a test reply.'
        shared.attachment = None
        
        logger.info("Created SharedState with test data")
        
        # Create and run PostProcessNode
        postprocess_node = PostProcessNode("post_process")
        logger.info("Created PostProcessNode")
        
        # Process the node
        logger.info("Processing PostProcessNode...")
        result = postprocess_node.process(shared)
        
        logger.info(f"PostProcessNode result: {result}")
        
        return True
        
    except Exception as e:
        logger.error(f"PostProcess test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_postprocess()
    if success:
        print("✅ PostProcess test completed")
    else:
        print("❌ PostProcess test failed")
        sys.exit(1) 