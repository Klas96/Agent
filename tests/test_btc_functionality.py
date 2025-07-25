#!/usr/bin/env python3
"""
Test script to verify Bitcoin address functionality
"""

import sys
import os
sys.path.append('/opt/pocketflow')

from utils.electrum_utils import get_new_btc_address, get_btc_usd_price
from src.pocketflow.services import llm_service, database_service

def test_btc_functionality(test_email=None):
    """Test the complete BTC address generation flow"""
    
    if not test_email:
        if len(sys.argv) > 1:
            test_email = sys.argv[1]
        else:
            test_email = input("Enter test email address: ")
    
    if not test_email:
        print("Test email address is required.")
        return False
    
    print("🧪 Testing Bitcoin Address Functionality")
    print("=" * 50)
    
    # Test email
    print(f"Using test email: {test_email}")
    
    # 1. Generate new BTC address
    print("1. Generating new BTC address...")
    btc_address = get_new_btc_address()
    if btc_address:
        print(f"   ✅ Generated: {btc_address}")
    else:
        print("   ❌ Failed to generate BTC address")
        return False
    
    # 2. Get BTC price
    print("2. Fetching BTC price...")
    btc_price = get_btc_usd_price()
    if btc_price:
        print(f"   ✅ BTC Price: ${btc_price:,.2f}")
    else:
        print("   ❌ Failed to get BTC price")
        return False
    
    # 3. Store address in database
    print("3. Storing address in database...")
    success = database_service.add_btc_address(test_email, btc_address)
    if success:
        print(f"   ✅ Stored address for {test_email}")
    else:
        print("   ❌ Failed to store address in database")
        return False
    
    # 4. Retrieve address from database
    print("4. Retrieving address from database...")
    stored_addresses = database_service.get_btc_addresses(test_email)
    if stored_addresses and btc_address in stored_addresses:
        print(f"   ✅ Retrieved: {btc_address}")
    else:
        print("   ❌ Failed to retrieve address from database")
        return False
    
    # 5. Calculate token pricing
    print("5. Calculating token pricing...")
    token_price_usd = 0.01  # $0.01 per token
    token_price_btc = token_price_usd / btc_price
    tokens_10_price_btc = token_price_btc * 10
    
    print(f"   ✅ Token price: {token_price_btc:.8f} BTC (≈ ${token_price_usd:.2f})")
    print(f"   ✅ 10 tokens: {tokens_10_price_btc:.8f} BTC")
    
    # 6. Simulate response message
    print("6. Simulating response message...")
    token_note = f"""
---
Note: For advanced features like music generation, you'll need tokens. 
To purchase tokens, send Bitcoin to: {btc_address}
Each token costs {token_price_btc:.8f} BTC (≈ ${token_price_usd:.2f}). 
You can purchase 10 tokens for approximately {tokens_10_price_btc:.8f} BTC.
"""
    print(f"   ✅ Response note generated")
    print(f"   📝 Note: {token_note.strip()}")
    
    print("\n🎉 All tests passed! Bitcoin functionality is working correctly!")
    return True

if __name__ == "__main__":
    success = test_btc_functionality()
    if success:
        print("\n✅ Bitcoin address functionality is fully operational!")
    else:
        print("\n❌ Some tests failed. Please check the logs.") 