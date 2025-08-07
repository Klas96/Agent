#!/usr/bin/env python3
import sqlite3

DB_PATH = '/opt/pocketflow/data/users.db'
BTC_ADDRESS = 'bc1q7mpa2vcxsmgxamcwe5p4dt9nek2j7t2t57jh27'

def remove_btc_address(db_path, btc_address):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM btc_addresses WHERE address=?", (btc_address,))
    deleted = cursor.rowcount
    conn.commit()
    conn.close()
    return deleted

def main():
    deleted = remove_btc_address(DB_PATH, BTC_ADDRESS)
    if deleted:
        print(f"✅ Removed {deleted} record(s) for address {BTC_ADDRESS} from {DB_PATH}")
    else:
        print(f"❌ Address {BTC_ADDRESS} not found in {DB_PATH}")

if __name__ == "__main__":
    main() 