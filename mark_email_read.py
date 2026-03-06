#!/usr/bin/env python3
"""
Mark specific email as read to stop spam.
"""

import os
import imaplib

def mark_email_read():
    """Mark email 951 as read."""
    
    print("Marking email 951 as read...")
    
    # Email configuration
    email_user = os.getenv('EMAIL_USER', 'agent@klasholmgren.se')
    email_pass = os.getenv('EMAIL_PASSWORD', '40qE7xKJuz')
    imap_server = os.getenv('IMAP_SERVER', 'mailcluster.loopia.se')
    
    try:
        # Connect to IMAP server
        mail = imaplib.IMAP4(imap_server)
        mail.starttls()
        mail.login(email_user, email_pass)
        mail.select('INBOX')
        
        # Mark email 951 as read
        mail.store('951', '+FLAGS', '\\Seen')
        print("✅ Email 951 marked as read")
        
        # Verify it's marked as read
        status, messages = mail.search(None, 'UNSEEN')
        if status == 'OK':
            email_ids = messages[0].split()
            print(f"Remaining unread emails: {len(email_ids)}")
        
        mail.close()
        mail.logout()
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    mark_email_read() 