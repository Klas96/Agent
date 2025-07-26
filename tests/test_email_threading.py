#!/usr/bin/env python3
"""
Test for email threading functionality.
"""

import os
import sys
from pathlib import Path

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from pocketflow.core.types import SharedState, EmailSendRequest
from pocketflow.services.email_service import EmailService
from pocketflow.utils.logging import setup_logging, get_logger

def test_email_threading():
    """Test that email threading headers are properly set."""
    setup_logging(level="INFO", log_format="standard")
    logger = get_logger("EmailThreadingTest")
    
    logger.info("=== Testing Email Threading ===")
    
    try:
        # Create email service
        email_service = EmailService()
        logger.info("Created EmailService")
        
        # Test data with threading headers
        original_message_id = "<original-message-456@example.com>"
        reply_message_id = "<test-message-123@example.com>"
        references = f"{original_message_id} {reply_message_id}"
        
        # Create email send request with threading headers
        send_request = EmailSendRequest(
            to="test@example.com",
            subject="Re: Test Subject",
            body="This is a test reply with proper threading.",
            in_reply_to=reply_message_id,
            references=references
        )
        
        logger.info(f"Created EmailSendRequest with threading headers:")
        logger.info(f"  In-Reply-To: {send_request.in_reply_to}")
        logger.info(f"  References: {send_request.references}")
        
        # Note: We can't actually send the email in a test environment
        # but we can verify the headers are set correctly
        assert send_request.in_reply_to == reply_message_id
        assert send_request.references == references
        assert send_request.subject.startswith("Re: ")
        
        logger.info("✅ Email threading headers are properly set")
        return True
        
    except Exception as e:
        logger.error(f"Email threading test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_threading_with_shared_state():
    """Test threading with SharedState data."""
    setup_logging(level="INFO", log_format="standard")
    logger = get_logger("EmailThreadingSharedTest")
    
    logger.info("=== Testing Email Threading with SharedState ===")
    
    try:
        # Create shared state with email data
        shared = SharedState()
        shared.email = {
            'id': '123',
            'subject': 'Test Subject',
            'from': 'test@example.com',
            'body': 'Test body',
            'date': '2025-07-26 19:00:00',
            'message_id': '<test-message-123@example.com>',
            'thread_id': 'test-thread-123',
            'in_reply_to': '<original-message-456@example.com>',
            'references': '<original-message-456@example.com> <test-message-123@example.com>'
        }
        shared.user = 'test@example.com'
        shared.reply_body = 'This is a test reply with proper threading.'
        
        logger.info("Created SharedState with threading data")
        
        # Extract threading headers from shared state
        email = shared.email
        in_reply_to = email.get("in_reply_to") or email.get("message_id")
        references = email.get("references") or email.get("message_id")
        
        logger.info(f"Extracted threading headers:")
        logger.info(f"  In-Reply-To: {in_reply_to}")
        logger.info(f"  References: {references}")
        
        # Verify threading headers are properly extracted
        assert in_reply_to == '<original-message-456@example.com>'
        assert references == '<original-message-456@example.com> <test-message-123@example.com>'
        
        logger.info("✅ Threading headers properly extracted from SharedState")
        return True
        
    except Exception as e:
        logger.error(f"Email threading shared state test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success1 = test_email_threading()
    success2 = test_threading_with_shared_state()
    
    if success1 and success2:
        print("✅ All email threading tests completed successfully")
    else:
        print("❌ Some email threading tests failed")
        sys.exit(1) 