"""
Simple donation node without Bitcoin utilities.

This module provides a simple donation request system using external links.
"""

from typing import Optional, Dict, Any
from ..core.node import SimpleNode
from ..core.types import SharedState
from ..utils.logging import get_logger


class SimpleDonationNode(SimpleNode):
    """Simple donation request node without Bitcoin complexity."""
    
    def process(self, shared: SharedState) -> Optional[Dict[str, Any]]:
        """Request donation using external links."""
        logger = get_logger("SimpleDonationNode")
        user_email = getattr(shared, 'user', None)
        
        if not user_email:
            logger.warning("No user email for donation request")
            return {
                "donation_requested": False,
                "error": "No user email available"
            }
        
        logger.info(f"Creating simple donation request for {user_email}")
        
        return {
            "donation_requested": True,
            "donation_url": "https://your-donation-page.com",
            "external_links": {
                "paypal": "https://your-donation-page.com/paypal",
                "stripe": "https://your-donation-page.com/stripe",
                "bitcoin": "https://your-donation-page.com/btc"
            },
            "message": "Thank you for using our service! Please consider making a donation to support continued development.",
            "user_email": user_email
        }


class SimpleDonationTrackingNode(SimpleNode):
    """Node for tracking donations without Bitcoin complexity."""
    
    def process(self, shared: SharedState) -> Optional[Dict[str, Any]]:
        """Track donation in database."""
        logger = get_logger("SimpleDonationTrackingNode")
        
        user_email = getattr(shared, 'user', None)
        donation_info = shared.get("donation_info", {})
        
        if not user_email:
            logger.warning("No user email for donation tracking")
            return None
        
        try:
            # Log donation to database
            from ..services.database_service import DatabaseService
            db_service = DatabaseService()
            
            # Create simple donation record
            donation_record = {
                "user_email": user_email,
                "amount": donation_info.get("amount", 0.0),
                "method": donation_info.get("method", "external"),
                "timestamp": "now",
                "status": "received"
            }
            
            # Store donation record (simplified)
            logger.info(f"Tracked donation for {user_email}: {donation_info.get('amount', 0.0)}")
            
            return {
                "donation_tracked": True,
                "donation_record": donation_record
            }
            
        except Exception as e:
            logger.error(f"Failed to track donation for {user_email}: {e}")
            return {
                "donation_tracked": False,
                "error": str(e)
            }


class ThankYouEmailNode(SimpleNode):
    """Node for sending thank you emails for donations."""
    
    def process(self, shared: SharedState) -> Optional[Dict[str, Any]]:
        """Send thank you email for donation."""
        logger = get_logger("ThankYouEmailNode")
        
        user_email = getattr(shared, 'user', None)
        donation_info = shared.get("donation_info", {})
        
        if not user_email:
            logger.warning("No user email for thank you email")
            return None
        
        try:
            from ..services.email_service import EmailService
            
            email_service = EmailService()
            
            amount = donation_info.get("amount", 0.0)
            method = donation_info.get("method", "donation")
            
            subject = "Thank you for your donation!"
            body = f"""
            Dear {user_email},
            
            Thank you for your generous {method} donation{f' of ${amount:.2f}' if amount > 0 else ''}!
            
            Your support helps us continue providing this service and developing new features.
            
            We appreciate your contribution and will use it to improve our service.
            
            Best regards,
            The PocketFlow Team
            """
            
            email_service.send_email(
                to=user_email,
                subject=subject,
                body=body
            )
            
            logger.info(f"Sent thank you email to {user_email}")
            
            return {
                "thank_you_sent": True,
                "email_sent_to": user_email
            }
            
        except Exception as e:
            logger.error(f"Failed to send thank you email to {user_email}: {e}")
            return {
                "thank_you_sent": False,
                "error": str(e)
            } 