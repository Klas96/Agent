#!/usr/bin/env python3
"""
Test script to mark recent emails as unread for testing.
"""

import os
import sys
from pathlib import Path

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from pocketflow.config.settings import get_settings
from pocketflow.utils.logging import setup_logging, get_logger
import imaplib

def mark_emails_unread():
    """Mark the 3 most recent emails as unread for testing."""
    setup_logging(level="INFO", log_format="standard")
    logger = get_logger("MarkEmailsUnread")
    
    logger.info("=== Marking Recent Emails as Unread for Testing ===")
    
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
        
        if len(email_ids) >= 3:
            # Mark the 3 most recent emails as unread
            recent_ids = email_ids[-3:]  # Last 3 emails
            
            logger.info(f"Marking {len(recent_ids)} recent emails as unread...")
            
            for email_id in recent_ids:
                try:
                    # Remove the SEEN flag to mark as unread
                    imap_server.store(email_id, '-FLAGS', '\\Seen')
                    logger.info(f"Marked email {email_id.decode()} as unread")
                except Exception as e:
                    logger.warning(f"Failed to mark email {email_id} as unread: {e}")
            
            logger.info("✅ Successfully marked recent emails as unread")
            logger.info("Now try sending an email to agent@klasholmgren.se to test the system")
            
        else:
            logger.warning("Not enough emails in inbox to mark as unread")
        
        imap_server.close()
        return True
        
    except Exception as e:
        logger.error(f"Failed to mark emails as unread: {e}")
        return False

if __name__ == "__main__":
    success = mark_emails_unread()
    if success:
        print("✅ Email marking test completed")
    else:
        print("❌ Email marking test failed")
        sys.exit(1) 