#!/usr/bin/env python3
"""
Test script to verify user email extraction.
"""

import sys
import os
from pathlib import Path

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from pocketflow.core.types import SharedState
from pocketflow.nodes.email.fetch import FetchEmailNode
from pocketflow.utils.email_utils import extract_email

def test_user_extraction():
    """Test user email extraction from email data."""
    
    # Test the extract_email function
    test_cases = [
        "Klas Holmgren <klas0holmgren@gmail.com>",
        "klas0holmgren@gmail.com",
        "Some Name <test@example.com>",
        "test@example.com"
    ]
    
    print("Testing extract_email function:")
    for test_case in test_cases:
        extracted = extract_email(test_case)
        print(f"  '{test_case}' -> '{extracted}'")
    
    # Test with a mock email data
    print("\nTesting FetchEmailNode user extraction:")
    
    # Create a mock shared state
    shared = SharedState()
    
    # Create a mock email data
    class MockEmailData:
        def __init__(self):
            self.id = "test123"
            self.subject = "Test Subject"
            self.from_ = "Klas Holmgren <klas0holmgren@gmail.com>"
            self.body = "Test email body"
            self.received_at = "2025-08-03 18:30:00"
            self.message_id = "<test@example.com>"
            self.thread_id = "<test@example.com>"
            self.in_reply_to = None
            self.references = None
    
    # Test the post method logic
    email_data = MockEmailData()
    
    # Simulate the post method logic
    shared.email = {
        'id': email_data.id,
        'subject': email_data.subject,
        'from': email_data.from_,
        'body': email_data.body,
        'date': email_data.received_at,
        'message_id': email_data.message_id,
        'thread_id': email_data.thread_id,
        'in_reply_to': email_data.in_reply_to,
        'references': email_data.references
    }
    
    # Extract user email from sender
    user_email = extract_email(email_data.from_)
    shared.user = user_email
    
    print(f"  Extracted user email: {shared.user}")
    print(f"  Shared state user: {shared.user}")
    
    return shared.user == "klas0holmgren@gmail.com"

if __name__ == "__main__":
    success = test_user_extraction()
    if success:
        print("\n✅ User extraction test PASSED")
    else:
        print("\n❌ User extraction test FAILED") 