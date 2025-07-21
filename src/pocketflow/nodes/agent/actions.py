"""
Agent action management node for PocketFlow.

This node handles popping and routing agent actions.
"""

from typing import Dict, Any, Optional

from ...core.node import SimpleNode
from ...core.types import SharedState
from ...utils.logging import get_logger


class PopAgentActionNode(SimpleNode):
    """Node for popping and routing agent actions."""
    
    def __init__(self, name: str = "pop_agent_action"):
        super().__init__(name)
        self.logger = get_logger("PopAgentActionNode")
    
    def process(self, shared: SharedState) -> Dict[str, Any]:
        """
        Pop the next action from the queue and set it as current action.
        
        Args:
            shared: Shared state containing action queue
            
        Returns:
            Processing result with routing information
        """
        try:
            queue = shared.get("action_queue", [])
            if not queue:
                self.logger.info("No more actions in queue")
                return {"route": "finish"}
            
            # Pop the next action
            action = queue.pop(0)
            shared["action_queue"] = queue
            shared["agent_action"] = action
            
            self.logger.info(f"Popped action: {action.get('action', 'unknown')}")
            
            # Route based on action type
            action_type = action.get("action")
            if not action_type:
                self.logger.warning("No action type found in popped action")
                return {"route": "default"}
            
            return {"route": action_type}
            
        except Exception as e:
            self.logger.error(f"Error in PopAgentActionNode: {e}")
            return {"route": "default", "error": str(e)} 