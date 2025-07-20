"""
Basic Flow Example

This example demonstrates how to use the new PocketFlow architecture
to create a simple email processing flow.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from pocketflow import create_flow, SharedState
from pocketflow.core.node import SimpleNode
from pocketflow.config.settings import get_settings, get_config
from pocketflow.utils.logging import setup_logging, get_logger


class EmailFetchNode(SimpleNode):
    """Example node that fetches emails."""
    
    def process(self, shared: SharedState):
        """Simulate fetching an email."""
        logger = get_logger("EmailFetchNode")
        logger.info("Fetching emails...")
        
        # Simulate email data
        email_data = {
            "id": "123",
            "from": "user@example.com",
            "subject": "Test email",
            "body": "Hello, can you generate a song for me?",
            "thread_id": "thread_1"
        }
        
        return {
            "email": email_data,
            "user": "user@example.com"
        }


class AgentNode(SimpleNode):
    """Example node that processes the email with an agent."""
    
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
    """Example node that generates content."""
    
    def process(self, shared: SharedState):
        """Simulate content generation."""
        logger = get_logger("ContentGenerationNode")
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
    """Example node that sends emails."""
    
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


def main():
    """Run the example flow."""
    # Set up logging
    setup_logging(level="INFO", log_format="standard")
    logger = get_logger("Example")
    
    # Load configuration
    try:
        settings = get_settings()
        config = get_config("development")
        logger.info(f"Loaded configuration for environment: {config.environment}")
    except Exception as e:
        logger.error(f"Failed to load configuration: {e}")
        return
    
    # Create nodes
    fetch_node = EmailFetchNode("fetch")
    agent_node = AgentNode("agent")
    generate_node = ContentGenerationNode("generate")
    send_node = EmailSendNode("send")
    
    # Create flow
    flow = (create_flow("email_processor")
            .add_step("fetch", fetch_node)
            .add_step("agent", agent_node)
            .add_step("generate", generate_node)
            .add_step("send", send_node)
            .set_start("fetch")
            .add_end_step("send")
            .add_routing("fetch", "default", "agent")
            .add_routing("agent", "generate", "generate")
            .add_routing("agent", "send", "send")
            .add_routing("generate", "default", "send")
            .build())
    
    # Create shared state
    shared = SharedState()
    
    # Run the flow
    logger.info("Starting flow execution...")
    result = flow.run(shared)
    
    if result.success:
        logger.info("Flow completed successfully!")
        logger.info(f"Final state: {shared}")
    else:
        logger.error(f"Flow failed: {result.error}")


if __name__ == "__main__":
    main() 