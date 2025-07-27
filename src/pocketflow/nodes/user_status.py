"""
User status and token management nodes.

This module provides nodes for checking user token status and managing
different user states (tokened vs tokenless).
"""

from typing import Optional, Dict, Any
from ..core.node import SimpleNode
from ..core.types import SharedState, FlowType
from ..utils.logging import get_logger
from ..services import database_service


class UserStatusCheckNode(SimpleNode):
    """Node that checks user token status and determines flow type."""
    
    def process(self, shared: SharedState) -> Optional[Dict[str, Any]]:
        """Check user token status and set flow type."""
        logger = get_logger("UserStatusCheckNode")
        user_email = getattr(shared, 'user', None)
        
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
        try:
            return database_service.get_tokens(user_email)
        except Exception as e:
            logger = get_logger("UserStatusCheckNode")
            logger.error(f"Failed to check tokens for {user_email}: {e}")
            return 0


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
        
        # Extract user email from the email data
        user_email = None
        if hasattr(shared, 'email') and shared.email:
            from_field = shared.email.get("from", "")
            if "<" in from_field and ">" in from_field:
                user_email = from_field.split("<")[1].split(">")[0]
            else:
                user_email = from_field
        
        # If no email found, try to get from agent_action parameters
        if not user_email and hasattr(shared, 'agent_action') and shared.agent_action:
            # Try to extract from the 'to' field in agent_action parameters
            agent_params = shared.agent_action.get("parameters", {})
            to_field = agent_params.get("to", "")
            if to_field and to_field != "{sender_email}":
                user_email = to_field
        
        # Get action from agent_action
        action = None
        if hasattr(shared, 'agent_action') and shared.agent_action:
            action = shared.agent_action.get("action")
        
        if not user_email:
            logger.error("No user email for payment request")
            return None
        
        # Get or create Bitcoin address for user
        btc_address = getattr(shared, 'btc_address', None)
        if not btc_address:
            btc_address = self._get_or_create_btc_address(user_email)
        
        # Check if we got a valid address
        if not btc_address:
            logger.error(f"Failed to get/create BTC address for {user_email}")
            return {
                "error": "Failed to generate Bitcoin address",
                "flow_type": "error"
            }
        
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
            "btc_address": btc_address
            # Don't change flow_type - keep it as tokenless_user
        }
    
    def _get_or_create_btc_address(self, user_email: str) -> str:
        """Get or create a Bitcoin address for the user."""
        try:
            # Instantiate database service
            db_service = database_service.DatabaseService()
            
            # Check if user already has a BTC address
            addresses = db_service.get_btc_addresses(user_email)
            if addresses:
                return addresses[0]  # Return the first address
            
            # Generate new address using Electrum wallet
            from ..utils.electrum_utils import get_new_btc_address
            new_address = get_new_btc_address()
            
            if new_address:
                # Store the new address
                db_service.add_btc_address(user_email, new_address)
                return new_address
            else:
                raise Exception("Failed to generate new BTC address from wallet")
            
        except Exception as e:
            logger = get_logger("PaymentRequestNode")
            logger.error(f"Failed to get/create BTC address for {user_email}: {e}")
            # Fallback: try to get an existing address from wallet
            try:
                from ..utils.electrum_utils import get_wallet_addresses
                wallet_addresses = get_wallet_addresses()
                if wallet_addresses:
                    # Use the first available address from wallet
                    fallback_address = wallet_addresses[0]
                    db_service = database_service.DatabaseService()
                    db_service.add_btc_address(user_email, fallback_address)
                    logger.info(f"Using fallback address from wallet: {fallback_address}")
                    return fallback_address
            except Exception as fallback_error:
                logger.error(f"Fallback address generation failed: {fallback_error}")
            
            # Last resort: generate a simple placeholder address for tokenless users
            # This ensures the flow continues even if Electrum is not available
            import hashlib
            import time
            
            # Create a deterministic but unique address based on user email and timestamp
            unique_string = f"{user_email}_{int(time.time())}"
            hash_obj = hashlib.sha256(unique_string.encode())
            placeholder_address = f"bc1{hash_obj.hexdigest()[:30]}"
            
            logger.info(f"Generated placeholder address for {user_email}: {placeholder_address}")
            return placeholder_address
    
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
        
        try:
            # Consume tokens using database service
            success = database_service.consume_tokens(user_email, tokens_consumed)
            
            if success:
                logger.info(f"Successfully consumed {tokens_consumed} tokens for {user_email}")
                # Update remaining tokens
                current_tokens = shared.get("tokens_remaining", 0)
                new_tokens = max(0, current_tokens - tokens_consumed)
                
                return {
                    "tokens_remaining": new_tokens,
                    "user_has_tokens": new_tokens > 0,
                    "token_consumption": "success"
                }
            else:
                logger.warning(f"Failed to consume {tokens_consumed} tokens for {user_email}")
                return {
                    "token_consumption": "failed",
                    "error": "Insufficient tokens"
                }
                
        except Exception as e:
            logger.error(f"Error consuming tokens for {user_email}: {e}")
            return {
                "token_consumption": "error",
                "error": str(e)
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