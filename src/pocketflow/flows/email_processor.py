"""
Email processor flow for PocketFlow.

This is the main flow for processing emails with full functionality.
"""

from typing import Dict, Any, Optional

from ..core.flow import Flow, FlowBuilder
from ..core.types import FlowType, SharedState
from ..nodes import (
    FetchEmailNode, SendEmailNode, ConversationContextNode,
    PopAgentActionNode, FinishNode
)
from ..nodes.email.guaranteed_response import GuaranteedResponseNode
from ..nodes.agent.tool_agent import ToolAgentNode
from ..nodes.mpc import (
    MPCContentGeneratorNode,
    MPCToolExecutorNode,
    MPCInvestigatorNode
)
from ..utils.logging import get_logger


class EmailProcessorFlow:
    """Main email processing flow with comprehensive routing."""
    
    def __init__(self):
        self.logger = get_logger("EmailProcessorFlow")
        self._flow = self._build_flow()
    
    def _build_flow(self) -> Flow:
        """Build the email processing flow."""
        return (FlowBuilder("email_processor", FlowType.USER, requires_tokens=False)
                .add_step("fetch_email", FetchEmailNode("fetch_email"))
                .add_step("conversation_context", ConversationContextNode("conversation_context"))
                .add_step("agent", ToolAgentNode("agent"))
                .add_step("pop_action", PopAgentActionNode("pop_action"))
                .add_step("tool_execution", MPCToolExecutorNode("tool_execution"))
                .add_step("generate_content", MPCContentGeneratorNode("generate_content"))
                .add_step("investigate", MPCInvestigatorNode("investigate"))
                .add_step("send_email", SendEmailNode("send_email"))
                .add_step("guaranteed_response", GuaranteedResponseNode("guaranteed_response"))
                .add_step("finish", FinishNode("finish"))
                .set_start("fetch_email")
                .add_end_step("finish")
                # Email fetching routing
                .add_routing("fetch_email", "finish", "guaranteed_response")
                .add_routing("fetch_email", "default", "conversation_context")
                # Conversation context routing
                .add_routing("conversation_context", "finish", "guaranteed_response")
                .add_routing("conversation_context", "no_email", "guaranteed_response")
                .add_routing("conversation_context", "default", "agent")
                # Agent routing
                .add_routing("agent", "finish", "guaranteed_response")
                .add_routing("agent", "default", "pop_action")
                # Action routing
                .add_routing("pop_action", "finish", "guaranteed_response")
                .add_routing("pop_action", "use_tool", "tool_execution")
                .add_routing("pop_action", "generate", "generate_content")
                .add_routing("pop_action", "investigate", "investigate")
                .add_routing("pop_action", "send", "send_email")
                .add_routing("pop_action", "email_send", "send_email")
                # Tool execution routing (via MPC)
                .add_routing("tool_execution", "finish", "guaranteed_response")
                .add_routing("tool_execution", "error", "guaranteed_response")
                .add_routing("tool_execution", "default", "pop_action")
                # Content generation routing (via MPC)
                .add_routing("generate_content", "error", "guaranteed_response")
                .add_routing("generate_content", "default", "pop_action")
                # Investigation routing (via MPC)
                .add_routing("investigate", "error", "guaranteed_response")
                .add_routing("investigate", "default", "pop_action")
                # Email sending routing
                .add_routing("send_email", "send_failed", "guaranteed_response")
                .add_routing("send_email", "error", "guaranteed_response")
                .add_routing("send_email", "default", "guaranteed_response")
                # Guaranteed response routing (always goes to finish)
                .add_routing("guaranteed_response", "default", "finish")
                .build())
    
    def run(self, shared: SharedState) -> Dict[str, Any]:
        """
        Run the email processing flow.
        
        This method ensures that a response is always sent, even if the flow fails.
        
        Args:
            shared: Shared state containing email context
            
        Returns:
            Flow execution result
        """
        try:
            self.logger.info("Starting email processing flow")
            result = self._flow.run(shared)
            
            # Check if response was sent
            response_sent = getattr(shared, 'sender_have_gotten_response', False)
            
            if result.success:
                self.logger.info("Email processing flow completed successfully")
                if not response_sent:
                    self.logger.warning("Flow completed but no response was sent, attempting guaranteed response")
                    # Try guaranteed response node directly
                    if "guaranteed_response" in self._flow.steps:
                        try:
                            guaranteed_node = self._flow.steps["guaranteed_response"].node
                            guaranteed_result = guaranteed_node.run(shared)
                            if guaranteed_result.success:
                                self.logger.info("Guaranteed response sent after flow completion")
                                result.metadata = result.metadata or {}
                                result.metadata["guaranteed_response_sent"] = True
                        except Exception as e:
                            self.logger.error(f"Failed to send guaranteed response after flow completion: {e}")
            else:
                self.logger.error(f"Email processing flow failed: {result.error}")
                # The flow.run() method should have already tried guaranteed response,
                # but verify response was sent
                if not response_sent:
                    self.logger.warning("Flow failed and no response was sent, attempting guaranteed response")
                    if "guaranteed_response" in self._flow.steps:
                        try:
                            guaranteed_node = self._flow.steps["guaranteed_response"].node
                            guaranteed_result = guaranteed_node.run(shared)
                            if guaranteed_result.success:
                                self.logger.info("Guaranteed response sent after flow failure")
                                result.success = True  # Mark as success since we sent a response
                                result.metadata = result.metadata or {}
                                result.metadata["guaranteed_response_sent"] = True
                        except Exception as e:
                            self.logger.error(f"Failed to send guaranteed response after flow failure: {e}")
            
            return {
                "success": result.success,
                "error": result.error,
                "response_sent": getattr(shared, 'sender_have_gotten_response', False),
                "final_state": dict(shared) if shared else None
            }
            
        except Exception as e:
            self.logger.error(f"Unexpected error in EmailProcessorFlow: {e}", exc_info=True)
            # Store error in shared state
            shared.last_error = str(e)
            
            # Try to send guaranteed response even on exception
            try:
                if "guaranteed_response" in self._flow.steps:
                    guaranteed_node = self._flow.steps["guaranteed_response"].node
                    guaranteed_result = guaranteed_node.run(shared)
                    if guaranteed_result.success:
                        self.logger.info("Guaranteed response sent after exception")
                        return {
                            "success": True,
                            "error": str(e),
                            "response_sent": True,
                            "guaranteed_response_sent": True,
                            "final_state": dict(shared) if shared else None
                        }
            except Exception as guaranteed_error:
                self.logger.error(f"Failed to send guaranteed response after exception: {guaranteed_error}")
            
            return {
                "success": False,
                "error": str(e),
                "response_sent": getattr(shared, 'sender_have_gotten_response', False),
                "final_state": dict(shared) if shared else None
            }
    
    def get_flow_info(self) -> Dict[str, Any]:
        """Get information about the flow."""
        return {
            "name": "email_processor",
            "type": FlowType.USER,
            "requires_tokens": False,
            "steps": [
                "fetch_email",
                "conversation_context", 
                "agent",
                "pop_action",
                "tool_execution",  # via MPC
                "generate_content",  # via MPC
                "investigate",  # via MPC
                "send_email"
            ],
            "capabilities": [
                "email_fetching",
                "conversation_management",
                "llm_processing",
                "content_generation_via_mpc",
                "investigation_via_mpc",
                "tool_execution_via_mpc",
                "email_sending"
            ]
        }


# Global email processor flow instance
email_processor_flow = EmailProcessorFlow() 