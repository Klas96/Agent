#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.pocketflow.services import database_service
from nodes import get_or_create_btc_address

def main():
    if len(sys.argv) > 1:
        email = sys.argv[1]
    else:
        email = input("Enter user email: ")
    if not email:
        print("Email is required.")
        sys.exit(1)
    btc_address = get_or_create_btc_address({}, email)
    if btc_address not in database_service.get_btc_addresses(email):
        database_service.add_btc_address(email, btc_address)
    database_service.create_user(email, tokens=0)  # No btc_address field
    print(f"User added: {email}\nBTC address: {btc_address}")

if __name__ == "__main__":
    main() 