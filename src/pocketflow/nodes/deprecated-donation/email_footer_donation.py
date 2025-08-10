"""
Email footer donation system.

This module adds a simple donation address footer to every email.
"""

from typing import Optional, Dict, Any
from ..core.node import SimpleNode
from ..core.types import SharedState
from ..utils.logging import get_logger


class EmailFooterDonationNode(SimpleNode):
    """Node that adds donation address footer to emails."""
    
    def __init__(self):
        super().__init__()
        self.donation_address = "bc1q88na538qmsac5tp6hdn7pc53eegwy758usez99"  # Your actual address
        self.donation_message = "Support through BTC: "
    
    def process(self, shared: SharedState) -> Optional[Dict[str, Any]]:
        """Add donation footer to email."""
        logger = get_logger("EmailFooterDonationNode")
        
        # Get the email body from shared state
        email_body = shared.get("reply_body", "")
        
        if not email_body:
            logger.warning("No email body found for donation footer")
            return None
        
        # Create donation footer
        donation_footer = self._create_donation_footer()
        
        # Add footer to email body
        updated_body = f"{email_body}\n\n{donation_footer}"
        
        logger.info("Added donation footer to email")
        
        return {
            "reply_body": updated_body,
            "donation_footer_added": True,
            "donation_address": self.donation_address
        }
    
    def _create_donation_footer(self) -> str:
        """Create donation footer text."""
        return f"""
---
{self.donation_message} {self.donation_address}
Thank you for using our service!
        """.strip()


class ConfigurableDonationFooterNode(SimpleNode):
    """Node that adds configurable donation footer to emails."""
    
    def __init__(self, donation_address: str = None, donation_message: str = None):
        super().__init__()
        self.donation_address = donation_address or "bc1q88na538qmsac5tp6hdn7pc53eegwy758usez99"
        self.donation_message = donation_message or "Support through BTC: "
    
    def process(self, shared: SharedState) -> Optional[Dict[str, Any]]:
        """Add configurable donation footer to email."""
        logger = get_logger("ConfigurableDonationFooterNode")
        
        # Get the email body from shared state
        email_body = shared.get("reply_body", "")
        
        if not email_body:
            logger.warning("No email body found for donation footer")
            return None
        
        # Create donation footer
        donation_footer = self._create_donation_footer()
        
        # Add footer to email body
        updated_body = f"{email_body}\n\n{donation_footer}"
        
        logger.info(f"Added donation footer with address: {self.donation_address}")
        
        return {
            "reply_body": updated_body,
            "donation_footer_added": True,
            "donation_address": self.donation_address,
            "donation_message": self.donation_message
        }
    
    def _create_donation_footer(self) -> str:
        """Create donation footer text."""
        return f"""
---
{self.donation_message} {self.donation_address}
Thank you for using our service!
        """.strip()


class MultiMethodDonationFooterNode(SimpleNode):
    """Node that adds multiple donation methods to email footer."""
    
    def __init__(self):
        super().__init__()
        self.donation_methods = {
            "bitcoin": "bc1q88na538qmsac5tp6hdn7pc53eegwy758usez99",
            "paypal": "https://paypal.me/yourusername",
            "github": "https://github.com/sponsors/yourusername",
            "stripe": "https://buy.stripe.com/yourlink"
        }
    
    def process(self, shared: SharedState) -> Optional[Dict[str, Any]]:
        """Add multi-method donation footer to email."""
        logger = get_logger("MultiMethodDonationFooterNode")
        
        # Get the email body from shared state
        email_body = shared.get("reply_body", "")
        
        if not email_body:
            logger.warning("No email body found for donation footer")
            return None
        
        # Create donation footer
        donation_footer = self._create_donation_footer()
        
        # Add footer to email body
        updated_body = f"{email_body}\n\n{donation_footer}"
        
        logger.info("Added multi-method donation footer to email")
        
        return {
            "reply_body": updated_body,
            "donation_footer_added": True,
            "donation_methods": self.donation_methods
        }
    
    def _create_donation_footer(self) -> str:
        """Create multi-method donation footer text."""
        footer_lines = [
            "---",
            "Support through BTC:",
            f"Bitcoin: {self.donation_methods['bitcoin']}",
            f"PayPal: {self.donation_methods['paypal']}",
            f"GitHub Sponsors: {self.donation_methods['github']}",
            f"Credit Card: {self.donation_methods['stripe']}",
            "Thank you for using our service!"
        ]
        
        return "\n".join(footer_lines)


class SimpleDonationFooterNode(SimpleNode):
    """Simple donation footer node with minimal text."""
    
    def __init__(self, donation_address: str = None):
        super().__init__()
        self.donation_address = donation_address or "bc1q88na538qmsac5tp6hdn7pc53eegwy758usez99"
    
    def process(self, shared: SharedState) -> Optional[Dict[str, Any]]:
        """Add simple donation footer to email."""
        logger = get_logger("SimpleDonationFooterNode")
        
        # Get the email body from shared state
        email_body = shared.get("reply_body", "")
        
        if not email_body:
            logger.warning("No email body found for donation footer")
            return None
        
        # Create simple donation footer
        donation_footer = f"\n\n---\nSupport through BTC: {self.donation_address}"
        
        # Add footer to email body
        updated_body = f"{email_body}{donation_footer}"
        
        logger.info(f"Added simple donation footer with address: {self.donation_address}")
        
        return {
            "reply_body": updated_body,
            "donation_footer_added": True,
            "donation_address": self.donation_address
        } 