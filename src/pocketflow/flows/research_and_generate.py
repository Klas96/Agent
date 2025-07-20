"""
Research and Generate Flow for PocketFlow.

This flow is specialized for the pattern: investigate → generate content based on findings.
"""

from typing import Dict, Any, Optional

from ..core.flow import Flow, FlowBuilder
from ..core.types import FlowType, SharedState
from ..nodes import (
    FetchEmailNode, SendEmailNode, ConversationContextNode,
    AgentNode, PopAgentActionNode,
    ContentCreatorNode, ContentParamNode, GenerateContentNode,
    InvestigateTopicNode
)
from ..utils.logging import get_logger


class ResearchAndGenerateFlow:
    """Flow specialized for investigate → generate content pattern."""
    
    def __init__(self):
        self.logger = get_logger("ResearchAndGenerateFlow")
        self._flow = self._build_flow()
    
    def _build_flow(self) -> Flow:
        """Build the research and generate flow."""
        return (FlowBuilder("research_and_generate", FlowType.TOKENED_USER, requires_tokens=True)
                .add_step("fetch_email", FetchEmailNode("fetch_email"))
                .add_step("conversation_context", ConversationContextNode("conversation_context"))
                .add_step("agent", AgentNode("agent"))
                .add_step("pop_action", PopAgentActionNode("pop_action"))
                .add_step("investigate", InvestigateTopicNode("investigate"))
                .add_step("content_creator", ContentCreatorNode("content_creator"))
                .add_step("content_params", ContentParamNode("content_params"))
                .add_step("generate_content", GenerateContentNode("generate_content"))
                .add_step("send_email", SendEmailNode("send_email"))
                .set_start("fetch_email")
                .add_end_step("send_email")
                .add_end_step("finish")
                # Email fetching routing
                .add_routing("fetch_email", "no_email", "finish")
                .add_routing("fetch_email", "default", "conversation_context")
                # Conversation context routing
                .add_routing("conversation_context", "no_context", "finish")
                .add_routing("conversation_context", "default", "agent")
                # Agent routing - detect research+generate pattern
                .add_routing("agent", "finish", "finish")
                .add_routing("agent", "research_and_generate", "investigate")
                .add_routing("agent", "investigate", "investigate")
                .add_routing("agent", "generate", "content_creator")
                .add_routing("agent", "default", "pop_action")
                # Action routing
                .add_routing("pop_action", "finish", "finish")
                .add_routing("pop_action", "research_and_generate", "investigate")
                .add_routing("pop_action", "investigate", "investigate")
                .add_routing("pop_action", "generate", "content_creator")
                .add_routing("pop_action", "send", "send_email")
                # Investigation routing - after investigation, go to content generation
                .add_routing("investigate", "investigation_complete", "content_creator")
                .add_routing("investigate", "investigation_failed", "finish")
                .add_routing("investigate", "default", "content_creator")
                # Content generation routing
                .add_routing("content_creator", "default", "content_params")
                .add_routing("content_params", "default", "generate_content")
                .add_routing("generate_content", "generation_failed", "finish")
                .add_routing("generate_content", "default", "send_email")
                # Email sending routing
                .add_routing("send_email", "send_failed", "finish")
                .add_routing("send_email", "default", "finish")
                .build())
    
    def run(self, shared: SharedState) -> Dict[str, Any]:
        """
        Run the research and generate flow.
        
        Args:
            shared: Shared state containing email context
            
        Returns:
            Flow execution result
        """
        try:
            self.logger.info("Starting research and generate flow")
            
            # Enhance the shared state with research context
            if "email" in shared and "body" in shared["email"]:
                # Add research context to help the agent understand this is a research+generate task
                shared["research_context"] = {
                    "mode": "research_and_generate",
                    "original_request": shared["email"]["body"]
                }
            
            result = self._flow.run(shared)
            
            if result.success:
                self.logger.info("Research and generate flow completed successfully")
            else:
                self.logger.error(f"Research and generate flow failed: {result.error}")
            
            return {
                "success": result.success,
                "error": result.error,
                "final_state": dict(shared) if shared else None
            }
            
        except Exception as e:
            self.logger.error(f"Unexpected error in ResearchAndGenerateFlow: {e}")
            return {
                "success": False,
                "error": str(e),
                "final_state": dict(shared) if shared else None
            }
    
    def get_flow_info(self) -> Dict[str, Any]:
        """Get information about the flow."""
        return {
            "name": "research_and_generate",
            "type": FlowType.TOKENED_USER,
            "requires_tokens": True,
            "steps": [
                "fetch_email",
                "conversation_context",
                "agent",
                "pop_action",
                "investigate",
                "content_creator",
                "content_params",
                "generate_content",
                "send_email"
            ],
            "capabilities": [
                "email_fetching",
                "conversation_management",
                "llm_processing",
                "web_investigation",
                "research_based_content_generation",
                "email_sending"
            ],
            "specialization": [
                "investigate_then_generate",
                "research_based_content",
                "web_research_integration"
            ],
            "workflow_pattern": "investigate → generate content based on findings"
        }


# Global research and generate flow instance
research_and_generate_flow = ResearchAndGenerateFlow() 