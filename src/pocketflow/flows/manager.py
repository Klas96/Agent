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
from .content_generation import ContentGenerationFlow
from .tool_flow import ToolFlow


class FlowManager:
    """Manager for dynamic flow selection and execution."""
    
    def __init__(self):
        self.logger = get_logger("FlowManager")
        self._flows = {
            "email_processor": email_processor_flow,
            "tokenless_user": tokenless_user_flow,
            "content_generation": ContentGenerationFlow(),
            "tool_flow": ToolFlow()
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
            # Get user email
            user_email = getattr(shared, 'user', None)
            
            # Check if this is a content generation request
            email = getattr(shared, 'email', {})
            body = email.get('body', '').lower() if email else ''
            
            self.logger.info(f"Flow selection - Email body: '{body}'")
            
            # Content generation keywords
            content_keywords = [
                "generate", "create", "make", "song", "music", "image", 
                "document", "write", "podcast", "audio", "episode"
            ]
            
            # Check if the email contains content generation keywords
            detected_keywords = [keyword for keyword in content_keywords if keyword in body]
            if detected_keywords:
                self.logger.info(f"Content generation request detected for {user_email}")
                self.logger.info(f"Detected keywords: {detected_keywords}")
                self.logger.info(f"Auto-selected flow: content_generation")
                return "content_generation"
            
            # Use donation-only approach - tokens system is deprecated
            # All users get the same flow regardless of token status
            flow_type = FlowType.USER
            
            self.logger.info(f"Selecting flow for user: {user_email}, flow_type: {flow_type}")
            self.logger.info(f"Auto-selected flow: email_processor")
            
            # Default to email processor flow (donation-based)
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