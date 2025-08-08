"""
Tool-enabled flow for PocketFlow.

This flow allows the agent to use tools to accomplish tasks.
"""

from typing import Dict, Any, Optional, List

from ..core.flow import FlowBuilder, Flow
from ..core.types import FlowType, SharedState
from ..nodes.email import FetchEmailNode, SendEmailNode, ConversationContextNode
from ..nodes.agent import AgentNode, PopAgentActionNode
from ..nodes.agent.core import ToolExecutionNode
from ..nodes import FinishNode
from ..utils.logging import get_logger


class ToolFlow:
    """
    Flow that enables tool usage for agents.
    """
    
    def __init__(self):
        self.logger = get_logger("ToolFlow")
        self._flow = self._build_flow()
    
    def _build_flow(self) -> Flow:
        """Build the tool flow."""
        return (FlowBuilder("tool_flow", FlowType.USER, requires_tokens=False)
                .add_step("fetch_email", FetchEmailNode("fetch_email"))
                .add_step("conversation_context", ConversationContextNode("conversation_context"))
                .add_step("agent", AgentNode("agent"))
                .add_step("pop_agent_action", PopAgentActionNode("pop_agent_action"))
                .add_step("tool_execution", ToolExecutionNode("tool_execution"))
                .add_step("send_email", SendEmailNode("send_email"))
                .add_step("finish", FinishNode("finish"))
                .set_start("fetch_email")
                .add_end_step("finish")
                .build())
    
    def run(self, shared: SharedState) -> Dict[str, Any]:
        """
        Run the tool-enabled flow.
        
        Args:
            shared: Shared state containing user input and context
            
        Returns:
            Flow execution result
        """
        try:
            self.logger.info("Starting tool-enabled flow")
            
            # Set user input from email data
            if hasattr(shared, 'email') and shared.email:
                shared.user_input = shared.email.get("subject", "") + "\n" + shared.email.get("body", "")
            
            result = self._flow.run(shared)
            
            if result.success:
                self.logger.info("Tool flow completed successfully")
                
                # Store the final response
                if hasattr(shared, 'agent_response') and shared.agent_response:
                    shared.response = shared.agent_response
                
                # Add tool results to response if any
                if hasattr(shared, 'tool_results') and shared.tool_results:
                    tool_summary = self._format_tool_results(shared.tool_results)
                    shared.response += f"\n\n**Tool Results:**\n{tool_summary}"
            else:
                self.logger.error(f"Tool flow failed: {result.error}")
            
            return {
                "success": result.success,
                "error": result.error,
                "final_state": dict(shared) if shared else None
            }
            
        except Exception as e:
            self.logger.error(f"Unexpected error in ToolFlow: {e}")
            return {
                "success": False,
                "error": str(e),
                "final_state": dict(shared) if shared else None
            }
    
    def _format_tool_results(self, tool_results: List[Dict[str, Any]]) -> str:
        """
        Format tool results for inclusion in the response.
        
        Args:
            tool_results: List of tool execution results
            
        Returns:
            Formatted string of tool results
        """
        if not tool_results:
            return ""
        
        summary = []
        for result in tool_results:
            tool_name = result["tool_name"]
            success = result["success"]
            
            if success:
                data = result["data"]
                summary.append(f"✅ {tool_name}: {str(data)}")
            else:
                error = result["error"]
                summary.append(f"❌ {tool_name}: {error}")
        
        return "\n".join(summary) 