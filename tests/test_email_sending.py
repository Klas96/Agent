#!/usr/bin/env python3
"""
Test script to test email sending functionality.
"""

import os
import sys
from pathlib import Path

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from pocketflow.core.types import EmailSendRequest
from pocketflow.services.email_service import EmailService
from pocketflow.utils.logging import setup_logging, get_logger

def test_email_sending():
    """Test email sending functionality."""
    setup_logging(level="INFO", log_format="standard")
    logger = get_logger("EmailSendingTest")
    
    logger.info("=== Testing Email Sending ===")
    
    try:
        # Create email service
        email_service = EmailService()
        logger.info("EmailService created successfully")
        
        # Create a test email request
        send_request = EmailSendRequest(
            to="klas0holmgren@gmail.com",
            subject="Test Email from PocketFlow",
            body="This is a test email to verify that the email sending functionality is working correctly.",
            cc=None,
            attachment=None
        )
        
        logger.info(f"Sending test email to: {send_request.to}")
        logger.info(f"Subject: {send_request.subject}")
        logger.info(f"Body: {send_request.body}")
        
        # Send the email
        success = email_service.send_email(send_request)
        
        if success:
            logger.info("✅ Test email sent successfully!")
            return True
        else:
            logger.error("❌ Test email sending failed!")
            return False
        
    except Exception as e:
        logger.error(f"Email sending test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_email_sending()
    if success:
        print("✅ Email sending test completed")
    else:
        print("❌ Email sending test failed")
        sys.exit(1) 