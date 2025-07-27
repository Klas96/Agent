"""
Flow manager for PocketFlow.

This module provides dynamic flow selection and management.
"""

from typing import Dict, Any, Optional, List
from enum import Enum

from ..core.types import SharedState, FlowType
from ..core.flow import FlowRouter
from ..utils.logging import get_logger
from .email_processor import email_processor_flow
from .tokenless_user import tokenless_user_flow
from .content_generation import content_generation_flow
from .investigation import investigation_flow
from .payment_processing import payment_processing_flow


class FlowManager:
    """Manager for dynamic flow selection and execution."""
    
    def __init__(self):
        self.logger = get_logger("FlowManager")
        self._flows = {
            "email_processor": email_processor_flow,
            "tokenless_user": tokenless_user_flow,
            "content_generation": content_generation_flow,
            "investigation": investigation_flow,
            "payment_processing": payment_processing_flow
        }
        self._router = FlowRouter()
    
    def select_flow(self, shared: SharedState) -> str:
        """
        Select the appropriate flow based on shared state.
        
        Args:
            shared: Shared state containing user context
            
        Returns:
            Name of the selected flow
        """
        try:
            # Get user email and flow type
            user_email = getattr(shared, 'user', None)
            flow_type = getattr(shared, 'flow_type', None)
            
            # If no flow_type is set, determine it based on user token status
            if flow_type is None:
                if user_email:
                    # Check user's token status
                    from ..services import database_service
                    try:
                        tokens_remaining = database_service.get_tokens(user_email)
                        user_has_tokens = tokens_remaining > 0
                        self.logger.info(f"User {user_email} has {tokens_remaining} tokens")
                        
                        if user_has_tokens:
                            flow_type = FlowType.TOKENED_USER
                        else:
                            flow_type = FlowType.TOKENLESS_USER
                    except Exception as e:
                        self.logger.error(f"Failed to check tokens for {user_email}: {e}")
                        flow_type = FlowType.TOKENLESS_USER  # Default to tokenless if check fails
                else:
                    # No user email, default to tokenless
                    flow_type = FlowType.TOKENLESS_USER
            
            self.logger.info(f"Selecting flow for user: {user_email}, flow_type: {flow_type}")
            
            # Select flow based on flow type
            if flow_type == FlowType.TOKENLESS_USER:
                return "tokenless_user"
            elif flow_type == FlowType.PAYMENT_PENDING:
                return "payment_processing"
            elif flow_type == FlowType.TOKENED_USER:
                # Check if this is a specialized request
                email = getattr(shared, 'email', {})
                body = email.get("body", "").lower() if email else ""
                
                # Check for content generation keywords
                content_keywords = ["generate", "create", "make", "song", "music", "image", "document"]
                if any(keyword in body for keyword in content_keywords):
                    return "content_generation"
                
                # Check for investigation keywords
                investigation_keywords = ["research", "investigate", "find", "search", "what is", "how to"]
                if any(keyword in body for keyword in investigation_keywords):
                    return "investigation"
                
                # Default to full email processor
                return "email_processor"
            else:
                # Default to email processor
                return "email_processor"
                
        except Exception as e:
            self.logger.error(f"Error selecting flow: {e}")
            return "email_processor"  # Default fallback
    
    def run_flow(self, flow_name: str, shared: SharedState) -> Dict[str, Any]:
        """
        Run a specific flow.
        
        Args:
            flow_name: Name of the flow to run
            shared: Shared state for the flow
            
        Returns:
            Flow execution result
        """
        try:
            if flow_name not in self._flows:
                self.logger.error(f"Flow not found: {flow_name}")
                return {
                    "success": False,
                    "error": f"Flow not found: {flow_name}",
                    "final_state": dict(shared) if shared else None
                }
            
            self.logger.info(f"Running flow: {flow_name}")
            flow = self._flows[flow_name]
            result = flow.run(shared)
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error running flow {flow_name}: {e}")
            return {
                "success": False,
                "error": str(e),
                "final_state": dict(shared) if shared else None
            }
    
    def run_auto_select(self, shared: SharedState) -> Dict[str, Any]:
        """
        Automatically select and run the appropriate flow.
        
        Args:
            shared: Shared state containing context
            
        Returns:
            Flow execution result
        """
        try:
            # Select the appropriate flow
            flow_name = self.select_flow(shared)
            self.logger.info(f"Auto-selected flow: {flow_name}")
            
            # Run the selected flow
            return self.run_flow(flow_name, shared)
            
        except Exception as e:
            self.logger.error(f"Error in auto-select flow: {e}")
            return {
                "success": False,
                "error": str(e),
                "final_state": dict(shared) if shared else None
            }
    
    def get_available_flows(self) -> List[Dict[str, Any]]:
        """Get information about all available flows."""
        flows_info = []
        for name, flow in self._flows.items():
            try:
                info = flow.get_flow_info()
                flows_info.append({
                    "name": name,
                    "info": info
                })
            except Exception as e:
                self.logger.error(f"Error getting info for flow {name}: {e}")
                flows_info.append({
                    "name": name,
                    "error": str(e)
                })
        
        return flows_info
    
    def get_flow_info(self, flow_name: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a specific flow.
        
        Args:
            flow_name: Name of the flow
            
        Returns:
            Flow information or None if not found
        """
        if flow_name not in self._flows:
            return None
        
        try:
            return self._flows[flow_name].get_flow_info()
        except Exception as e:
            self.logger.error(f"Error getting info for flow {flow_name}: {e}")
            return {"error": str(e)}


# Global flow manager instance
flow_manager = FlowManager() 