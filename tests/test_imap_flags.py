#!/usr/bin/env python3
"""
Test script to check IMAP flags and email status.
"""

import os
import sys
from pathlib import Path

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from pocketflow.config.settings import get_settings
from pocketflow.utils.logging import setup_logging, get_logger
import imaplib

def check_imap_flags():
    """Check IMAP flags for recent emails."""
    setup_logging(level="INFO", log_format="standard")
    logger = get_logger("IMAPFlagsTest")
    
    logger.info("=== Checking IMAP Flags ===")
    
    # Get settings
    settings = get_settings()
    
    try:
        # Connect to IMAP server
        imap_server = imaplib.IMAP4_SSL(settings.EMAIL_HOST)
        imap_server.login(settings.EMAIL_USERNAME, settings.EMAIL_PASSWORD)
        imap_server.select('INBOX')
        
        # Get recent emails
        _, data = imap_server.search(None, 'ALL')
        email_ids = data[0].split()
        
        if len(email_ids) >= 5:
            # Check the 5 most recent emails
            recent_ids = email_ids[-5:]  # Last 5 emails
            
            logger.info(f"Checking flags for {len(recent_ids)} recent emails...")
            
            for i, email_id in enumerate(recent_ids):
                try:
                    # Get flags for this email
                    _, flags_data = imap_server.fetch(email_id, '(FLAGS)')
                    flags = flags_data[0].decode()
                    
                    # Get basic email info
                    _, msg_data = imap_server.fetch(email_id, '(RFC822.HEADER)')
                    email_body = msg_data[0][1]
                    
                    # Parse headers
                    import email
                    email_message = email.message_from_bytes(email_body)
                    subject = email_message.get('Subject', 'No Subject')
                    from_addr = email_message.get('From', 'Unknown')
                    
                    logger.info(f"  Email {i+1} (ID: {email_id.decode()}):")
                    logger.info(f"    From: {from_addr}")
                    logger.info(f"    Subject: {subject}")
                    logger.info(f"    Flags: {flags}")
                    
                    # Check if it's marked as seen
                    if '\\Seen' in flags:
                        logger.info(f"    Status: READ")
                    else:
                        logger.info(f"    Status: UNREAD")
                    logger.info("")
                    
                except Exception as e:
                    logger.warning(f"Failed to check email {email_id}: {e}")
        
        imap_server.close()
        return True
        
    except Exception as e:
        logger.error(f"IMAP flags check failed: {e}")
        return False

if __name__ == "__main__":
    success = check_imap_flags()
    if success:
        print("✅ IMAP flags check completed")
    else:
        print("❌ IMAP flags check failed")
        sys.exit(1) 