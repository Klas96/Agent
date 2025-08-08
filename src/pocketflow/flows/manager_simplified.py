"""
Simplified flow manager for donation-only model.

This module provides flow management without token-based routing.
"""

from typing import Dict, Any, Optional
from ..core.types import SharedState, FlowType
from ..utils.logging import get_logger


class SimplifiedFlowManager:
    """Simplified flow manager for donation-only model."""
    
    def __init__(self):
        self.logger = get_logger("SimplifiedFlowManager")
        self.flows = {
            "user_flow": {
                "name": "User Flow",
                "description": "Unified flow for all users",
                "flow_type": FlowType.USER,
                "requires_tokens": False,
                "timeout": 300
            }
        }
    
    def select_flow(self, shared: SharedState) -> str:
        """
        Select the appropriate flow (always donation flow).
        
        Args:
            shared: Shared state containing user context
            
        Returns:
            Name of the selected flow
        """
        try:
            user_email = getattr(shared, 'user', None)
            
            # All users get the same flow
            flow_name = "user_flow"
            
            self.logger.info(f"User {user_email} - selected flow: {flow_name}")
            
            return flow_name
            
        except Exception as e:
            self.logger.error(f"Error selecting flow: {e}")
            return "user_flow"  # Default fallback
    
    def get_flow_info(self, flow_name: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a specific flow.
        
        Args:
            flow_name: Name of the flow
            
        Returns:
            Flow information or None if not found
        """
        return self.flows.get(flow_name)
    
    def list_flows(self) -> Dict[str, Dict[str, Any]]:
        """
        List all available flows.
        
        Returns:
            Dictionary of flow information
        """
        return self.flows
    
    def validate_flow(self, flow_name: str) -> bool:
        """
        Validate that a flow exists and is properly configured.
        
        Args:
            flow_name: Name of the flow to validate
            
        Returns:
            True if flow is valid, False otherwise
        """
        if flow_name not in self.flows:
            self.logger.warning(f"Flow '{flow_name}' not found")
            return False
        
        flow_info = self.flows[flow_name]
        required_fields = ["name", "description", "flow_type", "requires_tokens"]
        
        for field in required_fields:
            if field not in flow_info:
                self.logger.warning(f"Flow '{flow_name}' missing required field: {field}")
                return False
        
        return True


# Global simplified flow manager instance
simplified_flow_manager = SimplifiedFlowManager() 