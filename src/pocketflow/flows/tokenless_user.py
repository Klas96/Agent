"""
Tokenless user flow for PocketFlow.

This flow handles users without tokens, providing payment requests.
"""

from typing import Dict, Any, Optional

from ..core.flow import Flow, FlowBuilder
from ..core.types import FlowType, SharedState
from ..nodes import (
    FetchEmailNode, ConversationContextNode,
    AgentNode, PopAgentActionNode,
    PurchaseTokensWithBitcoinNode, FinishNode
)
from ..nodes.email.tokenless_send import TokenlessSendEmailNode
from ..utils.logging import get_logger


class TokenlessUserFlow:
    """Flow for users without tokens, providing payment requests."""
    
    def __init__(self):
        self.logger = get_logger("TokenlessUserFlow")
        self._flow = self._build_flow()
    
    def _build_flow(self) -> Flow:
        """Build the tokenless user flow."""
        return (FlowBuilder("tokenless_user", FlowType.TOKENLESS_USER, requires_tokens=False)
                .add_step("fetch_email", FetchEmailNode("fetch_email"))
                .add_step("conversation_context", ConversationContextNode("conversation_context"))
                .add_step("agent", AgentNode("agent"))
                .add_step("pop_action", PopAgentActionNode("pop_action"))
                .add_step("payment_request", PurchaseTokensWithBitcoinNode("payment_request"))
                .add_step("send_email", TokenlessSendEmailNode("send_email"))
                .add_step("finish", FinishNode("finish"))
                .set_start("fetch_email")
                .add_end_step("finish")
                # Email fetching routing
                .add_routing("fetch_email", "no_email", "finish")
                .add_routing("fetch_email", "default", "conversation_context")
                # Conversation context routing
                .add_routing("conversation_context", "no_context", "finish")
                .add_routing("conversation_context", "default", "agent")
                # Agent routing
                .add_routing("agent", "finish", "payment_request")  # Changed from "finish" to "payment_request"
                .add_routing("agent", "default", "pop_action")
                # Action routing - redirect content generation to payment
                .add_routing("pop_action", "finish", "finish")
                .add_routing("pop_action", "generate", "payment_request")
                .add_routing("pop_action", "investigate", "payment_request")
                .add_routing("pop_action", "send", "payment_request")
                # Payment request routing
                .add_routing("payment_request", "send", "send_email")
                .add_routing("payment_request", "default", "finish")
                # Email sending routing
                .add_routing("send_email", "send_failed", "finish")
                .add_routing("send_email", "default", "finish")
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
            "type": FlowType.TOKENLESS_USER,
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
                "payment_requests",
                "email_sending"
            ],
            "restrictions": [
                "no_content_generation",
                "no_investigation",
                "payment_required_for_features"
            ]
        }


# Global tokenless user flow instance
tokenless_user_flow = TokenlessUserFlow() 