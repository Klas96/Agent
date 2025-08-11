#!/usr/bin/env python3
"""
Test script to check all emails in the inbox.
"""

import os
import sys
from pathlib import Path

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from pocketflow.config.settings import get_settings
from pocketflow.services.email_service import EmailService
from pocketflow.utils.logging import setup_logging, get_logger
import imaplib
import email

def test_all_emails():
    """Test fetching all emails in the inbox."""
    setup_logging(level="INFO", log_format="standard")
    logger = get_logger("EmailFetchTest")
    
    logger.info("=== Testing All Email Fetching ===")
    
    # Get settings
    settings = get_settings()
    
    try:
        # Connect to IMAP server
        imap_server = imaplib.IMAP4_SSL(settings.EMAIL_HOST)
        imap_server.login(settings.EMAIL_USERNAME, settings.EMAIL_PASSWORD)
        imap_server.select('INBOX')
        
        # Get total number of emails
        _, data = imap_server.search(None, 'ALL')
        email_ids = data[0].split()
        total_emails = len(email_ids)
        
        logger.info(f"Total emails in inbox: {total_emails}")
        
        # Get unread emails
        _, data = imap_server.search(None, 'UNSEEN')
        unread_ids = data[0].split()
        unread_count = len(unread_ids)
        
        logger.info(f"Unread emails: {unread_count}")
        
        # Get recent emails (last 10)
        if total_emails > 0:
            logger.info("Recent emails:")
            recent_ids = email_ids[-10:]  # Last 10 emails
            for i, email_id in enumerate(recent_ids):
                try:
                    _, msg_data = imap_server.fetch(email_id, '(RFC822)')
                    email_body = msg_data[0][1]
                    email_message = email.message_from_bytes(email_body)
                    
                    subject = email_message.get('Subject', 'No Subject')
                    from_addr = email_message.get('From', 'Unknown')
                    date = email_message.get('Date', 'Unknown')
                    
                    logger.info(f"  {i+1}. From: {from_addr}")
                    logger.info(f"     Subject: {subject}")
                    logger.info(f"     Date: {date}")
                    logger.info(f"     ID: {email_id.decode()}")
                    logger.info("")
                    
                except Exception as e:
                    logger.warning(f"Failed to parse email {email_id}: {e}")
        
        imap_server.close()
        return True
        
    except Exception as e:
        logger.error(f"Email fetch test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_all_emails()
    if success:
        print("✅ Email fetch test completed")
    else:
        print("❌ Email fetch test failed")
        sys.exit(1) 