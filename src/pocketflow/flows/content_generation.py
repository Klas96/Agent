"""
Content generation flow for PocketFlow.

This flow specializes in content generation with optimized routing.
"""

from typing import Dict, Any, Optional

from ..core.flow import Flow, FlowBuilder
from ..core.types import FlowType, SharedState
from ..nodes import (
    ConversationContextNode,
    AgentNode, PopAgentActionNode,
    ContentCreatorNode, ContentParamNode, GenerateContentNode, DocumentGeneratorNode,
    SendEmailNode, FinishNode, FetchEmailNode
)
from ..utils.logging import get_logger


class ContentGenerationFlow:
    """Specialized flow for content generation."""
    
    def __init__(self):
        self.logger = get_logger("ContentGenerationFlow")
        self._flow = self._build_flow()
    
    def _build_flow(self) -> Flow:
        """Build the content generation flow."""
        return (FlowBuilder("content_generation", FlowType.USER, requires_tokens=False)
                .add_step("fetch_email", FetchEmailNode("fetch_email"))
                .add_step("conversation_context", ConversationContextNode("conversation_context"))
                .add_step("agent", AgentNode("agent"))
                .add_step("pop_agent_action", PopAgentActionNode("pop_agent_action"))
                .add_step("content_generation", ContentCreatorNode("content_generation"))
                .add_step("generate_content", GenerateContentNode("generate_content"))
                .add_step("pop_after_generation", PopAgentActionNode("pop_after_generation"))
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
                .add_routing("agent", "default", "pop_agent_action")
                # Action routing
                .add_routing("pop_agent_action", "finish", "finish")
                .add_routing("pop_agent_action", "generate", "content_generation")
                .add_routing("pop_agent_action", "send", "send_email")
                # Content generation routing
                .add_routing("content_generation", "default", "generate_content")
                .add_routing("generate_content", "default", "pop_after_generation")
                .add_routing("generate_content", "generation_failed", "pop_after_generation")
                # Pop after generation routing
                .add_routing("pop_after_generation", "finish", "finish")
                .add_routing("pop_after_generation", "send", "send_email")
                # Email sending routing
                .add_routing("send_email", "send_failed", "finish")
                .add_routing("send_email", "default", "finish")
                .build())
    
    def run(self, shared: SharedState) -> Dict[str, Any]:
        """
        Run the content generation flow.
        
        Args:
            shared: Shared state containing conversation context
            
        Returns:
            Flow execution result
        """
        try:
            self.logger.info("Starting content generation flow")
            result = self._flow.run(shared)
            
            if result.success:
                self.logger.info("Content generation flow completed successfully")
            else:
                self.logger.error(f"Content generation flow failed: {result.error}")
            
            return {
                "success": result.success,
                "error": result.error,
                "final_state": dict(shared) if shared else None
            }
            
        except Exception as e:
            self.logger.error(f"Unexpected error in ContentGenerationFlow: {e}")
            return {
                "success": False,
                "error": str(e),
                "final_state": dict(shared) if shared else None
            }
    
    def get_flow_info(self) -> Dict[str, Any]:
        """Get information about the flow."""
        return {
            "name": "content_generation",
            "type": FlowType.USER,
            "requires_tokens": False,
            "steps": [
                "fetch_email",
                "conversation_context",
                "agent",
                "pop_agent_action",
                "content_generation",
                "generate_content",
                "pop_after_generation",
                "send_email",
                "finish"
            ],
            "capabilities": [
                "conversation_management",
                "llm_processing",
                "content_generation",
                "email_sending"
            ],
            "specializations": [
                "optimized_for_content_generation",
                "focused_routing",
                "content_type_detection"
            ]
        }


# Global content generation flow instance
content_generation_flow = ContentGenerationFlow() 