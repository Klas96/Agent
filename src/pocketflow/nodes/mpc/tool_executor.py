"""
MPC wrapper node for tool execution.

This node calls the Tools-MPC process to execute tools instead of using local tools.
"""

from typing import Dict, Any, Optional
from ...core.node import Node
from ...core.types import SharedState
from ...services.mcp_client import get_mpc_manager
from ...utils.logging import get_logger

logger = get_logger("MPCToolExecutorNode")


class MPCToolExecutorNode(Node):
    """Node that executes tools via Tools-MPC process."""
    
    def prep(self, shared: SharedState):
        """Prepare by extracting tool execution request from agent action."""
        agent_action = getattr(shared, 'agent_action', None)
        
        if not agent_action:
            logger.error("No agent_action found in shared state")
            return None
        
        action = agent_action.get("action")
        if action != "use_tool":
            logger.warning(f"Agent action is not 'use_tool': {action}")
            return None
        
        parameters = agent_action.get("parameters", {})
        tool_name = parameters.get("tool_name")
        tool_params = parameters.get("parameters", {})
        
        if not tool_name:
            logger.error("No tool_name in agent action parameters")
            return None
        
        return {
            "tool_name": tool_name,
            "parameters": tool_params
        }
    
    def exec(self, prep_res):
        """Execute tool via Tools-MPC."""
        if not prep_res:
            return None
        
        try:
            tool_name = prep_res["tool_name"]
            tool_params = prep_res["parameters"]
            
            mpc_manager = get_mpc_manager()
            result = mpc_manager.execute_tool(tool_name, **tool_params)
            
            if result.get("success"):
                logger.info(f"Tool '{tool_name}' executed successfully via MPC")
                return result.get("data")
            else:
                error = result.get("error", "Unknown error")
                logger.error(f"Tool execution failed via MPC: {error}")
                return {"error": error}
                
        except Exception as e:
            logger.error(f"Error executing tool via MPC: {e}", exc_info=True)
            return {"error": str(e)}
    
    def post(self, shared: SharedState, prep_res, exec_res):
        """Post-process by storing tool result."""
        if exec_res:
            # Store tool result in shared state
            if not hasattr(shared, 'tool_results') or shared.tool_results is None:
                shared.tool_results = []
            
            tool_name = prep_res.get("tool_name") if prep_res else "unknown"
            shared.tool_results.append({
                "tool_name": tool_name,
                "result": exec_res
            })
            
            logger.info(f"Stored tool result for '{tool_name}'")
            return "default"
        else:
            logger.error("Tool execution failed")
            return "error"
