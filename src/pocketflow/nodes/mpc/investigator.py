"""
MPC wrapper node for topic investigation.

This node calls the Research-MPC process to investigate topics instead of using local services.
"""

from typing import Dict, Any, Optional
from ...core.node import Node
from ...core.types import SharedState
from ...services.mcp_client import get_mpc_manager
from ...utils.logging import get_logger

logger = get_logger("MPCInvestigatorNode")


class MPCInvestigatorNode(Node):
    """Node that investigates topics via Research-MPC process."""
    
    def prep(self, shared: SharedState):
        """Prepare by extracting investigation request from agent action or email."""
        # Check agent action first
        agent_action = getattr(shared, 'agent_action', None)
        if agent_action and agent_action.get("action") == "investigate":
            parameters = agent_action.get("parameters", {})
            topic = parameters.get("topic")
            depth = parameters.get("depth", "shallow")
            max_results = parameters.get("max_results", 10)
            
            if topic:
                return {
                    "topic": topic,
                    "depth": depth,
                    "max_results": max_results
                }
        
        # Fallback: extract from email body
        email = getattr(shared, 'email', {})
        if email:
            body = email.get("body", "")
            # Simple extraction - could be enhanced
            if body:
                return {
                    "topic": body[:200],  # Use first 200 chars as topic
                    "depth": "shallow",
                    "max_results": 10
                }
        
        logger.error("No investigation topic found")
        return None
    
    def exec(self, prep_res):
        """Execute investigation via Research-MPC."""
        if not prep_res:
            return None
        
        try:
            topic = prep_res["topic"]
            depth = prep_res.get("depth", "shallow")
            max_results = prep_res.get("max_results", 10)
            
            mpc_manager = get_mpc_manager()
            result = mpc_manager.investigate_topic(topic, depth, max_results)
            
            if result:
                logger.info(f"Investigation completed successfully via MPC for topic: {topic}")
                return result
            else:
                logger.error("Investigation failed via MPC")
                return {
                    "findings": [],
                    "summary": "Investigation failed"
                }
                
        except Exception as e:
            logger.error(f"Error investigating topic via MPC: {e}", exc_info=True)
            return {
                "findings": [],
                "summary": f"Investigation error: {str(e)}"
            }
    
    def post(self, shared: SharedState, prep_res, exec_res):
        """Post-process by storing investigation results."""
        if exec_res:
            # Store investigation results
            shared.rag_context = {
                "findings": exec_res.get("findings", []),
                "summary": exec_res.get("summary", "")
            }
            
            logger.info("Stored investigation results")
            return "default"
        else:
            logger.error("Investigation failed")
            return "error"
