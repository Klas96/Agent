#!/usr/bin/env python3
"""
Test to check if send_email step is being executed in the flow.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from pocketflow.core.types import SharedState
from pocketflow.flows.email_processor import EmailProcessorFlow
from pocketflow.utils.logging import get_logger

logger = get_logger("SendEmailFlowTest")

def test_send_email_in_flow():
    """Test if send_email step is executed in the flow."""
    logger.info("=== Testing send_email step in flow ===")
    
    # Create a mock email and agent action
    email = {
        'id': 'test_609',
        'subject': 'Test Subject',
        'from': 'Klas Holmgren <klas0holmgren@gmail.com>',
        'body': 'Test email body',
        'date': '2025-07-26 19:23:49',
        'message_id': 'test_609',
        'thread_id': 'test_thread_123'
    }
    
    agent_action = {
        'action': 'send',
        'parameters': {
            'to': 'klas0holmgren@gmail.com',
            'body': 'This is a test response from the agent.',
            'attachment': ''
        }
    }
    
    # Create shared state
    shared = SharedState()
    shared.email = email
    shared.agent_action = agent_action
    shared.user = None
    shared.conversation = []
    shared.conversations = {}
    
    logger.info("Created SharedState with test data")
    logger.info(f"Email: {email}")
    logger.info(f"Agent action: {agent_action}")
    
    # Create and run the flow
    flow = EmailProcessorFlow()
    logger.info("Created EmailProcessorFlow")
    
    try:
        logger.info("Running email processor flow...")
        result = flow.run(shared)
        logger.info(f"Flow result: {result}")
        
        if result.get('success'):
            logger.info("✅ Flow completed successfully!")
        else:
            logger.error(f"❌ Flow failed: {result.get('error')}")
            
    except Exception as e:
        logger.error(f"❌ Exception during flow execution: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_send_email_in_flow() 