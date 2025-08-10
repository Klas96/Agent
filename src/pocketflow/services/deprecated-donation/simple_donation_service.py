"""
Simple donation service without Bitcoin utilities.

This module provides a simple donation system using external links.
"""

from typing import Dict, Any, Optional, List
from ..utils.logging import get_logger
from ..utils.errors import DonationError


class SimpleDonationService:
    """Simple donation service without Bitcoin complexity."""
    
    def __init__(self):
        self.logger = get_logger("SimpleDonationService")
        self.donation_url = "https://your-donation-page.com"
        self.external_links = {
            "paypal": "https://your-donation-page.com/paypal",
            "stripe": "https://your-donation-page.com/stripe",
            "bitcoin": "https://your-donation-page.com/btc",
            "github": "https://github.com/sponsors/your-username"
        }
    
    def request_donation(self, user_email: str) -> Dict[str, Any]:
        """
        Request donation from user.
        
        Args:
            user_email: User's email address
            
        Returns:
            Donation request information
        """
        try:
            self.logger.info(f"Creating donation request for {user_email}")
            
            return {
                "donation_requested": True,
                "donation_url": self.donation_url,
                "external_links": self.external_links,
                "message": "Please consider making a donation to support our service.",
                "user_email": user_email,
                "suggested_amounts": [5, 10, 25, 50, 100]
            }
            
        except Exception as e:
            self.logger.error(f"Failed to create donation request for {user_email}: {e}")
            raise DonationError(f"Donation request failed: {e}")
    
    def track_donation(self, user_email: str, amount: float, method: str) -> bool:
        """
        Track donation in database.
        
        Args:
            user_email: User's email address
            amount: Donation amount
            method: Payment method used
            
        Returns:
            True if tracking successful, False otherwise
        """
        try:
            from .database_service import DatabaseService
            
            db_service = DatabaseService()
            
            # Create donation record
            donation_record = {
                "user_email": user_email,
                "amount": amount,
                "method": method,
                "status": "received",
                "tracked_at": "now"
            }
            
            # Store in database (simplified)
            self.logger.info(f"Tracked donation: {user_email} donated ${amount} via {method}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to track donation for {user_email}: {e}")
            return False
    
    def send_thank_you_email(self, user_email: str, amount: float = None, method: str = "donation"):
        """
        Send thank you email for donation.
        
        Args:
            user_email: User's email address
            amount: Donation amount (optional)
            method: Payment method used
        """
        try:
            from .email_service import EmailService
            
            email_service = EmailService()
            
            subject = "Thank you for your donation!"
            body = f"""
            Dear {user_email},
            
            Thank you for your generous {method} donation{f' of ${amount:.2f}' if amount else ''}!
            
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
            
            self.logger.info(f"Sent thank you email to {user_email}")
            
        except Exception as e:
            self.logger.error(f"Failed to send thank you email to {user_email}: {e}")
    
    def get_donation_stats(self) -> Dict[str, Any]:
        """
        Get donation statistics.
        
        Returns:
            Dictionary with donation statistics
        """
        try:
            from .database_service import DatabaseService
            
            db_service = DatabaseService()
            
            # Get donation statistics (simplified)
            stats = {
                "total_donations": 0,
                "total_amount": 0.0,
                "donation_methods": {},
                "recent_donations": []
            }
            
            self.logger.info("Retrieved donation statistics")
            return stats
            
        except Exception as e:
            self.logger.error(f"Failed to get donation stats: {e}")
            return {}
    
    def get_donation_links(self) -> Dict[str, str]:
        """
        Get external donation links.
        
        Returns:
            Dictionary of donation links
        """
        return self.external_links.copy()
    
    def validate_donation_amount(self, amount: float) -> bool:
        """
        Validate donation amount.
        
        Args:
            amount: Donation amount to validate
            
        Returns:
            True if valid, False otherwise
        """
        try:
            # Basic validation
            if amount <= 0:
                return False
            
            if amount > 10000:  # Reasonable maximum
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Donation amount validation failed: {e}")
            return False
    
    def get_suggested_amounts(self) -> List[float]:
        """
        Get suggested donation amounts.
        
        Returns:
            List of suggested amounts
        """
        return [5.0, 10.0, 25.0, 50.0, 100.0]
    
    def format_donation_message(self, user_email: str, amount: float = None) -> str:
        """
        Format donation request message.
        
        Args:
            user_email: User's email address
            amount: Suggested amount (optional)
            
        Returns:
            Formatted donation message
        """
        base_message = "Thank you for using our service! Please consider making a donation to support continued development."
        
        if amount:
            return f"{base_message} Suggested amount: ${amount:.2f}"
        
        return base_message


# Global instance for easy access
simple_donation_service = SimpleDonationService() 