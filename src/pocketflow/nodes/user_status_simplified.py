"""
Simplified user status management for donation-only model.

This module provides nodes for checking user status without token management.
"""

from typing import Optional, Dict, Any
from ..core.node import SimpleNode
from ..core.types import SharedState, FlowType
from ..utils.logging import get_logger
from ..services import database_service


class UserStatusCheckNode(SimpleNode):
    """Node that checks user status (simplified for donation-only)."""
    
    def process(self, shared: SharedState) -> Optional[Dict[str, Any]]:
        """Check user status and set flow type."""
        logger = get_logger("UserStatusCheckNode")
        user_email = getattr(shared, 'user', None)
        
        if not user_email:
            logger.warning("No user email found in shared state")
            return {"flow_type": FlowType.USER.value}
        
        # All users get the same flow type - donation-based
        logger.info(f"User {user_email} - using donation flow")
        
        return {
            "flow_type": FlowType.USER.value,
            "user_email": user_email
        }


class DonationRequestNode(SimpleNode):
    """Node that requests donations from users."""
    
    def process(self, shared: SharedState) -> Optional[Dict[str, Any]]:
        """Request donation and provide payment instructions."""
        logger = get_logger("DonationRequestNode")
        user_email = getattr(shared, 'user', None)
        
        if not user_email:
            logger.warning("No user email for donation request")
            return {
                "donation_requested": False,
                "error": "No user email available"
            }
        
        # Get or create user and Bitcoin address
        try:
            db_service = database_service.DatabaseService()
            
            # Get or create user
            user = db_service.get_user(user_email)
            if not user:
                user = db_service.create_user(user_email)
            
            # Get or create Bitcoin address for user
            btc_address = getattr(shared, 'btc_address', None)
            if not btc_address:
                btc_address = self._get_or_create_btc_address(user_email)
            
            # Save the Bitcoin address to the user's record
            if btc_address and user:
                db_service.update_user_btc_address(user['id'], btc_address)
                logger.info(f"Updated BTC address for user {user_email}: {btc_address}")
            
        except Exception as e:
            logger.error(f"Failed to get/create BTC address for {user_email}: {e}")
            return {
                "error": "Bitcoin donation system unavailable - cannot process donation",
                "flow_type": "error",
                "message": "Donation system is currently unavailable. Please try again later or contact support."
            }
        
        # Check if we got a valid address
        if not btc_address:
            logger.error(f"Failed to get/create BTC address for {user_email}")
            return {
                "error": "Failed to generate Bitcoin address",
                "flow_type": "error",
                "message": "Unable to generate donation address. Please try again later."
            }
        
        logger.info(f"Creating donation request for {user_email}")
        
        return {
            "donation_requested": True,
            "btc_address": btc_address,
            "user_email": user_email,
            "message": "Thank you for using our service! Please consider making a donation to support continued development.",
            "suggested_amount": "0.001 BTC"
        }
    
    def _get_or_create_btc_address(self, user_email: str) -> Optional[str]:
        """Get or create a Bitcoin address for the user."""
        try:
            from ..utils.electrum_utils import get_wallet_addresses, create_new_address
            
            # Try to get existing addresses first
            wallet_addresses = get_wallet_addresses()
            if wallet_addresses:
                # Use the first available address
                address = wallet_addresses[0]
                logger = get_logger("DonationRequestNode")
                logger.info(f"Using existing wallet address: {address}")
                return address
            
            # Create new address if none available
            new_address = create_new_address()
            if new_address:
                logger = get_logger("DonationRequestNode")
                logger.info(f"Created new wallet address: {new_address}")
                return new_address
            
            return None
            
        except Exception as e:
            logger = get_logger("DonationRequestNode")
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
            
            # CRITICAL: Do not generate fake addresses - this is fraudulent
            # Instead, raise an exception to prevent donation processing
            logger.error(f"Cannot generate real BTC address for {user_email} - donation system unavailable")
            raise Exception("Bitcoin donation system unavailable - cannot generate real addresses")


class FlowTypeRouterNode(SimpleNode):
    """Node that routes to different flows based on user status."""
    
    def process(self, shared: SharedState) -> Optional[Dict[str, Any]]:
        """Route to appropriate flow based on user status."""
        logger = get_logger("FlowTypeRouterNode")
        
        flow_type = shared.get("flow_type")
        
        logger.info(f"Routing flow. Type: {flow_type}")
        
        # All users get the same routing decision
        routing_decision = "donation_flow"
        
        return {
            "routing_decision": routing_decision,
            "flow_type": flow_type
        } 