#!/usr/bin/env python3
"""
Simple script to check for Bitcoin payments and assign tokens.
"""

import sys
import os
import json
import subprocess
import sqlite3
from pathlib import Path

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def check_address_balance(address):
    """Check the balance for a specific address."""
    try:
        result = subprocess.run([
            "/opt/pocketflow/venv/bin/electrum",
            "-D", "/opt/pocketflow/.electrum",
            "--wallet", "/opt/pocketflow/.electrum/wallets/user_wallet",
            "getaddressbalance",
            address
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            balance_data = json.loads(result.stdout.strip())
            confirmed = float(balance_data.get("confirmed", "0"))
            unconfirmed = float(balance_data.get("unconfirmed", "0"))
            return confirmed + unconfirmed
        else:
            print(f"Failed to get address balance: {result.stderr}")
            return 0.0
            
    except Exception as e:
        print(f"Error getting address balance: {e}")
        return 0.0

def update_user_tokens(email, tokens_to_add):
    """Update user's token balance."""
    try:
        db_path = '/opt/pocketflow/data/pocketflow.db'
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            
            # Get current tokens
            cursor.execute('SELECT tokens FROM users WHERE email = ?', (email,))
            result = cursor.fetchone()
            if result:
                current_tokens = result[0] or 0
                new_tokens = current_tokens + tokens_to_add
                
                # Update tokens
                cursor.execute('UPDATE users SET tokens = ? WHERE email = ?', (new_tokens, email))
                conn.commit()
                
                print(f"Updated user {email}: {current_tokens} -> {new_tokens} tokens")
                return new_tokens
            else:
                print(f"User {email} not found")
                return None
                
    except Exception as e:
        print(f"Error updating user tokens: {e}")
        return None

def log_payment(email, address, amount, tokens_added):
    """Log the payment."""
    try:
        db_path = '/opt/pocketflow/data/pocketflow.db'
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO payment_logs (user_id, address, amount, tokens_added, timestamp)
                VALUES ((SELECT id FROM users WHERE email = ?), ?, ?, ?, datetime('now'))
            ''', (email, address, amount, tokens_added))
            
            conn.commit()
            print(f"Logged payment: {amount} BTC -> {tokens_added} tokens")
            
    except Exception as e:
        print(f"Error logging payment: {e}")

def update_address_balance(address, balance):
    """Update the last known balance for an address."""
    try:
        db_path = '/opt/pocketflow/data/pocketflow.db'
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO address_balances (address, last_balance, last_checked)
                VALUES (?, ?, datetime('now'))
            ''', (address, balance))
            
            conn.commit()
            print(f"Updated address balance: {address} -> {balance}")
            
    except Exception as e:
        print(f"Error updating address balance: {e}")

def get_address_last_balance(address):
    """Get the last known balance for an address."""
    try:
        db_path = '/opt/pocketflow/data/pocketflow.db'
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('SELECT last_balance FROM address_balances WHERE address = ?', (address,))
            result = cursor.fetchone()
            
            return float(result[0]) if result else 0.0
            
    except Exception as e:
        print(f"Error getting address last balance: {e}")
        return 0.0

def main():
    """Main function to check for payments."""
    print("Checking for Bitcoin payments...")
    
    # Get user and address from database
    try:
        db_path = '/opt/pocketflow/data/pocketflow.db'
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('SELECT email, btc_address FROM users WHERE btc_address IS NOT NULL')
            users = cursor.fetchall()
            
            for email, btc_address in users:
                print(f"\nChecking user: {email}")
                print(f"Address: {btc_address}")
                
                # Get current balance
                current_balance = check_address_balance(btc_address)
                print(f"Current balance: {current_balance} BTC")
                
                # Get last known balance
                last_balance = get_address_last_balance(btc_address)
                print(f"Last known balance: {last_balance} BTC")
                
                if current_balance > last_balance:
                    payment_amount = current_balance - last_balance
                    tokens_to_add = int(payment_amount / 0.0001)  # 1 token = 0.0001 BTC
                    
                    print(f"New payment detected: {payment_amount} BTC")
                    print(f"Tokens to add: {tokens_to_add}")
                    
                    # Give at least 1 token for any payment, or calculate fractional tokens
                    if tokens_to_add == 0 and payment_amount > 0:
                        tokens_to_add = 1
                        print(f"Small payment detected, giving 1 token")
                    
                    if tokens_to_add > 0:
                        # Update user tokens
                        new_balance = update_user_tokens(email, tokens_to_add)
                        
                        if new_balance is not None:
                            # Log the payment
                            log_payment(email, btc_address, payment_amount, tokens_to_add)
                            
                            # Update address balance
                            update_address_balance(btc_address, current_balance)
                            
                            print(f"✅ Payment processed successfully!")
                            print(f"User {email} now has {new_balance} tokens")
                        else:
                            print("❌ Failed to update user tokens")
                    else:
                        print("Payment amount too small for tokens")
                else:
                    print("No new payments detected")
                    
    except Exception as e:
        print(f"Error checking payments: {e}")

if __name__ == "__main__":
    main() 