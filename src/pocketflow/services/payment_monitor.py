"""
Payment monitoring service for PocketFlow.

This module monitors Bitcoin payments and automatically assigns tokens to users.
"""

import logging
import time
import json
import subprocess
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta

from ..config.settings import get_settings
from ..services.database_service import DatabaseService
from ..utils.electrum_utils import get_wallet_addresses
# PaymentError not needed - using generic exceptions

logger = logging.getLogger(__name__)

class PaymentMonitor:
    """Service for monitoring Bitcoin payments and assigning tokens."""
    
    def __init__(self):
        """Initialize the payment monitor."""
        self.settings = get_settings()
        self.db = DatabaseService()
        self.last_check_time = None
        self.address_to_user_map = {}
        self.logger = logging.getLogger(__name__)
        
    def get_wallet_balance(self) -> Dict[str, str]:
        """Get the current wallet balance."""
        try:
            result = subprocess.run([
                "/opt/pocketflow/venv/bin/electrum",
                "-D", "/opt/pocketflow/.electrum",
                "--wallet", "/opt/pocketflow/.electrum/wallets/user_wallet",
                "getbalance",
                "--offline"
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                balance_data = json.loads(result.stdout.strip())
                return balance_data
            else:
                logger.error(f"Failed to get wallet balance: {result.stderr}")
                return {"confirmed": "0", "unconfirmed": "0"}
                
        except Exception as e:
            logger.error(f"Error getting wallet balance: {e}")
            return {"confirmed": "0", "unconfirmed": "0"}
    
    def get_address_balance(self, address: str) -> float:
        """Get the balance for a specific address."""
        try:
            result = subprocess.run([
                "/opt/pocketflow/venv/bin/electrum",
                "-D", "/opt/pocketflow/.electrum",
                "--wallet", "/opt/pocketflow/.electrum/wallets/user_wallet",
                "getaddressbalance",
                address,
                "--offline"
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                balance_data = json.loads(result.stdout.strip())
                confirmed = float(balance_data.get("confirmed", "0"))
                unconfirmed = float(balance_data.get("unconfirmed", "0"))
                return confirmed + unconfirmed
            else:
                logger.error(f"Failed to get address balance for {address}: {result.stderr}")
                return 0.0
                
        except Exception as e:
            logger.error(f"Error getting address balance for {address}: {e}")
            return 0.0
    
    def load_address_mappings(self):
        """Load the mapping of Bitcoin addresses to users from the database."""
        try:
            # Get all users and their assigned Bitcoin addresses
            users = self.db.get_all_users()
            for user in users:
                if user.get('btc_address'):
                    self.address_to_user_map[user['btc_address']] = {
                        'user_id': user['id'],
                        'email': user['email'],
                        'current_tokens': user.get('tokens', 0)
                    }
            
            logger.info(f"Loaded {len(self.address_to_user_map)} address mappings")
            
        except Exception as e:
            logger.error(f"Error loading address mappings: {e}")
    
    def check_for_payments(self) -> List[Dict]:
        """Check for new payments and return list of new payments."""
        new_payments = []
        
        try:
            # Reload address mappings to get latest data
            self.load_address_mappings()
            
            # Check each address for new payments
            for address, user_info in self.address_to_user_map.items():
                current_balance = self.get_address_balance(address)
                
                # Get the last known balance for this address
                last_balance = self.db.get_address_last_balance(address)
                
                if current_balance > last_balance:
                    payment_amount = current_balance - last_balance
                    
                    # Calculate tokens based on payment amount (1 token = 0.0001 BTC)
                    tokens_to_add = int(payment_amount / 0.0001)
                    
                    if tokens_to_add > 0:
                        payment_info = {
                            'address': address,
                            'user_id': user_info['user_id'],
                            'email': user_info['email'],
                            'payment_amount': payment_amount,
                            'tokens_added': tokens_to_add,
                            'timestamp': datetime.now()
                        }
                        
                        new_payments.append(payment_info)
                        logger.info(f"New payment detected: {payment_amount} BTC -> {tokens_to_add} tokens for {user_info['email']}")
            
            return new_payments
            
        except Exception as e:
            logger.error(f"Error checking for payments: {e}")
            return []
    
    def process_payments(self, payments: List[Dict]):
        """Process new payments and assign tokens to users."""
        for payment in payments:
            try:
                # Update user's token balance
                new_balance = self.db.add_tokens_to_user(
                    payment['user_id'], 
                    payment['tokens_added']
                )
                
                # Update the last known balance for this address
                self.db.update_address_balance(
                    payment['address'],
                    self.get_address_balance(payment['address'])
                )
                
                # Log the payment
                self.db.log_payment(
                    user_id=payment['user_id'],
                    address=payment['address'],
                    amount=payment['payment_amount'],
                    tokens_added=payment['tokens_added']
                )
                
                logger.info(f"Processed payment: {payment['email']} received {payment['tokens_added']} tokens")
                
            except Exception as e:
                logger.error(f"Error processing payment for {payment['email']}: {e}")
    
    def run_monitoring_cycle(self):
        """Run one cycle of payment monitoring."""
        try:
            logger.info("Starting payment monitoring cycle")
            
            # Check for new payments
            new_payments = self.check_for_payments()
            
            if new_payments:
                # Process the payments
                self.process_payments(new_payments)
                logger.info(f"Processed {len(new_payments)} new payments")
            else:
                logger.info("No new payments detected")
                
        except Exception as e:
            logger.error(f"Error in payment monitoring cycle: {e}")
    
    def start_monitoring(self, interval_seconds: int = 300):
        """Start continuous payment monitoring."""
        logger.info(f"Starting payment monitoring with {interval_seconds}s intervals")
        
        while True:
            try:
                self.run_monitoring_cycle()
                time.sleep(interval_seconds)
                
            except KeyboardInterrupt:
                logger.info("Payment monitoring stopped by user")
                break
            except Exception as e:
                logger.error(f"Error in payment monitoring: {e}")
                time.sleep(interval_seconds) 