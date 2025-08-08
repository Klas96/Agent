"""
User status checking and validation nodes.

This module provides nodes for checking user status, validating permissions,
and managing user flow routing.
"""

import logging
from typing import Dict, Any, Optional
from ..core.types import SharedState, FlowType
from ..services.database_service import DatabaseService
from ..utils.logging import get_logger


class UserStatusCheckNode:
    """Node that checks user token status and sets flow type."""
    
    def __init__(self):
        self.logger = get_logger("UserStatusCheckNode")
        self.database_service = DatabaseService()
    
    def process(self, shared: SharedState) -> Optional[Dict[str, Any]]:
        """Check user status and set flow type."""
        logger = get_logger("UserStatusCheckNode")
        user_email = getattr(shared, 'user', None)
        
        if not user_email:
            logger.warning("No user email found in shared state")
            return {"flow_type": FlowType.USER.value}
        
        # All users get the same treatment since tokens are deprecated
        logger.info(f"User {user_email} - tokens system deprecated, using donation-based approach")
        
        return {
            "flow_type": FlowType.USER.value,
            "user_has_tokens": False,
            "tokens_remaining": 0
        }


class TokenValidationNode:
    """Node that validates if user has sufficient tokens for requested action."""
    
    def __init__(self):
        self.logger = get_logger("TokenValidationNode")
        self.database_service = DatabaseService()
    
    def process(self, shared: SharedState) -> Optional[Dict[str, Any]]:
        """Validate if user has sufficient tokens for the requested action."""
        logger = get_logger("TokenValidationNode")
        
        # Tokens are deprecated - all actions are allowed
        logger.info("Token validation skipped - tokens system deprecated")
        
        return {
            "validation_passed": True,
            "tokens_consumed": 0,
            "tokens_remaining": 0
        }


class TokenConsumptionNode:
    """Node that consumes tokens after successful actions."""
    
    def __init__(self):
        self.logger = get_logger("TokenConsumptionNode")
        self.database_service = DatabaseService()
    
    def process(self, shared: SharedState) -> Optional[Dict[str, Any]]:
        """Consume tokens after successful action execution."""
        logger = get_logger("TokenConsumptionNode")
        
        # Tokens are deprecated - no consumption needed
        logger.info("Token consumption skipped - tokens system deprecated")
        
        return {
            "tokens_consumed": 0,
            "tokens_remaining": 0,
            "user_has_tokens": False
        }


class FlowRoutingNode:
    """Node that routes flows based on user status and token availability."""
    
    def __init__(self):
        self.logger = get_logger("FlowRoutingNode")
    
    def process(self, shared: SharedState) -> Optional[Dict[str, Any]]:
        """Route the flow based on user status and token availability."""
        logger = get_logger("FlowRoutingNode")
        
        flow_type = shared.get("flow_type", "user")
        
        # All users get the same flow type since tokens are deprecated
        logger.info(f"Routing flow. Type: {flow_type} - tokens system deprecated")
        
        return {
            "flow_type": flow_type,
            "user_has_tokens": False,
            "tokens_remaining": 0
        } 