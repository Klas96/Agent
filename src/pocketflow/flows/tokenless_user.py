"""
Tokenless user flow for PocketFlow.

This flow handles users without tokens, providing payment requests.
"""

from typing import Dict, Any, Optional

from ..core.flow import FlowBuilder, Flow
from ..core.types import FlowType, SharedState
from ..nodes.email import FetchEmailNode, SendEmailNode, ConversationContextNode
from ..nodes.agent import AgentNode, PopAgentActionNode
# ContentCreatorNode moved to MPC - tokenless users should use email_processor flow
# from ..nodes.content import ContentCreatorNode
from ..nodes.mpc import MPCContentGeneratorNode
from ..nodes import FinishNode
from ..utils.logging import get_logger


class TokenlessUserFlow:
    """Flow for users without tokens, providing payment requests."""
    
    def __init__(self):
        self.logger = get_logger("TokenlessUserFlow")
        self._flow = self._build_flow()
    
    def _build_flow(self) -> Flow:
        """Build the tokenless user flow."""
        return (FlowBuilder("user", FlowType.USER, requires_tokens=False)
                .add_step("fetch_email", FetchEmailNode("fetch_email"))
                .add_step("conversation_context", ConversationContextNode("conversation_context"))
                .add_step("agent", AgentNode("agent"))
                .add_step("pop_agent_action", PopAgentActionNode("pop_agent_action"))
                .add_step("content_generation", MPCContentGeneratorNode("content_generation"))
                .add_step("add_donation_footer", self._create_donation_footer_node())
                .add_step("send_email", SendEmailNode("send_email"))
                .add_step("finish", FinishNode("finish"))
                .set_start("fetch_email")
                .add_end_step("finish")
                .build())
    
    def run(self, shared: SharedState) -> Dict[str, Any]:
        """
        Run the tokenless user flow.
        
        Args:
            shared: Shared state containing email context
            
        Returns:
            Flow execution result
        """
        try:
            self.logger.info("Starting tokenless user flow")
            result = self._flow.run(shared)
            
            if result.success:
                self.logger.info("Tokenless user flow completed successfully")
            else:
                self.logger.error(f"Tokenless user flow failed: {result.error}")
            
            return {
                "success": result.success,
                "error": result.error,
                "final_state": dict(shared) if shared else None
            }
            
        except Exception as e:
            self.logger.error(f"Unexpected error in TokenlessUserFlow: {e}")
            return {
                "success": False,
                "error": str(e),
                "final_state": dict(shared) if shared else None
            }
    
    def get_flow_info(self) -> Dict[str, Any]:
        """Get information about the flow."""
        return {
            "name": "tokenless_user",
            "type": FlowType.USER,  # Changed from TOKENLESS_USER to USER
            "requires_tokens": False,
            "steps": [
                "fetch_email",
                "conversation_context",
                "agent",
                "pop_action",
                "payment_request",
                "send_email"
            ],
            "capabilities": [
                "email_fetching",
                "conversation_management",
                "llm_processing",
                "action_management",
                "email_sending"
            ],
            "restrictions": [
                "payment_required",
                "no_content_generation",
                "no_investigation"
            ]
        }

    def _create_donation_footer_node(self):
        """Create the donation footer node."""
        # Temporarily comment out to debug import issue
        # from ..nodes.email_footer_donation import SimpleDonationFooterNode
        # return SimpleDonationFooterNode()
        
        # Return a simple placeholder node for now
        from ..nodes import FinishNode
        return FinishNode("add_donation_footer")


# Global tokenless user flow instance
tokenless_user_flow = TokenlessUserFlow() 