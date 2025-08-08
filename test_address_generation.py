#!/usr/bin/env python3
"""
Test script to verify that different users get different Bitcoin addresses.
"""

import sys
import os
sys.path.append('/opt/pocketflow')

from src.pocketflow.utils.simple_bitcoin_utils import simple_bitcoin_utils

def test_address_generation():
    """Test that different users get different addresses."""
    
    print("🧪 Testing Bitcoin Address Generation")
    print("=" * 50)
    
    # Test different user emails
    test_emails = [
        "user1@example.com",
        "user2@example.com", 
        "user3@example.com",
        "klas0holmgren@gmail.com",
        "test@test.com"
    ]
    
    addresses = {}
    
    for email in test_emails:
        print(f"\nTesting email: {email}")
        
        try:
            # Generate address for this user
            address = simple_bitcoin_utils.get_new_address(email)
            
            if address:
                print(f"   ✅ Generated: {address}")
                addresses[email] = address
            else:
                print(f"   ❌ Failed to generate address")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    # Check for duplicates
    print(f"\n📊 Address Generation Results:")
    print("=" * 50)
    
    unique_addresses = set(addresses.values())
    total_addresses = len(addresses)
    unique_count = len(unique_addresses)
    
    print(f"Total addresses generated: {total_addresses}")
    print(f"Unique addresses: {unique_count}")
    print(f"Duplicate addresses: {total_addresses - unique_count}")
    
    if unique_count == total_addresses:
        print("✅ SUCCESS: All users got different addresses!")
    else:
        print("❌ FAILURE: Some users got the same address!")
        
        # Show which addresses are duplicates
        address_counts = {}
        for email, address in addresses.items():
            if address in address_counts:
                address_counts[address].append(email)
            else:
                address_counts[address] = [email]
        
        print("\nDuplicate addresses:")
        for address, emails in address_counts.items():
            if len(emails) > 1:
                print(f"  {address}: {emails}")
    
    return unique_count == total_addresses

if __name__ == "__main__":
    success = test_address_generation()
    sys.exit(0 if success else 1) 