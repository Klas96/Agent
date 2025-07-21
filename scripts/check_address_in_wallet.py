import os
import json
import requests
import sys

address_to_check = sys.argv[1] if len(sys.argv) > 1 else input("Enter BTC address to check: ").strip()

url = f"http://localhost:{os.environ.get('ELECTRUM_RPCPORT', '7778')}/"
payload = {
    "id": 0,
    "method": "listaddresses",
    "params": []
}
headers = {"Content-Type": "application/json"}
user = os.environ.get("ELECTRUM_RPCUSER", "myuser")
password = os.environ.get("ELECTRUM_RPCPASSWORD", "mypass")
auth = (user, password) if user and password else None

response = requests.post(url, data=json.dumps(payload), headers=headers, auth=auth)
try:
    data = response.json()
except Exception as e:
    print("Error decoding JSON from Electrum RPC. Raw response:")
    print(response.text)
    exit(1)
if "result" in data:
    addresses = data["result"]
    if address_to_check in addresses:
        print(f"Address {address_to_check} IS in your Electrum wallet.")
    else:
        print(f"Address {address_to_check} is NOT in your Electrum wallet.")
else:
    print("Error from Electrum RPC:", data) 