"""
Production Flows Example

This example demonstrates the production-ready flows with dynamic selection.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from pocketflow import SharedState, FlowType
from pocketflow.flows.manager import flow_manager
from pocketflow.utils.logging import setup_logging, get_logger


def test_email_processor_flow():
    """Test the email processor flow."""
    logger = get_logger("EmailProcessorTest")
    
    # Create shared state with email context
    shared = SharedState(
        user="test@example.com",
        flow_type=FlowType.TOKENED_USER,
        email={
            "id": "email_1",
            "from": "user@example.com",
            "to": "assistant@example.com",
            "subject": "Help me with a task",
            "body": "Please help me organize my schedule for next week.",
            "thread_id": "thread_1"
        }
    )
    
    logger.info("=== Testing Email Processor Flow ===")
    result = flow_manager.run_flow("email_processor", shared)
    
    if result["success"]:
        logger.info("✅ Email processor flow completed successfully!")
        logger.info(f"Final state keys: {list(result.get('final_state', {}).keys())}")
    else:
        logger.error(f"❌ Email processor flow failed: {result.get('error')}")
    
    return result


def test_content_generation_flow():
    """Test the content generation flow."""
    logger = get_logger("ContentGenerationTest")
    
    # Create shared state with content generation request
    shared = SharedState(
        user="creator@example.com",
        flow_type=FlowType.TOKENED_USER,
        email={
            "id": "email_2",
            "from": "creator@example.com",
            "to": "assistant@example.com",
            "subject": "Generate a song",
            "body": "Please generate a 2-minute song in the style of Daft Punk and send it to me.",
            "thread_id": "thread_2"
        }
    )
    
    logger.info("=== Testing Content Generation Flow ===")
    result = flow_manager.run_flow("content_generation", shared)
    
    if result["success"]:
        logger.info("✅ Content generation flow completed successfully!")
        logger.info(f"Final state keys: {list(result.get('final_state', {}).keys())}")
    else:
        logger.error(f"❌ Content generation flow failed: {result.get('error')}")
    
    return result


def test_investigation_flow():
    """Test the investigation flow."""
    logger = get_logger("InvestigationTest")
    
    # Create shared state with investigation request
    shared = SharedState(
        user="researcher@example.com",
        flow_type=FlowType.TOKENED_USER,
        email={
            "id": "email_3",
            "from": "researcher@example.com",
            "to": "assistant@example.com",
            "subject": "Research request",
            "body": "Please research the latest developments in artificial intelligence and summarize your findings.",
            "thread_id": "thread_3"
        }
    )
    
    logger.info("=== Testing Investigation Flow ===")
    result = flow_manager.run_flow("investigation", shared)
    
    if result["success"]:
        logger.info("✅ Investigation flow completed successfully!")
        logger.info(f"Final state keys: {list(result.get('final_state', {}).keys())}")
    else:
        logger.error(f"❌ Investigation flow failed: {result.get('error')}")
    
    return result


def test_tokenless_user_flow():
    """Test the tokenless user flow."""
    logger = get_logger("TokenlessUserTest")
    
    # Create shared state for tokenless user
    shared = SharedState(
        user="newuser@example.com",
        flow_type=FlowType.TOKENLESS_USER,
        email={
            "id": "email_4",
            "from": "newuser@example.com",
            "to": "assistant@example.com",
            "subject": "I want to generate content",
            "body": "Please generate a song for me.",
            "thread_id": "thread_4"
        }
    )
    
    logger.info("=== Testing Tokenless User Flow ===")
    result = flow_manager.run_flow("tokenless_user", shared)
    
    if result["success"]:
        logger.info("✅ Tokenless user flow completed successfully!")
        logger.info(f"Final state keys: {list(result.get('final_state', {}).keys())}")
    else:
        logger.error(f"❌ Tokenless user flow failed: {result.get('error')}")
    
    return result


def test_payment_processing_flow():
    """Test the payment processing flow."""
    logger = get_logger("PaymentProcessingTest")
    
    # Create shared state for payment processing
    shared = SharedState(
        user="payer@example.com",
        flow_type=FlowType.PAYMENT_PENDING,
        email={
            "id": "email_5",
            "from": "payer@example.com",
            "to": "assistant@example.com",
            "subject": "Payment request",
            "body": "I want to purchase tokens.",
            "thread_id": "thread_5"
        }
    )
    
    logger.info("=== Testing Payment Processing Flow ===")
    result = flow_manager.run_flow("payment_processing", shared)
    
    if result["success"]:
        logger.info("✅ Payment processing flow completed successfully!")
        logger.info(f"Final state keys: {list(result.get('final_state', {}).keys())}")
    else:
        logger.error(f"❌ Payment processing flow failed: {result.get('error')}")
    
    return result


def test_auto_select_flow():
    """Test automatic flow selection."""
    logger = get_logger("AutoSelectTest")
    
    # Test different scenarios for auto-selection
    test_cases = [
        {
            "name": "Content Generation Request",
            "shared": SharedState(
                user="auto@example.com",
                flow_type=FlowType.TOKENED_USER,
                email={
                    "id": "auto_1",
                    "from": "auto@example.com",
                    "to": "assistant@example.com",
                    "subject": "Generate content",
                    "body": "Please generate a song for me.",
                    "thread_id": "auto_thread_1"
                }
            )
        },
        {
            "name": "Investigation Request",
            "shared": SharedState(
                user="auto@example.com",
                flow_type=FlowType.TOKENED_USER,
                email={
                    "id": "auto_2",
                    "from": "auto@example.com",
                    "to": "assistant@example.com",
                    "subject": "Research request",
                    "body": "Please research the latest AI developments.",
                    "thread_id": "auto_thread_2"
                }
            )
        },
        {
            "name": "Tokenless User",
            "shared": SharedState(
                user="newauto@example.com",
                flow_type=FlowType.TOKENLESS_USER,
                email={
                    "id": "auto_3",
                    "from": "newauto@example.com",
                    "to": "assistant@example.com",
                    "subject": "I need help",
                    "body": "Please generate content for me.",
                    "thread_id": "auto_thread_3"
                }
            )
        }
    ]
    
    logger.info("=== Testing Auto-Select Flow ===")
    
    for i, test_case in enumerate(test_cases, 1):
        logger.info(f"Test case {i}: {test_case['name']}")
        result = flow_manager.run_auto_select(test_case["shared"])
        
        if result["success"]:
            logger.info(f"✅ Auto-select completed successfully for: {test_case['name']}")
        else:
            logger.error(f"❌ Auto-select failed for {test_case['name']}: {result.get('error')}")


def test_flow_info():
    """Test getting flow information."""
    logger = get_logger("FlowInfoTest")
    
    logger.info("=== Testing Flow Information ===")
    
    # Get all available flows
    flows_info = flow_manager.get_available_flows()
    logger.info(f"Available flows: {[flow['name'] for flow in flows_info]}")
    
    # Get specific flow info
    for flow_name in ["email_processor", "content_generation", "investigation"]:
        info = flow_manager.get_flow_info(flow_name)
        if info:
            logger.info(f"Flow '{flow_name}' info: {info.get('capabilities', [])}")
        else:
            logger.warning(f"Flow '{flow_name}' info not available")


def main():
    """Run all production flow tests."""
    # Set up logging
    setup_logging(level="INFO", log_format="standard")
    logger = get_logger("ProductionFlowsExample")
    
    logger.info("🚀 Starting Production Flows Example")
    
    # Test individual flows
    test_email_processor_flow()
    test_content_generation_flow()
    test_investigation_flow()
    test_tokenless_user_flow()
    test_payment_processing_flow()
    
    # Test auto-selection
    test_auto_select_flow()
    
    # Test flow information
    test_flow_info()
    
    logger.info("✅ Production Flows Example completed!")


if __name__ == "__main__":
    main() 