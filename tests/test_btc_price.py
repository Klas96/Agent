#!/usr/bin/env python3
"""
Test script for Bitcoin service CoinGecko integration.
"""

import sys
import os
sys.path.append('/opt/pocketflow')

from src.pocketflow.services.bitcoin_service import BitcoinService

def main():
    """Test the Bitcoin service."""
    try:
        print("Testing Bitcoin service...")
        
        # Create Bitcoin service
        bitcoin_service = BitcoinService()
        
        # Test getting BTC price
        btc_price = bitcoin_service.get_btc_price()
        print(f"Current BTC price: ${btc_price:,.2f}")
        
        # Test USD to BTC conversion
        usd_amount = 10.0
        btc_amount = bitcoin_service._usd_to_btc(usd_amount)
        print(f"${usd_amount} = {btc_amount:.8f} BTC")
        
        # Test service info
        info = bitcoin_service.get_service_info()
        print(f"Service info: {info}")
        
        print("✅ Bitcoin service test completed successfully!")
        
    except Exception as e:
        print(f"❌ Error testing Bitcoin service: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 