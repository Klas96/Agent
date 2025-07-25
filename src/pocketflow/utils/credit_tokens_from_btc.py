#!/usr/bin/env python3
"""
Monitor Bitcoin payments and credit tokens to users.

This script monitors incoming Bitcoin payments and automatically credits tokens to users.
"""

import os
import sys
import time
import sqlite3
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import requests

from utils.electrum_utils import call_electrum_rpc, get_btc_usd_price
from src.pocketflow.services import database_service
from src.pocketflow.utils.errors import BitcoinError, DatabaseError

# Configure logging
logging.basicConfig(level=logging.INFO)
from src.pocketflow.utils.logging import get_logger
logger = get_logger("credit_tokens_from_btc")

# Configuration
DATABASE_PATH = "/opt/pocketflow/data/pocketflow.db"
TOKEN_PRICE_USD = 0.01  # $0.01 per token
MONITORING_INTERVAL = 60  # seconds
PAYMENT_CONFIRMATIONS = 1  # minimum confirmations required

class BTCPaymentMonitor:
    """Monitor Bitcoin payments and credit tokens to users."""
    
    def __init__(self):
        self.processed_payments = set()
        self.logger = logger
    
    def get_wallet_transactions(self) -> List[Dict]:
        """Get recent wallet transactions."""
        try:
            # Get transactions from the last 24 hours
            since_timestamp = int((datetime.now() - timedelta(hours=24)).timestamp())
            
            result = call_electrum_rpc("listtransactions", ["", 100, 0, True])
            if not result:
                logger.error("Failed to get wallet transactions")
                return []
            
            # Filter for incoming transactions in the last 24 hours
            incoming_txs = []
            for tx in result:
                if (tx.get('category') == 'receive' and 
                    tx.get('confirmations', 0) >= PAYMENT_CONFIRMATIONS and
                    tx.get('time', 0) >= since_timestamp):
                    incoming_txs.append(tx)
                    
            logger.info(f"Found {len(incoming_txs)} incoming transactions")
            return incoming_txs
            
        except Exception as e:
            logger.error(f"Error getting wallet transactions: {e}")
            raise BitcoinError(f"Failed to get wallet transactions: {e}")
    
    def get_address_user_mapping(self) -> Dict[str, str]:
        """Get mapping of BTC addresses to user emails."""
        try:
            # Get all users and their BTC addresses
            mapping = {}
            
            # Get all users from the database
            # Note: This would require adding a method to DatabaseService to get all users
            # For now, we'll use a more robust approach by querying the database directly
            # to get all users with BTC addresses
            
            conn = sqlite3.connect(DATABASE_PATH)
            cursor = conn.cursor()
            
            # Get all users with BTC addresses
            cursor.execute("""
                SELECT DISTINCT u.email, b.address 
                FROM users u 
                JOIN btc_addresses b ON u.email = b.email 
                WHERE b.address IS NOT NULL AND b.address != ''
            """)
            
            for email, address in cursor.fetchall():
                if address and address != "None":
                    mapping[address] = email
                    
            conn.close()
            logger.info(f"Found {len(mapping)} address-user mappings")
            return mapping
            
        except Exception as e:
            logger.error(f"Error getting address-user mapping: {e}")
            raise DatabaseError(f"Failed to get address-user mapping: {e}")
    
    def calculate_tokens_from_btc(self, btc_amount: float) -> int:
        """Calculate number of tokens based on BTC amount."""
        try:
            btc_price_usd = get_btc_usd_price()
            if not btc_price_usd:
                logger.error("Failed to get BTC price")
                raise BitcoinError("Failed to get BTC price")
                
            usd_amount = btc_amount * btc_price_usd
            tokens = int(usd_amount / TOKEN_PRICE_USD)
            
            logger.info(f"BTC: {btc_amount:.8f}, USD: ${usd_amount:.2f}, Tokens: {tokens}")
            return tokens
            
        except Exception as e:
            logger.error(f"Error calculating tokens: {e}")
            raise BitcoinError(f"Failed to calculate tokens: {e}")
    
    def credit_tokens_to_user(self, email: str, tokens: int, tx_id: str) -> bool:
        """Credit tokens to user and log the transaction."""
        try:
            # Update user tokens
            success = database_service.add_tokens(email, tokens)
            if not success:
                logger.error(f"Failed to update tokens for {email}")
                raise DatabaseError(f"Failed to update tokens for {email}")
            
            # Log the payment transaction
            conn = sqlite3.connect(DATABASE_PATH)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO btc_payments (email, btc_amount, usd_amount, tokens_credited, tx_id, timestamp)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (email, None, None, tokens, tx_id, datetime.now().isoformat()))
            
            conn.commit()
            conn.close()
            
            logger.info(f"Credited {tokens} tokens to {email} for transaction {tx_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to credit tokens to {email}: {e}")
            raise DatabaseError(f"Failed to credit tokens to {email}: {e}")
    
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
            
            # Check if address belongs to a user
            if address not in address_mapping:
                logger.debug(f"Address {address} not associated with any user")
                return False
            
            email = address_mapping[address]
            logger.info(f"Processing payment: {btc_amount} BTC to {email}")
            
            # Calculate tokens
            tokens = self.calculate_tokens_from_btc(btc_amount)
            if tokens <= 0:
                logger.warning(f"Calculated tokens is {tokens} for {btc_amount} BTC")
                return False
            
            # Credit tokens to user
            success = self.credit_tokens_to_user(email, tokens, tx_id)
            if success:
                self.processed_payments.add(tx_id)
                logger.info(f"Successfully processed payment: {tokens} tokens to {email}")
                return True
            else:
                logger.error(f"Failed to process payment for {email}")
                return False
                
        except Exception as e:
            logger.error(f"Error processing payment: {e}")
            raise BitcoinError(f"Failed to process payment: {e}")
    
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
            logger.info(f"Monitoring payments every {MONITORING_INTERVAL} seconds...")
            while True:
                try:
                    self.run_monitoring_cycle()
                    time.sleep(MONITORING_INTERVAL)
                except KeyboardInterrupt:
                    logger.info("Payment monitoring stopped by user")
                    break
                except Exception as e:
                    logger.error(f"Error in monitoring loop: {e}")
                    time.sleep(MONITORING_INTERVAL)
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

