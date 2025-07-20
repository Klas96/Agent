"""
Refactored Nodes Example

This example demonstrates the refactored nodes with service integration.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from pocketflow import create_flow, SharedState, FlowType
from pocketflow.core.flow import FlowRouter
from pocketflow.config.settings import get_settings, get_config
from pocketflow.utils.logging import setup_logging, get_logger
from pocketflow.nodes import (
    FetchEmailNode, SendEmailNode, ConversationContextNode,
    AgentNode, PopAgentActionNode,
    ContentCreatorNode, ContentParamNode, GenerateContentNode,
    InvestigateTopicNode,
    PurchaseTokensWithBitcoinNode
)


def create_email_processing_flow():
    """Create a flow that demonstrates email processing with refactored nodes."""
    return (create_flow("email_processing_flow", FlowType.TOKENED_USER, requires_tokens=True)
            .add_step("fetch_email", FetchEmailNode("fetch_email"))
            .add_step("conversation_context", ConversationContextNode("conversation_context"))
            .add_step("agent", AgentNode("agent"))
            .add_step("pop_action", PopAgentActionNode("pop_action"))
            .add_step("content_creator", ContentCreatorNode("content_creator"))
            .add_step("content_params", ContentParamNode("content_params"))
            .add_step("generate_content", GenerateContentNode("generate_content"))
            .add_step("investigate", InvestigateTopicNode("investigate"))
            .add_step("send_email", SendEmailNode("send_email"))
            .set_start("fetch_email")
            .add_end_step("send_email")
            .add_routing("fetch_email", "no_email", "finish")
            .add_routing("fetch_email", "default", "conversation_context")
            .add_routing("conversation_context", "no_context", "finish")
            .add_routing("conversation_context", "default", "agent")
            .add_routing("agent", "finish", "finish")
            .add_routing("agent", "default", "pop_action")
            .add_routing("pop_action", "finish", "finish")
            .add_routing("pop_action", "generate", "content_creator")
            .add_routing("pop_action", "investigate", "investigate")
            .add_routing("pop_action", "send", "send_email")
            .add_routing("content_creator", "default", "content_params")
            .add_routing("content_params", "default", "generate_content")
            .add_routing("generate_content", "generation_failed", "finish")
            .add_routing("generate_content", "default", "pop_action")
            .add_routing("investigate", "default", "pop_action")
            .add_routing("send_email", "send_failed", "finish")
            .add_routing("send_email", "default", "pop_action")
            .build())


def create_tokenless_user_flow():
    """Create a flow for users without tokens."""
    return (create_flow("tokenless_user_flow", FlowType.TOKENLESS_USER, requires_tokens=False)
            .add_step("fetch_email", FetchEmailNode("fetch_email"))
            .add_step("conversation_context", ConversationContextNode("conversation_context"))
            .add_step("agent", AgentNode("agent"))
            .add_step("pop_action", PopAgentActionNode("pop_action"))
            .add_step("payment_request", PurchaseTokensWithBitcoinNode("payment_request"))
            .add_step("send_email", SendEmailNode("send_email"))
            .set_start("fetch_email")
            .add_end_step("send_email")
            .add_routing("fetch_email", "no_email", "finish")
            .add_routing("fetch_email", "default", "conversation_context")
            .add_routing("conversation_context", "no_context", "finish")
            .add_routing("conversation_context", "default", "agent")
            .add_routing("agent", "finish", "finish")
            .add_routing("agent", "default", "pop_action")
            .add_routing("pop_action", "finish", "finish")
            .add_routing("pop_action", "generate", "payment_request")
            .add_routing("pop_action", "investigate", "payment_request")
            .add_routing("pop_action", "send", "send_email")
            .add_routing("payment_request", "send", "send_email")
            .add_routing("send_email", "send_failed", "finish")
            .add_routing("send_email", "default", "finish")
            .build())


def main():
    """Run the refactored nodes example."""
    # Set up logging
    setup_logging(level="INFO", log_format="standard")
    logger = get_logger("RefactoredNodesExample")
    
    # Create flows
    email_flow = create_email_processing_flow()
    tokenless_flow = create_tokenless_user_flow()
    
    # Create shared state with mock email
    shared = SharedState(
        user="test@example.com",
        email={
            "id": "test_email_1",
            "from": "user@example.com",
            "to": "assistant@example.com",
            "subject": "Generate a song for me",
            "body": "Please generate a 2-minute song in the style of Daft Punk and send it to me.",
            "thread_id": "thread_1"
        }
    )
    
    # Test email processing flow
    logger.info("=== Testing Email Processing Flow ===")
    result = email_flow.run(shared)
    
    if result.success:
        logger.info("✅ Email processing flow completed successfully!")
        logger.info(f"Final state: {shared}")
    else:
        logger.error(f"❌ Email processing flow failed: {result.error}")
    
    # Test tokenless user flow
    logger.info("\n=== Testing Tokenless User Flow ===")
    tokenless_shared = SharedState(
        user="tokenless@example.com",
        email={
            "id": "test_email_2",
            "from": "tokenless@example.com",
            "to": "assistant@example.com",
            "subject": "I want to generate content",
            "body": "Please generate a song for me.",
            "thread_id": "thread_2"
        }
    )
    
    result = tokenless_flow.run(tokenless_shared)
    
    if result.success:
        logger.info("✅ Tokenless user flow completed successfully!")
        logger.info(f"Final state: {tokenless_shared}")
    else:
        logger.error(f"❌ Tokenless user flow failed: {result.error}")


if __name__ == "__main__":
    main() 