#!/usr/bin/env python3
import os
import sqlite3

BTC_ADDRESS = 'bc19aaad8cc40b7109eefd6ca1f53f4ecab00'

# List of .db files to search in /opt/pocketflow
DB_FILES = [
    '/opt/pocketflow/data/users.db',
    '/opt/pocketflow/data/pocketflow.db',
    '/opt/pocketflow/user_db.db',
    '/opt/pocketflow/tests/user_data.db',
    '/opt/pocketflow/user_data.db',
]

def search_db(db_path, btc_address):
    if not os.path.exists(db_path):
        return []
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT email, address FROM btc_addresses WHERE address=?", (btc_address,))
        results = cursor.fetchall()
        conn.close()
        return results
    except Exception as e:
        print(f"Error searching {db_path}: {e}")
        return []

def main():
    print(f"🔍 Searching for BTC address: {BTC_ADDRESS}")
    print("=" * 50)
    
    found = False
    for db_path in DB_FILES:
        print(f"Checking {db_path}...")
        results = search_db(db_path, BTC_ADDRESS)
        if results:
            print(f"✅ Found in {db_path}:")
            for email, address in results:
                print(f"   Email: {email}")
                print(f"   Address: {address}")
            found = True
        else:
            print(f"   ❌ Not found")
    
    if not found:
        print(f"\n❌ Address {BTC_ADDRESS} not found in any database.")
    else:
        print(f"\n✅ Address {BTC_ADDRESS} is in the wallet database.")

if __name__ == "__main__":
    main() 