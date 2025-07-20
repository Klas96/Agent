"""
Token-Based Flows Example

This example demonstrates how PocketFlow handles different flows
for users with tokens vs users without tokens.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from pocketflow import create_flow, SharedState, FlowType
from pocketflow.core.node import SimpleNode
from pocketflow.core.flow import FlowRouter
from pocketflow.config.settings import get_settings, get_config
from pocketflow.utils.logging import setup_logging, get_logger
from pocketflow.nodes.user_status import (
    UserStatusCheckNode, TokenValidationNode, PaymentRequestNode,
    TokenConsumptionNode, FlowTypeRouterNode
)


class EmailFetchNode(SimpleNode):
    """Node that fetches emails."""
    
    def process(self, shared: SharedState):
        """Simulate fetching an email."""
        logger = get_logger("EmailFetchNode")
        logger.info("Fetching emails...")
        
        # Simulate email data
        email_data = {
            "id": "123",
            "from": "user@example.com",
            "subject": "Generate a song for me",
            "body": "Can you generate a happy song about coding?",
            "thread_id": "thread_1"
        }
        
        return {
            "email": email_data,
            "user": "user@example.com"
        }


class AgentNode(SimpleNode):
    """Node that processes the email with an agent."""
    
    def process(self, shared: SharedState):
        """Simulate agent processing."""
        logger = get_logger("AgentNode")
        email = shared.get("email")
        
        if not email:
            logger.warning("No email to process")
            return None
        
        logger.info(f"Processing email: {email.get('subject')}")
        
        # Simulate agent decision
        if "generate" in email.get("body", "").lower():
            return {
                "action": "generate",
                "content_type": "song",
                "prompt": "A happy song about coding"
            }
        else:
            return {
                "action": "send",
                "response": "I understand your request."
            }


class ContentGenerationNode(SimpleNode):
    """Node that generates content (only for tokened users)."""
    
    def process(self, shared: SharedState):
        """Simulate content generation."""
        logger = get_logger("ContentGenerationNode")
        
        # Check if user has tokens
        user_has_tokens = shared.get("user_has_tokens", False)
        if not user_has_tokens:
            logger.warning("User has no tokens, cannot generate content")
            return {"error": "insufficient_tokens"}
        
        action = shared.get("action")
        if action != "generate":
            return None
        
        content_type = shared.get("content_type")
        prompt = shared.get("prompt")
        
        logger.info(f"Generating {content_type}: {prompt}")
        
        # Simulate file generation
        file_path = f"generated/song_{shared.get('email', {}).get('id', 'unknown')}.mp3"
        
        return {
            "generated_file_path": file_path,
            "content_type": content_type
        }


class EmailSendNode(SimpleNode):
    """Node that sends emails."""
    
    def process(self, shared: SharedState):
        """Simulate sending an email."""
        logger = get_logger("EmailSendNode")
        action = shared.get("action")
        
        if action == "send":
            response = shared.get("response", "Default response")
            logger.info(f"Sending email response: {response}")
            return {"email_sent": True}
        
        elif action == "generate" and shared.get("generated_file_path"):
            file_path = shared.get("generated_file_path")
            logger.info(f"Sending email with attachment: {file_path}")
            return {"email_sent": True, "attachment_sent": file_path}
        
        return None


class PaymentResponseNode(SimpleNode):
    """Node that sends payment instructions to tokenless users."""
    
    def process(self, shared: SharedState):
        """Send payment instructions."""
        logger = get_logger("PaymentResponseNode")
        
        payment_request = shared.get("payment_request")
        if not payment_request:
            logger.warning("No payment request found")
            return None
        
        amount = payment_request.get("amount_usd")
        btc_address = payment_request.get("btc_address")
        
        response = f"""
        To proceed with your request, please send ${amount} to:
        {btc_address}
        
        Once payment is confirmed, you'll be able to use our services.
        """
        
        logger.info(f"Sending payment instructions for ${amount}")
        
        return {
            "email_sent": True,
            "payment_instructions_sent": True,
            "response": response
        }


def create_tokened_user_flow():
    """Create flow for users with tokens."""
    return (create_flow("tokened_user_flow", FlowType.TOKENED_USER, requires_tokens=True)
            .add_step("fetch", EmailFetchNode("fetch"))
            .add_step("status_check", UserStatusCheckNode("status_check"))
            .add_step("agent", AgentNode("agent"))
            .add_step("token_validation", TokenValidationNode("token_validation"))
            .add_step("generate", ContentGenerationNode("generate"))
            .add_step("consume_tokens", TokenConsumptionNode("consume_tokens"))
            .add_step("send", EmailSendNode("send"))
            .set_start("fetch")
            .add_end_step("send")
            .add_routing("fetch", "default", "status_check")
            .add_routing("status_check", "default", "agent")
            .add_routing("agent", "default", "token_validation")
            .add_routing("token_validation", "approved", "generate")
            .add_routing("token_validation", "insufficient", "send")
            .add_routing("generate", "default", "consume_tokens")
            .add_routing("consume_tokens", "default", "send")
            .build())


def create_tokenless_user_flow():
    """Create flow for users without tokens."""
    return (create_flow("tokenless_user_flow", FlowType.TOKENLESS_USER, requires_tokens=False)
            .add_step("fetch", EmailFetchNode("fetch"))
            .add_step("status_check", UserStatusCheckNode("status_check"))
            .add_step("agent", AgentNode("agent"))
            .add_step("payment_request", PaymentRequestNode("payment_request"))
            .add_step("payment_response", PaymentResponseNode("payment_response"))
            .set_start("fetch")
            .add_end_step("payment_response")
            .add_routing("fetch", "default", "status_check")
            .add_routing("status_check", "default", "agent")
            .add_routing("agent", "default", "payment_request")
            .add_routing("payment_request", "default", "payment_response")
            .build())


def main():
    """Run the token-based flows example."""
    # Set up logging
    setup_logging(level="INFO", log_format="standard")
    logger = get_logger("TokenBasedFlows")
    
    # Create flows
    tokened_flow = create_tokened_user_flow()
    tokenless_flow = create_tokenless_user_flow()
    
    # Create flow router
    router = FlowRouter()
    router.register_flow(tokened_flow)
    router.register_flow(tokenless_flow)
    
    # Test scenarios
    test_scenarios = [
        {
            "name": "User with tokens",
            "user_email": "rich_user@example.com",
            "expected_flow": "tokened_user_flow"
        },
        {
            "name": "User without tokens",
            "user_email": "poor_user@example.com",
            "expected_flow": "tokenless_user_flow"
        }
    ]
    
    for scenario in test_scenarios:
        logger.info(f"\n=== Testing: {scenario['name']} ===")
        
        # Create shared state
        shared = SharedState(user=scenario["user_email"])
        
        # Run the appropriate flow
        result = router.run_appropriate_flow(shared)
        
        if result.success:
            logger.info(f"✅ {scenario['name']} completed successfully!")
            logger.info(f"Flow type: {shared.get('flow_type')}")
            logger.info(f"User has tokens: {shared.get('user_has_tokens')}")
            logger.info(f"Tokens remaining: {shared.get('tokens_remaining')}")
        else:
            logger.error(f"❌ {scenario['name']} failed: {result.error}")


if __name__ == "__main__":
    main() 