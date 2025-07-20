import os
import json
import requests

url = f"http://localhost:{os.environ.get('ELECTRUM_RPCPORT', '7777')}/"
payload = {
    "id": 0,
    "method": "getbalance",
    "params": []
}
headers = {"Content-Type": "application/json"}
user = os.environ.get("ELECTRUM_RPCUSER")
password = os.environ.get("ELECTRUM_RPCPASSWORD")
auth = (user, password) if user and password else None

response = requests.post(url, data=json.dumps(payload), headers=headers, auth=auth)
print(response.json()) 