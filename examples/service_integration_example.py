"""
Service Integration Example

This example demonstrates how the service layer integrates with
the flow architecture in PocketFlow.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from pocketflow import create_flow, SharedState, FlowType
from pocketflow.core.node import SimpleNode
from pocketflow.core.flow import FlowRouter
from pocketflow.config.settings import get_settings, get_config
from pocketflow.utils.logging import setup_logging, get_logger
from pocketflow.services import (
    email_service, llm_service, content_service, 
    bitcoin_service, websearch_service
)
from pocketflow.core.types import (
    EmailSendRequest, ContentGenerationRequest, 
    InvestigationRequest, PaymentRequest
)


class ServiceIntegrationNode(SimpleNode):
    """Node that demonstrates service integration."""
    
    def process(self, shared: SharedState):
        """Demonstrate service integration."""
        logger = get_logger("ServiceIntegrationNode")
        
        # Get user email from shared state
        user_email = shared.get("user", "test@example.com")
        
        logger.info(f"Demonstrating service integration for user: {user_email}")
        
        # 1. Email Service Demo
        logger.info("=== Email Service Demo ===")
        try:
            # Simulate fetching emails
            emails = email_service.fetch_unread_emails()
            logger.info(f"Fetched {len(emails)} emails")
            
            # Simulate sending email
            send_request = EmailSendRequest(
                to=user_email,
                subject="Service Integration Test",
                body="This is a test email from PocketFlow services."
            )
            success = email_service.send_email(send_request)
            logger.info(f"Email sent successfully: {success}")
            
        except Exception as e:
            logger.error(f"Email service error: {e}")
        
        # 2. LLM Service Demo
        logger.info("=== LLM Service Demo ===")
        try:
            messages = [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Generate a short song about coding."}
            ]
            
            response = llm_service.call_llm(messages)
            logger.info(f"LLM response: {response[:100]}...")
            
            actions = llm_service.extract_actions(response)
            logger.info(f"Extracted {len(actions)} actions")
            
        except Exception as e:
            logger.error(f"LLM service error: {e}")
        
        # 3. Content Service Demo
        logger.info("=== Content Service Demo ===")
        try:
            content_request = ContentGenerationRequest(
                content_type="sound",
                prompt="A happy coding song",
                duration=30
            )
            
            file_path = content_service.generate_content(content_request)
            if file_path:
                logger.info(f"Content generated: {file_path}")
                
                # Get content info
                info = content_service.get_content_info(file_path)
                logger.info(f"Content info: {info}")
            else:
                logger.warning("Content generation failed")
                
        except Exception as e:
            logger.error(f"Content service error: {e}")
        
        # 4. Bitcoin Service Demo
        logger.info("=== Bitcoin Service Demo ===")
        try:
            # Get or create Bitcoin address
            address = bitcoin_service.get_or_create_address(user_email)
            logger.info(f"Bitcoin address: {address}")
            
            # Create payment request
            payment_request = PaymentRequest(
                amount_usd=0.10,
                user_email=user_email,
                btc_address=address,
                description="Test payment"
            )
            
            payment_info = bitcoin_service.create_payment_request(payment_request)
            logger.info(f"Payment request created: {payment_info}")
            
            # Check payment status
            status = bitcoin_service.check_payment_status(payment_info["payment_id"])
            logger.info(f"Payment status: {status}")
            
        except Exception as e:
            logger.error(f"Bitcoin service error: {e}")
        
        # 5. Web Search Service Demo
        logger.info("=== Web Search Service Demo ===")
        try:
            search_request = InvestigationRequest(
                query="artificial intelligence trends 2024",
                max_results=3
            )
            
            results = websearch_service.search(search_request)
            logger.info(f"Found {len(results)} search results")
            
            # Summarize results
            summary = websearch_service.summarize_results(results)
            logger.info(f"Search summary: {summary}")
            
        except Exception as e:
            logger.error(f"Web search service error: {e}")
        
        return {
            "services_tested": ["email", "llm", "content", "bitcoin", "websearch"],
            "integration_successful": True
        }


class ServiceStatusNode(SimpleNode):
    """Node that checks service status."""
    
    def process(self, shared: SharedState):
        """Check status of all services."""
        logger = get_logger("ServiceStatusNode")
        
        logger.info("=== Service Status Check ===")
        
        services_status = {}
        
        # Check each service
        try:
            # Bitcoin service info
            btc_info = bitcoin_service.get_service_info()
            services_status["bitcoin"] = btc_info
            
            # Web search service info
            search_info = websearch_service.get_service_info()
            services_status["websearch"] = search_info
            
            # Content service info
            content_types = content_service.get_supported_types()
            services_status["content"] = {
                "supported_types": content_types,
                "service_status": "operational"
            }
            
            logger.info("All services operational")
            
        except Exception as e:
            logger.error(f"Service status check failed: {e}")
            services_status["error"] = str(e)
        
        return {
            "services_status": services_status,
            "all_operational": "error" not in services_status
        }


def create_service_demo_flow():
    """Create a flow that demonstrates service integration."""
    return (create_flow("service_demo_flow", FlowType.TOKENED_USER, requires_tokens=True)
            .add_step("integration", ServiceIntegrationNode("integration"))
            .add_step("status", ServiceStatusNode("status"))
            .set_start("integration")
            .add_end_step("status")
            .add_routing("integration", "default", "status")
            .build())


def main():
    """Run the service integration example."""
    # Set up logging
    setup_logging(level="INFO", log_format="standard")
    logger = get_logger("ServiceIntegration")
    
    # Create flow
    flow = create_service_demo_flow()
    
    # Create shared state
    shared = SharedState(user="demo@example.com")
    
    # Run the flow
    logger.info("Starting service integration demo...")
    result = flow.run(shared)
    
    if result.success:
        logger.info("✅ Service integration demo completed successfully!")
        logger.info(f"Final state: {shared}")
    else:
        logger.error(f"❌ Service integration demo failed: {result.error}")


if __name__ == "__main__":
    main() 