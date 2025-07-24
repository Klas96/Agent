#!/usr/bin/env python3
import os
import sqlite3

BTC_ADDRESS = 'bc1q7mpa2vcxsmgxamcwe5p4dt9nek2j7t2t57jh27'

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
    found = False
    for db in DB_FILES:
        results = search_db(db, BTC_ADDRESS)
        if results:
            print(f"\n✅ Found in {db}:")
            for email, address in results:
                print(f"  User: {email}\n  Address: {address}")
            found = True
    if not found:
        print("\n❌ Address not found in any production database.")

if __name__ == "__main__":
    main() 