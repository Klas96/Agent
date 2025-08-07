"""
Email processor flow for PocketFlow.

This is the main flow for processing emails with full functionality.
"""

from typing import Dict, Any, Optional

from ..core.flow import Flow, FlowBuilder
from ..core.types import FlowType, SharedState
from ..nodes import (
    FetchEmailNode, SendEmailNode, ConversationContextNode,
    AgentNode, PopAgentActionNode,
    ContentCreatorNode, ContentParamNode, GenerateContentNode,
    InvestigateTopicNode, FinishNode
)
from ..nodes.agent.core import ToolExecutionNode
from ..utils.logging import get_logger


class EmailProcessorFlow:
    """Main email processing flow with comprehensive routing."""
    
    def __init__(self):
        self.logger = get_logger("EmailProcessorFlow")
        self._flow = self._build_flow()
    
    def _build_flow(self) -> Flow:
        """Build the email processing flow."""
        return (FlowBuilder("email_processor", FlowType.TOKENED_USER, requires_tokens=True)
                .add_step("fetch_email", FetchEmailNode("fetch_email"))
                .add_step("conversation_context", ConversationContextNode("conversation_context"))
                .add_step("agent", AgentNode("agent"))
                .add_step("pop_action", PopAgentActionNode("pop_action"))
                .add_step("tool_execution", ToolExecutionNode("tool_execution"))
                .add_step("content_creator", ContentCreatorNode("content_creator"))
                .add_step("content_params", ContentParamNode("content_params"))
                .add_step("generate_content", GenerateContentNode("generate_content"))
                .add_step("investigate", InvestigateTopicNode("investigate"))
                .add_step("send_email", SendEmailNode("send_email"))
                .add_step("finish", FinishNode("finish"))
                .set_start("fetch_email")
                .add_end_step("finish")
                # Email fetching routing
                .add_routing("fetch_email", "finish", "finish")
                .add_routing("fetch_email", "default", "conversation_context")
                # Conversation context routing
                .add_routing("conversation_context", "finish", "finish")
                .add_routing("conversation_context", "no_email", "finish")
                .add_routing("conversation_context", "default", "agent")
                # Agent routing
                .add_routing("agent", "finish", "finish")
                .add_routing("agent", "default", "pop_action")
                # Action routing
                .add_routing("pop_action", "finish", "finish")
                .add_routing("pop_action", "use_tool", "tool_execution")
                .add_routing("pop_action", "generate", "content_creator")
                .add_routing("pop_action", "investigate", "investigate")
                .add_routing("pop_action", "send", "send_email")
                # Tool execution routing
                .add_routing("tool_execution", "finish", "finish")
                .add_routing("tool_execution", "send", "send_email")
                # Content generation routing
                .add_routing("content_creator", "default", "content_params")
                .add_routing("content_params", "default", "generate_content")
                .add_routing("generate_content", "generation_failed", "finish")
                .add_routing("generate_content", "default", "pop_action")
                # Investigation routing
                .add_routing("investigate", "default", "pop_action")
                # Email sending routing
                .add_routing("send_email", "send_failed", "finish")
                .add_routing("send_email", "default", "finish")
                .build())
    
    def run(self, shared: SharedState) -> Dict[str, Any]:
        """
        Run the email processing flow.
        
        Args:
            shared: Shared state containing email context
            
        Returns:
            Flow execution result
        """
        try:
            self.logger.info("Starting email processing flow")
            result = self._flow.run(shared)
            
            if result.success:
                self.logger.info("Email processing flow completed successfully")
            else:
                self.logger.error(f"Email processing flow failed: {result.error}")
            
            return {
                "success": result.success,
                "error": result.error,
                "final_state": dict(shared) if shared else None
            }
            
        except Exception as e:
            self.logger.error(f"Unexpected error in EmailProcessorFlow: {e}")
            return {
                "success": False,
                "error": str(e),
                "final_state": dict(shared) if shared else None
            }
    
    def get_flow_info(self) -> Dict[str, Any]:
        """Get information about the flow."""
        return {
            "name": "email_processor",
            "type": FlowType.TOKENED_USER,
            "requires_tokens": True,
            "steps": [
                "fetch_email",
                "conversation_context", 
                "agent",
                "pop_action",
                "content_creator",
                "content_params",
                "generate_content",
                "investigate",
                "send_email"
            ],
            "capabilities": [
                "email_fetching",
                "conversation_management",
                "llm_processing",
                "content_generation",
                "investigation",
                "email_sending"
            ]
        }


# Global email processor flow instance
email_processor_flow = EmailProcessorFlow() 