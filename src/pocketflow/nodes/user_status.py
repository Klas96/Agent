"""
User status and token management nodes.

This module provides nodes for checking user token status and managing
different user states (tokened vs tokenless).
"""

from typing import Optional, Dict, Any
from ..core.node import SimpleNode
from ..core.types import SharedState, FlowType
from ..utils.logging import get_logger


class UserStatusCheckNode(SimpleNode):
    """Node that checks user token status and determines flow type."""
    
    def process(self, shared: SharedState) -> Optional[Dict[str, Any]]:
        """Check user token status and set flow type."""
        logger = get_logger("UserStatusCheckNode")
        user_email = shared.get("user")
        
        if not user_email:
            logger.warning("No user email found in shared state")
            return {"user_has_tokens": False, "flow_type": FlowType.TOKENLESS_USER.value}
        
        # TODO: Replace with actual database query
        # For now, simulate token check
        tokens_remaining = self._check_user_tokens(user_email)
        user_has_tokens = tokens_remaining > 0
        
        logger.info(f"User {user_email} has {tokens_remaining} tokens remaining")
        
        # Determine flow type
        if user_has_tokens:
            flow_type = FlowType.TOKENED_USER.value
        else:
            flow_type = FlowType.TOKENLESS_USER.value
        
        return {
            "tokens_remaining": tokens_remaining,
            "user_has_tokens": user_has_tokens,
            "flow_type": flow_type
        }
    
    def _check_user_tokens(self, user_email: str) -> int:
        """Check how many tokens a user has remaining."""
        # TODO: Implement actual database query
        # This is a placeholder implementation
        import random
        return random.choice([0, 5, 10, 15])


class TokenValidationNode(SimpleNode):
    """Node that validates if user has sufficient tokens for requested action."""
    
    def process(self, shared: SharedState) -> Optional[Dict[str, Any]]:
        """Validate token requirements for the requested action."""
        logger = get_logger("TokenValidationNode")
        
        tokens_remaining = shared.get("tokens_remaining", 0)
        action = shared.get("action")
        
        if not action:
            logger.warning("No action specified for token validation")
            return {"token_validation": "no_action"}
        
        # Define token costs for different actions
        token_costs = {
            "generate": 1,
            "investigate": 1,
            "send": 0,  # Sending emails is free
        }
        
        cost = token_costs.get(action, 0)
        
        if tokens_remaining >= cost:
            logger.info(f"Token validation passed. Cost: {cost}, Remaining: {tokens_remaining}")
            return {
                "token_validation": "approved",
                "tokens_consumed": cost,
                "tokens_remaining": tokens_remaining - cost
            }
        else:
            logger.warning(f"Token validation failed. Required: {cost}, Available: {tokens_remaining}")
            return {
                "token_validation": "insufficient",
                "required_tokens": cost,
                "available_tokens": tokens_remaining
            }


class PaymentRequestNode(SimpleNode):
    """Node that handles payment requests for tokenless users."""
    
    def process(self, shared: SharedState) -> Optional[Dict[str, Any]]:
        """Generate payment request for tokenless users."""
        logger = get_logger("PaymentRequestNode")
        
        user_email = shared.get("user")
        action = shared.get("action")
        
        if not user_email:
            logger.error("No user email for payment request")
            return None
        
        # Get or create Bitcoin address for user
        btc_address = shared.get("btc_address")
        if not btc_address:
            btc_address = self._get_or_create_btc_address(user_email)
        
        # Calculate payment amount based on action
        payment_amount = self._calculate_payment_amount(action)
        
        logger.info(f"Creating payment request for {user_email}: ${payment_amount}")
        
        return {
            "payment_request": {
                "amount_usd": payment_amount,
                "user_email": user_email,
                "btc_address": btc_address,
                "description": f"Payment for {action} action"
            },
            "btc_address": btc_address,
            "flow_type": FlowType.PAYMENT_PENDING.value
        }
    
    def _get_or_create_btc_address(self, user_email: str) -> str:
        """Get or create a Bitcoin address for the user."""
        # TODO: Implement actual Bitcoin address management
        # This is a placeholder implementation
        import hashlib
        address_hash = hashlib.md5(user_email.encode()).hexdigest()[:34]
        return f"bc1{address_hash}"
    
    def _calculate_payment_amount(self, action: str) -> float:
        """Calculate payment amount based on action type."""
        # TODO: Implement actual pricing logic
        base_prices = {
            "generate": 0.10,
            "investigate": 0.05,
            "send": 0.00,  # Free
        }
        return base_prices.get(action, 0.10)


class TokenConsumptionNode(SimpleNode):
    """Node that consumes tokens after successful actions."""
    
    def process(self, shared: SharedState) -> Optional[Dict[str, Any]]:
        """Consume tokens after successful action execution."""
        logger = get_logger("TokenConsumptionNode")
        
        tokens_consumed = shared.get("tokens_consumed", 0)
        user_email = shared.get("user")
        
        if tokens_consumed <= 0:
            logger.info("No tokens to consume")
            return None
        
        if not user_email:
            logger.error("No user email for token consumption")
            return None
        
        # TODO: Implement actual token consumption in database
        logger.info(f"Consuming {tokens_consumed} tokens for user {user_email}")
        
        # Update remaining tokens
        current_tokens = shared.get("tokens_remaining", 0)
        new_tokens = max(0, current_tokens - tokens_consumed)
        
        return {
            "tokens_remaining": new_tokens,
            "user_has_tokens": new_tokens > 0
        }


class FlowTypeRouterNode(SimpleNode):
    """Node that routes to different flows based on user status."""
    
    def process(self, shared: SharedState) -> Optional[Dict[str, Any]]:
        """Route to appropriate flow based on user status."""
        logger = get_logger("FlowTypeRouterNode")
        
        flow_type = shared.get("flow_type")
        user_has_tokens = shared.get("user_has_tokens", False)
        tokens_remaining = shared.get("tokens_remaining", 0)
        
        logger.info(f"Routing flow. Type: {flow_type}, Has tokens: {user_has_tokens}, Remaining: {tokens_remaining}")
        
        # Determine routing decision
        if user_has_tokens and tokens_remaining > 0:
            routing_decision = "tokened_flow"
        elif not user_has_tokens:
            routing_decision = "tokenless_flow"
        else:
            routing_decision = "payment_required"
        
        return {
            "routing_decision": routing_decision,
            "flow_type": flow_type
        } 