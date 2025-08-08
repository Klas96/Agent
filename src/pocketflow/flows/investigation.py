"""
Investigation flow for PocketFlow.

This flow specializes in web search and investigation.
"""

from typing import Dict, Any, Optional

from ..core.flow import Flow, FlowBuilder
from ..core.types import FlowType, SharedState
from ..nodes import (
    ConversationContextNode,
    AgentNode, PopAgentActionNode,
    InvestigateTopicNode,
    SendEmailNode, FinishNode,
    FetchEmailNode
)
from ..utils.logging import get_logger


class InvestigationFlow:
    """Specialized flow for investigation and web search."""
    
    def __init__(self):
        self.logger = get_logger("InvestigationFlow")
        self._flow = self._build_flow()
    
    def _build_flow(self) -> Flow:
        """Build the investigation flow."""
        return (FlowBuilder("investigation", FlowType.USER, requires_tokens=False)
                .add_step("fetch_email", FetchEmailNode("fetch_email"))
                .add_step("conversation_context", ConversationContextNode("conversation_context"))
                .add_step("agent", AgentNode("agent"))
                .add_step("pop_agent_action", PopAgentActionNode("pop_agent_action"))
                .add_step("investigation", InvestigateTopicNode("investigation"))
                .add_step("send_email", SendEmailNode("send_email"))
                .add_step("finish", FinishNode("finish"))
                .set_start("fetch_email")
                .add_end_step("finish")
                .build())
    
    def run(self, shared: SharedState) -> Dict[str, Any]:
        """
        Run the investigation flow.
        
        Args:
            shared: Shared state containing conversation context
            
        Returns:
            Flow execution result
        """
        try:
            self.logger.info("Starting investigation flow")
            result = self._flow.run(shared)
            
            if result.success:
                self.logger.info("Investigation flow completed successfully")
            else:
                self.logger.error(f"Investigation flow failed: {result.error}")
            
            return {
                "success": result.success,
                "error": result.error,
                "final_state": dict(shared) if shared else None
            }
            
        except Exception as e:
            self.logger.error(f"Unexpected error in InvestigationFlow: {e}")
            return {
                "success": False,
                "error": str(e),
                "final_state": dict(shared) if shared else None
            }
    
    def get_flow_info(self) -> Dict[str, Any]:
        """Get information about the flow."""
        return {
            "name": "investigation",
            "type": FlowType.TOKENED_USER,
            "requires_tokens": True,
            "steps": [
                "conversation_context",
                "agent",
                "pop_action",
                "investigate",
                "send_email"
            ],
            "capabilities": [
                "conversation_management",
                "llm_processing",
                "web_search",
                "investigation",
                "email_sending"
            ],
            "specializations": [
                "optimized_for_investigation",
                "web_search_focused",
                "result_summarization"
            ]
        }


# Global investigation flow instance
investigation_flow = InvestigationFlow() 