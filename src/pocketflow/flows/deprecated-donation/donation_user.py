"""
Donation user flow for PocketFlow.

This flow handles all users with donation support (no token management).
"""

from typing import Dict, Any

from ..core.flow import Flow, FlowBuilder
from ..core.types import FlowType, SharedState
from ..nodes.email.fetch import FetchEmailNode
from ..nodes.email.context import ConversationContextNode
from ..nodes.agent.core import AgentNode
from ..nodes.agent.actions import PopAgentActionNode
from ..nodes.email.send import SendEmailNode
from ..nodes import FinishNode
from ..utils.logging import get_logger


class DonationUserFlow:
    """Flow for all users with donation support."""
    
    def __init__(self):
        self.logger = get_logger("DonationUserFlow")
        self._flow = self._build_flow()
    
    def _build_flow(self) -> Flow:
        """Build the simplified donation user flow."""
        return (FlowBuilder("user", FlowType.USER, requires_tokens=False)
                .add_step("fetch_email", FetchEmailNode("fetch_email"))
                .add_step("conversation_context", ConversationContextNode("conversation_context"))
                .add_step("agent", AgentNode("agent"))
                .add_step("pop_action", PopAgentActionNode("pop_action"))
                .add_step("generate_content", self._create_content_generation_node())
                .add_step("add_donation_footer", self._create_donation_footer_node())
                .add_step("send_email", SendEmailNode("send_email"))
                .add_step("finish", FinishNode("finish"))
                .set_start("fetch_email")
                .add_end_step("finish")
                # Simplified routing - linear flow with minimal branching
                .add_routing("fetch_email", "finish", "finish")
                .add_routing("fetch_email", "default", "conversation_context")
                .add_routing("conversation_context", "no_context", "finish")
                .add_routing("conversation_context", "default", "agent")
                .add_routing("agent", "default", "pop_action")
                .add_routing("pop_action", "finish", "finish")
                .add_routing("pop_action", "default", "generate_content")
                .add_routing("generate_content", "default", "add_donation_footer")
                .add_routing("add_donation_footer", "default", "send_email")
                .add_routing("send_email", "default", "finish")
                .build())
    
    def _create_content_generation_node(self):
        """Create a content generation node for the donation flow."""
        from ..nodes.content.creator import ContentCreatorNode
        
        class DonationContentGenerationNode(ContentCreatorNode):
            """Content generation node for donation flow."""
            
            def process(self, shared: SharedState) -> Dict[str, Any]:
                """Generate content without token validation."""
                # Always allow content generation in donation flow
                return super().process(shared)
        
        return DonationContentGenerationNode("generate_content")
    
    def _create_donation_footer_node(self):
        """Create a donation footer node for the donation flow."""
        from ..nodes.email_footer_donation import SimpleDonationFooterNode
        
        return SimpleDonationFooterNode("add_donation_footer")
    
    def run(self, shared: SharedState) -> Dict[str, Any]:
        """
        Run the donation user flow.
        
        Args:
            shared: Shared state containing email context
            
        Returns:
            Flow execution result
        """
        try:
            self.logger.info("Starting donation user flow")
            result = self._flow.run(shared)
            
            if result.success:
                self.logger.info("Donation user flow completed successfully")
            else:
                self.logger.error(f"Donation user flow failed: {result.error}")
            
            return {
                "success": result.success,
                "error": result.error,
                "final_state": dict(shared) if shared else None
            }
            
        except Exception as e:
            self.logger.error(f"Unexpected error in DonationUserFlow: {e}")
            return {
                "success": False,
                "error": str(e),
                "final_state": dict(shared) if shared else None
            }
    
    def get_flow_info(self) -> Dict[str, Any]:
        """Get information about the flow."""
        return {
            "name": "user",
            "type": FlowType.USER,
            "requires_tokens": False,
            "steps": [
                "fetch_email",
                "conversation_context", 
                "agent",
                "pop_action",
                "generate_content",
                "add_donation_footer",
                "send_email"
            ],
            "capabilities": [
                "email_fetching",
                "conversation_management",
                "llm_processing",
                "action_management",
                "content_generation",
                "donation_footer",
                "email_sending"
            ],
            "features": [
                "full_functionality",
                "donation_support",
                "no_token_management",
                "simplified_user_experience"
            ]
        } 