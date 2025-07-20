import os
import json
import requests
import sqlite3

DB_PATH = "user_db.db"

# Get all addresses from Electrum wallet
url = f"http://localhost:{os.environ.get('ELECTRUM_RPCPORT', '7777')}/"
payload = {
    "id": 0,
    "method": "listaddresses",
    "params": []
}
headers = {"Content-Type": "application/json"}
user = os.environ.get("ELECTRUM_RPCUSER")
password = os.environ.get("ELECTRUM_RPCPASSWORD")
auth = (user, password) if user and password else None
response = requests.post(url, data=json.dumps(payload), headers=headers, auth=auth)
data = response.json()
if "result" in data:
    wallet_addresses = set(data["result"])
else:
    print("Error from Electrum RPC:", data)
    exit(1)

# Connect to the database
conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()
cur.execute("SELECT id, btc_address FROM addresses")
rows = cur.fetchall()
removed = 0
for row in rows:
    addr_id, btc_address = row
    if btc_address not in wallet_addresses:
        print(f"Removing address not in wallet: {btc_address}")
        cur.execute("DELETE FROM addresses WHERE id=?", (addr_id,))
        removed += 1
conn.commit()
conn.close()
print(f"Done. Removed {removed} invalid addresses.") 