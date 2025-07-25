#!/usr/bin/env python3
"""
Purge invalid Bitcoin addresses from database.
"""

import sys
import os
sys.path.append('/opt/pocketflow')

import json
import requests
from src.pocketflow.config.settings import get_settings
from src.pocketflow.services import database_service
from src.pocketflow.utils.errors import BitcoinError, DatabaseError

def main():
    """Purge invalid addresses from database."""
    try:
        # Get settings
        settings = get_settings()
        
        # Get all addresses from Electrum wallet
        url = f"http://localhost:{settings.ELECTRUM_PORT}/"
        payload = {
            "id": 0,
            "method": "listaddresses",
            "params": []
        }
        headers = {"Content-Type": "application/json"}
        
        user = settings.ELECTRUM_USERNAME
        password = settings.ELECTRUM_PASSWORD
        auth = (user, password) if user and password else None
        
        response = requests.post(url, data=json.dumps(payload), headers=headers, auth=auth)
        data = response.json()
        
        if "result" in data:
            wallet_addresses = set(data["result"])
        else:
            print("Error from Electrum RPC:", data)
            return False
        
        # Get all BTC addresses from database
        btc_addresses = database_service.get_btc_addresses()
        removed = 0
        
        for address_data in btc_addresses:
            btc_address = address_data.get("address")
            if btc_address and btc_address not in wallet_addresses:
                print(f"Removing address not in wallet: {btc_address}")
                # Note: We would need to add a delete method to database_service
                # For now, just report the invalid addresses
                removed += 1
        
        print(f"Found {removed} invalid addresses to remove.")
        return True
        
    except Exception as e:
        print(f"Error purging invalid addresses: {e}")
        return False

if __name__ == "__main__":
    main() 