#!/usr/bin/env python3
"""
Check if a Bitcoin address is in the Electrum wallet.
"""

import sys
import os
sys.path.append('/opt/pocketflow')

import json
import requests
from src.pocketflow.config.settings import get_settings
from src.pocketflow.utils.errors import BitcoinError

def main():
    """Check if address is in wallet."""
    try:
        # Get address to check
        address_to_check = sys.argv[1] if len(sys.argv) > 1 else input("Enter BTC address to check: ").strip()
        
        # Get settings
        settings = get_settings()
        
        # Build RPC URL
        url = f"http://localhost:{settings.ELECTRUM_PORT}/"
        payload = {
            "id": 0,
            "method": "listaddresses",
            "params": []
        }
        headers = {"Content-Type": "application/json"}
        
        # Use settings for authentication
        user = settings.ELECTRUM_USERNAME or "myuser"
        password = settings.ELECTRUM_PASSWORD or "mypass"
        auth = (user, password) if user and password else None
        
        response = requests.post(url, data=json.dumps(payload), headers=headers, auth=auth)
        
        try:
            data = response.json()
        except Exception as e:
            print("Error decoding JSON from Electrum RPC. Raw response:")
            print(response.text)
            return False
        
        if "result" in data:
            addresses = data["result"]
            if address_to_check in addresses:
                print(f"Address {address_to_check} IS in your Electrum wallet.")
                return True
            else:
                print(f"Address {address_to_check} is NOT in your Electrum wallet.")
                return False
        else:
            print("Error from Electrum RPC:", data)
            return False
            
    except Exception as e:
        print(f"Error checking address: {e}")
        return False

if __name__ == "__main__":
    main() 