"""
Donation monitor for PocketFlow.

This module monitors Bitcoin donations without token conversion.
"""

import sqlite3
import time
from datetime import datetime
from typing import List, Dict, Any, Optional
from ..utils.logging import get_logger
from ..services.database_service import DatabaseService


class DonationMonitor:
    """Monitor for Bitcoin donations (no token conversion)."""
    
    def __init__(self, db_path: str = None):
        self.logger = get_logger("DonationMonitor")
        self.db = DatabaseService()
        self.address_to_user_map = {}
        self.load_address_mappings()
    
    def load_address_mappings(self):
        """Load address to user mappings from database."""
        try:
            addresses = self.db.get_all_btc_addresses()
            for address_info in addresses:
                email = address_info.get('email')
                address = address_info.get('address')
                if email and address:
                    self.address_to_user_map[address] = {
                        'email': email,
                        'user_id': address_info.get('user_id')
                    }
            
            self.logger.info(f"Loaded {len(self.address_to_user_map)} address mappings")
            
        except Exception as e:
            self.logger.error(f"Failed to load address mappings: {e}")
    
    def get_address_balance(self, address: str) -> float:
        """Get current balance for a Bitcoin address."""
        try:
            # Use simplified Bitcoin utilities
            from ..utils.simple_bitcoin_utils import simple_bitcoin_utils
            return simple_bitcoin_utils.check_address_balance(address)
        except Exception as e:
            self.logger.error(f"Failed to get balance for {address}: {e}")
            return 0.0
    
    def check_for_donations(self) -> List[Dict]:
        """Check for new donations and return list of new donations."""
        new_donations = []
        
        try:
            # Reload address mappings to get latest data
            self.load_address_mappings()
            
            # Check each address for new donations
            for address, user_info in self.address_to_user_map.items():
                current_balance = self.get_address_balance(address)
                
                # Get the last known balance for this address
                last_balance = self.db.get_address_last_balance(address)
                
                if current_balance > last_balance:
                    donation_amount = current_balance - last_balance
                    
                    donation_info = {
                        'address': address,
                        'user_id': user_info['user_id'],
                        'email': user_info['email'],
                        'donation_amount': donation_amount,
                        'timestamp': datetime.now()
                    }
                    
                    new_donations.append(donation_info)
                    self.logger.info(f"New donation detected: {donation_amount} BTC for {user_info['email']}")
            
            return new_donations
            
        except Exception as e:
            self.logger.error(f"Error checking for donations: {e}")
            return []
    
    def process_donations(self, donations: List[Dict]):
        """Process new donations (no token conversion)."""
        for donation in donations:
            try:
                # Log the donation
                self.db.log_donation(
                    user_id=donation['user_id'],
                    address=donation['address'],
                    amount=donation['donation_amount']
                )
                
                # Update the last known balance for this address
                self.db.update_address_balance(
                    donation['address'],
                    self.get_address_balance(donation['address'])
                )
                
                # Send thank you email
                self._send_thank_you_email(donation)
                
                self.logger.info(f"Processed donation: {donation['email']} donated {donation['donation_amount']} BTC")
                
            except Exception as e:
                self.logger.error(f"Error processing donation for {donation['email']}: {e}")
    
    def _send_thank_you_email(self, donation: Dict[str, Any]):
        """Send thank you email for donation."""
        try:
            from ..services.email_service import EmailService
            
            email_service = EmailService()
            
            subject = "Thank you for your donation!"
            body = f"""
            Dear {donation['email']},
            
            Thank you for your generous donation of {donation['donation_amount']} BTC!
            
            Your support helps us continue providing this service and developing new features.
            
            We appreciate your contribution!
            
            Best regards,
            The PocketFlow Team
            """
            
            email_service.send_email(
                to=donation['email'],
                subject=subject,
                body=body
            )
            
            self.logger.info(f"Sent thank you email to {donation['email']}")
            
        except Exception as e:
            self.logger.error(f"Failed to send thank you email to {donation['email']}: {e}")
    
    def run_monitoring_cycle(self):
        """Run one cycle of donation monitoring."""
        try:
            self.logger.info("Starting donation monitoring cycle")
            
            # Check for new donations
            new_donations = self.check_for_donations()
            
            if new_donations:
                # Process the donations
                self.process_donations(new_donations)
                self.logger.info(f"Processed {len(new_donations)} new donations")
            else:
                self.logger.info("No new donations detected")
                
        except Exception as e:
            self.logger.error(f"Error in donation monitoring cycle: {e}")
    
    def start_monitoring(self, interval_seconds: int = 300):
        """Start continuous donation monitoring."""
        self.logger.info(f"Starting donation monitoring (interval: {interval_seconds}s)")
        
        while True:
            try:
                self.run_monitoring_cycle()
                time.sleep(interval_seconds)
            except KeyboardInterrupt:
                self.logger.info("Donation monitoring stopped by user")
                break
            except Exception as e:
                self.logger.error(f"Error in donation monitoring: {e}")
                time.sleep(interval_seconds)


# Global donation monitor instance
donation_monitor = DonationMonitor() 