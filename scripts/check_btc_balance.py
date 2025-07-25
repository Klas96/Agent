#!/usr/bin/env python3
"""
Check Bitcoin balance using Electrum RPC.
"""

import sys
import os
sys.path.append('/opt/pocketflow')

import json
import requests
from src.pocketflow.config.settings import get_settings
from src.pocketflow.utils.errors import BitcoinError

def main():
    """Check Bitcoin balance."""
    try:
        # Get settings
        settings = get_settings()
        
        # Build RPC URL
        url = f"http://localhost:{settings.ELECTRUM_PORT}/"
        
        payload = {
            "id": 0,
            "method": "getbalance",
            "params": []
        }
        headers = {"Content-Type": "application/json"}
        
        # Use settings for authentication
        user = settings.ELECTRUM_USERNAME
        password = settings.ELECTRUM_PASSWORD
        auth = (user, password) if user and password else None
        
        response = requests.post(url, data=json.dumps(payload), headers=headers, auth=auth)
        result = response.json()
        
        print(f"Bitcoin Balance: {result}")
        return result
        
    except Exception as e:
        print(f"Error checking Bitcoin balance: {e}")
        return None

if __name__ == "__main__":
    main() 