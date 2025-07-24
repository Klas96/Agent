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
    ContentCreatorNode, ContentParamNode, GenerateContentNode,
    SendEmailNode, FinishNode
)
from ..utils.logging import get_logger


class ContentGenerationFlow:
    """Specialized flow for content generation."""
    
    def __init__(self):
        self.logger = get_logger("ContentGenerationFlow")
        self._flow = self._build_flow()
    
    def _build_flow(self) -> Flow:
        """Build the content generation flow."""
        return (FlowBuilder("content_generation", FlowType.TOKENED_USER, requires_tokens=True)
                .add_step("conversation_context", ConversationContextNode("conversation_context"))
                .add_step("agent", AgentNode("agent"))
                .add_step("pop_action", PopAgentActionNode("pop_action"))
                .add_step("content_creator", ContentCreatorNode("content_creator"))
                .add_step("content_params", ContentParamNode("content_params"))
                .add_step("generate_content", GenerateContentNode("generate_content"))
                .add_step("send_email", SendEmailNode("send_email"))
                .add_step("finish", FinishNode("finish"))
                .set_start("conversation_context")
                .add_end_step("send_email")
                .add_end_step("finish")
                # Conversation context routing
                .add_routing("conversation_context", "no_context", "finish")
                .add_routing("conversation_context", "default", "agent")
                # Agent routing
                .add_routing("agent", "finish", "finish")
                .add_routing("agent", "default", "pop_action")
                # Action routing - focus on content generation
                .add_routing("pop_action", "finish", "finish")
                .add_routing("pop_action", "generate", "content_creator")
                .add_routing("pop_action", "send", "send_email")
                # Content generation routing
                .add_routing("content_creator", "default", "content_params")
                .add_routing("content_params", "default", "generate_content")
                .add_routing("generate_content", "generation_failed", "finish")
                .add_routing("generate_content", "default", "pop_action")
                # Email sending routing
                .add_routing("send_email", "send_failed", "finish")
                .add_routing("send_email", "default", "pop_action")
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
            "type": FlowType.TOKENED_USER,
            "requires_tokens": True,
            "steps": [
                "conversation_context",
                "agent",
                "pop_action",
                "content_creator",
                "content_params",
                "generate_content",
                "send_email"
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