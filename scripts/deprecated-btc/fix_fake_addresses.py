#!/usr/bin/env python3
"""
Fix fake Bitcoin addresses in the database.

This script identifies addresses that were generated using the old hash-based method
and replaces them with real addresses from the Electrum wallet.
"""

import sys
import os
import sqlite3
import hashlib
import subprocess

DB_PATH = '/opt/pocketflow/data/users.db'

def is_fake_address(address: str) -> bool:
    """Check if an address was generated using the old hash method."""
    # The old method generated addresses like bc1 + 34 character hash
    if not address.startswith('bc1'):
        return False
    
    # Check if it's exactly 35 characters (bc1 + 34 char hash)
    if len(address) != 35:
        return False
    
    # Check if the part after bc1 looks like a hex hash
    hash_part = address[3:]  # Remove 'bc1'
    try:
        # Try to decode as hex to see if it's a valid hash
        int(hash_part, 16)
        return True
    except ValueError:
        return False

def get_real_addresses_from_wallet() -> list:
    """Get real addresses from Electrum wallet."""
    try:
        result = subprocess.run([
            "sudo", "-u", "pocketflow", 
            "/opt/pocketflow/venv/bin/electrum",
            "--wallet", "/home/pocketflow/.electrum/wallets/user_wallet",
            "listaddresses", "--offline"
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            # Parse the JSON output
            import json
            addresses = json.loads(result.stdout)
            return addresses
        else:
            print(f"Failed to get wallet addresses: {result.stderr}")
            return []
    except Exception as e:
        print(f"Error getting wallet addresses: {e}")
        return []

def fix_fake_addresses():
    """Identify and fix fake addresses in the database."""
    print("🔧 Fixing fake Bitcoin addresses in database")
    print("=" * 50)
    
    # Connect to database
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Get all addresses
    cursor.execute("SELECT email, address FROM btc_addresses")
    all_addresses = cursor.fetchall()
    
    fake_addresses = []
    real_addresses = []
    
    # Identify fake addresses
    for email, address in all_addresses:
        if is_fake_address(address):
            fake_addresses.append((email, address))
        else:
            real_addresses.append((email, address))
    
    print(f"Found {len(fake_addresses)} fake addresses:")
    for email, address in fake_addresses:
        print(f"  {email}: {address}")
    
    if not fake_addresses:
        print("✅ No fake addresses found!")
        return
    
    # Get real addresses from wallet
    wallet_addresses = get_real_addresses_from_wallet()
    if not wallet_addresses:
        print("❌ Failed to get addresses from wallet")
        return
    
    print(f"\nFound {len(wallet_addresses)} real addresses in wallet")
    
    # Fix fake addresses
    fixed_count = 0
    for email, fake_address in fake_addresses:
        # Find an unused real address
        used_addresses = [addr for _, addr in real_addresses]
        available_addresses = [addr for addr in wallet_addresses if addr not in used_addresses]
        
        if available_addresses:
            real_address = available_addresses[0]
            
            # Update the database
            cursor.execute(
                "UPDATE btc_addresses SET address = ? WHERE email = ? AND address = ?",
                (real_address, email, fake_address)
            )
            
            print(f"✅ Fixed {email}: {fake_address} → {real_address}")
            fixed_count += 1
            
            # Update our tracking
            real_addresses.append((email, real_address))
        else:
            print(f"❌ No available addresses for {email}")
    
    conn.commit()
    conn.close()
    
    print(f"\n✅ Fixed {fixed_count} fake addresses")

if __name__ == "__main__":
    fix_fake_addresses() 