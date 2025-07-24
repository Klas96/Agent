#!/usr/bin/env python3
"""
Bitcoin Payment Monitoring and Token Crediting System

This module monitors Bitcoin payments and automatically credits tokens to users
when payments are received at their assigned addresses.
"""

import json
import time
import logging
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from decimal import Decimal
import requests

from utils.electrum_utils import call_electrum_rpc, get_btc_usd_price
from utils.user_db import get_user_by_email, update_user_tokens, get_btc_addresses

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
TOKEN_PRICE_USD = 0.01  # $0.01 per token
MIN_CONFIRMATIONS = 1    # Minimum confirmations required
CHECK_INTERVAL = 60      # Check for payments every 60 seconds
DATABASE_PATH = "/opt/pocketflow/data/pocketflow.db"

class BTCPaymentMonitor:
    """Monitors Bitcoin payments and credits tokens automatically."""
    
    def __init__(self):
        self.processed_payments = set()  # Track processed payment IDs
        self.last_check_time = None
        
    def get_wallet_transactions(self) -> List[Dict]:
        """Get recent transactions from Electrum wallet."""
        try:
            # Get recent transactions (last 24 hours)
            since_timestamp = int((datetime.now() - timedelta(hours=24)).timestamp())
            
            result = call_electrum_rpc("listtransactions", [50])  # Get last 50 transactions
            if not result:
                logger.warning("Failed to get wallet transactions")
                return []
                
            # Filter for incoming transactions with sufficient confirmations
            incoming_txs = []
            for tx in result:
                if (tx.get('category') == 'receive' and 
                    tx.get('confirmations', 0) >= MIN_CONFIRMATIONS and
                    tx.get('time', 0) >= since_timestamp):
                    incoming_txs.append(tx)
                    
            logger.info(f"Found {len(incoming_txs)} incoming transactions")
            return incoming_txs
            
        except Exception as e:
            logger.error(f"Error getting wallet transactions: {e}")
            return []
    
    def get_address_user_mapping(self) -> Dict[str, str]:
        """Get mapping of BTC addresses to user emails."""
        try:
            conn = sqlite3.connect(DATABASE_PATH)
            cursor = conn.cursor()
            
            # Get all user BTC addresses
            cursor.execute("""
                SELECT email, btc_address 
                FROM user_btc_addresses 
                WHERE btc_address IS NOT NULL AND btc_address != ''
            """)
            
            mapping = {}
            for email, address in cursor.fetchall():
                if address and address != "None":
                    mapping[address] = email
                    
            conn.close()
            logger.info(f"Found {len(mapping)} address-user mappings")
            return mapping
            
        except Exception as e:
            logger.error(f"Error getting address-user mapping: {e}")
            return {}
    
    def calculate_tokens_from_btc(self, btc_amount: float) -> int:
        """Calculate number of tokens based on BTC amount."""
        try:
            btc_price_usd = get_btc_usd_price()
            if not btc_price_usd:
                logger.error("Failed to get BTC price")
                return 0
                
            usd_amount = btc_amount * btc_price_usd
            tokens = int(usd_amount / TOKEN_PRICE_USD)
            
            logger.info(f"BTC: {btc_amount:.8f}, USD: ${usd_amount:.2f}, Tokens: {tokens}")
            return tokens
            
        except Exception as e:
            logger.error(f"Error calculating tokens: {e}")
            return 0
    
    def credit_tokens_to_user(self, email: str, tokens: int, tx_id: str) -> bool:
        """Credit tokens to user and log the transaction."""
        try:
            # Update user tokens
            success = update_user_tokens(email, tokens)
            if not success:
                logger.error(f"Failed to update tokens for {email}")
                return False
            
            # Log the payment transaction
            conn = sqlite3.connect(DATABASE_PATH)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO btc_payments 
                (email, btc_amount, usd_amount, tokens_credited, tx_id, timestamp)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                email,
                None,  # We'll calculate this later
                None,  # We'll calculate this later  
                tokens,
                tx_id,
                datetime.now().isoformat()
            ))
            
            conn.commit()
            conn.close()
            
            logger.info(f"Credited {tokens} tokens to {email} for transaction {tx_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error crediting tokens to {email}: {e}")
            return False
    
    def process_payment(self, tx: Dict, address_mapping: Dict[str, str]) -> bool:
        """Process a single payment transaction."""
        try:
            tx_id = tx.get('txid')
            address = tx.get('address')
            btc_amount = tx.get('amount', 0)
            
            # Skip if already processed
            if tx_id in self.processed_payments:
                logger.debug(f"Transaction {tx_id} already processed")
                return False
            
            # Find user for this address
            user_email = address_mapping.get(address)
            if not user_email:
                logger.warning(f"No user found for address {address}")
                return False
            
            # Calculate tokens
            tokens = self.calculate_tokens_from_btc(btc_amount)
            if tokens <= 0:
                logger.warning(f"Invalid token calculation for {btc_amount} BTC")
                return False
            
            # Credit tokens
            success = self.credit_tokens_to_user(user_email, tokens, tx_id)
            if success:
                self.processed_payments.add(tx_id)
                logger.info(f"Successfully processed payment: {tx_id} -> {user_email} ({tokens} tokens)")
                return True
            else:
                logger.error(f"Failed to credit tokens for transaction {tx_id}")
                return False
                
        except Exception as e:
            logger.error(f"Error processing payment: {e}")
            return False
    
    def create_payment_tables(self):
        """Create necessary database tables for payment tracking."""
        try:
            conn = sqlite3.connect(DATABASE_PATH)
            cursor = conn.cursor()
            
            # Create BTC payments table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS btc_payments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    email TEXT NOT NULL,
                    btc_amount REAL,
                    usd_amount REAL,
                    tokens_credited INTEGER NOT NULL,
                    tx_id TEXT UNIQUE NOT NULL,
                    timestamp TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create user BTC addresses table if it doesn't exist
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_btc_addresses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    email TEXT UNIQUE NOT NULL,
                    btc_address TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.commit()
            conn.close()
            logger.info("Payment tracking tables created/verified")
            
        except Exception as e:
            logger.error(f"Error creating payment tables: {e}")
    
    def run_monitoring_cycle(self) -> int:
        """Run one monitoring cycle and return number of payments processed."""
        try:
            logger.info("Starting BTC payment monitoring cycle")
            
            # Get recent transactions
            transactions = self.get_wallet_transactions()
            if not transactions:
                return 0
            
            # Get address-user mapping
            address_mapping = self.get_address_user_mapping()
            if not address_mapping:
                logger.warning("No address-user mappings found")
                return 0
            
            # Process each transaction
            processed_count = 0
            for tx in transactions:
                if self.process_payment(tx, address_mapping):
                    processed_count += 1
            
            logger.info(f"Monitoring cycle complete: {processed_count} payments processed")
            return processed_count
            
        except Exception as e:
            logger.error(f"Error in monitoring cycle: {e}")
            return 0
    
    def start_monitoring(self, run_forever: bool = True):
        """Start the payment monitoring system."""
        logger.info("Starting BTC payment monitoring system")
        
        # Create necessary tables
        self.create_payment_tables()
        
        if run_forever:
            logger.info(f"Monitoring payments every {CHECK_INTERVAL} seconds...")
            while True:
                try:
                    self.run_monitoring_cycle()
                    time.sleep(CHECK_INTERVAL)
                except KeyboardInterrupt:
                    logger.info("Payment monitoring stopped by user")
                    break
                except Exception as e:
                    logger.error(f"Error in monitoring loop: {e}")
                    time.sleep(CHECK_INTERVAL)
        else:
            # Run once
            return self.run_monitoring_cycle()


def main():
    """Main function to run the BTC payment monitor."""
    monitor = BTCPaymentMonitor()
    
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--once":
        # Run once and exit
        processed = monitor.start_monitoring(run_forever=False)
        print(f"Processed {processed} payments")
    else:
        # Run continuously
        monitor.start_monitoring()


if __name__ == "__main__":
    main()

