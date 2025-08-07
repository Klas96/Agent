#!/usr/bin/env python3
"""
Direct test of Electrum wallet address generation.
"""

import subprocess
import sys

def test_electrum_direct():
    """Test Electrum wallet directly."""
    print("Testing Electrum wallet address generation...")
    
    # Test listing addresses
    try:
        result = subprocess.run([
            "/opt/pocketflow/venv/bin/electrum",
            "--wallet", "/home/pocketflow/.electrum/wallets/user_wallet",
            "listaddresses",
            "--offline"
        ], capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            print("✅ Successfully listed addresses:")
            print(result.stdout)
        else:
            print("❌ Failed to list addresses:")
            print(result.stderr)
            
    except Exception as e:
        print(f"❌ Exception listing addresses: {e}")
    
    # Test creating new address
    try:
        result = subprocess.run([
            "/opt/pocketflow/venv/bin/electrum",
            "--wallet", "/home/pocketflow/.electrum/wallets/user_wallet",
            "createnewaddress",
            "--offline"
        ], capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            print("✅ Successfully created new address:")
            print(result.stdout)
        else:
            print("❌ Failed to create new address:")
            print(result.stderr)
            
    except Exception as e:
        print(f"❌ Exception creating address: {e}")

if __name__ == "__main__":
    test_electrum_direct() 