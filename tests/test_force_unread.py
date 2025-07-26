#!/usr/bin/env python3
"""
Test script to force mark emails as unread.
"""

import os
import sys
from pathlib import Path

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from pocketflow.config.settings import get_settings
from pocketflow.utils.logging import setup_logging, get_logger
import imaplib

def force_mark_unread():
    """Force mark recent emails as unread using different IMAP commands."""
    setup_logging(level="INFO", log_format="standard")
    logger = get_logger("ForceUnread")
    
    logger.info("=== Force Marking Emails as Unread ===")
    
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
            
            logger.info(f"Force marking {len(recent_ids)} recent emails as unread...")
            
            for email_id in recent_ids:
                try:
                    # Method 1: Remove SEEN flag
                    imap_server.store(email_id, '-FLAGS', '\\Seen')
                    
                    # Method 2: Set UNSEEN flag (if supported)
                    try:
                        imap_server.store(email_id, '+FLAGS', '\\Unseen')
                    except:
                        pass
                    
                    # Method 3: Remove all flags and set only UNSEEN
                    try:
                        imap_server.store(email_id, 'FLAGS', '\\Unseen')
                    except:
                        pass
                    
                    logger.info(f"Force marked email {email_id.decode()} as unread")
                    
                except Exception as e:
                    logger.warning(f"Failed to mark email {email_id} as unread: {e}")
            
            logger.info("✅ Force marked recent emails as unread")
            
            # Verify the changes
            logger.info("Verifying changes...")
            _, data = imap_server.search(None, 'UNSEEN')
            unread_ids = data[0].split()
            logger.info(f"Now have {len(unread_ids)} unread emails")
            
        else:
            logger.warning("Not enough emails in inbox to mark as unread")
        
        imap_server.close()
        return True
        
    except Exception as e:
        logger.error(f"Failed to force mark emails as unread: {e}")
        return False

if __name__ == "__main__":
    success = force_mark_unread()
    if success:
        print("✅ Force unread marking completed")
    else:
        print("❌ Force unread marking failed")
        sys.exit(1) 