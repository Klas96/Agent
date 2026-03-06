#!/usr/bin/env python3
"""
Test email connection and check for emails.
"""

import os
import imaplib
import email
from email.header import decode_header
from datetime import datetime

def test_email_connection():
    """Test connection to email server and check for emails."""
    
    print("Testing email connection...")
    
    # Email configuration
    email_user = os.getenv('EMAIL_USER', 'agent@klasholmgren.se')
    email_pass = os.getenv('EMAIL_PASSWORD', '40qE7xKJuz')  # Use EMAIL_PASSWORD instead of EMAIL_PASS
    imap_server = os.getenv('IMAP_SERVER', 'mailcluster.loopia.se')
    
    print(f"Email: {email_user}")
    print(f"IMAP Server: {imap_server}")
    
    try:
        # Connect to IMAP server
        print("\nConnecting to IMAP server...")
        mail = imaplib.IMAP4(imap_server)
        mail.starttls()
        
        # Login
        print("Logging in...")
        mail.login(email_user, email_pass)
        print("✅ Login successful!")
        
        # List mailboxes
        print("\nAvailable mailboxes:")
        status, mailboxes = mail.list()
        if status == 'OK':
            for mailbox in mailboxes:
                print(f"  - {mailbox.decode()}")
        
        # Check INBOX
        print("\nChecking INBOX...")
        mail.select('INBOX')
        
        # Search for all emails (not just unread)
        print("Searching for ALL emails...")
        status, messages = mail.search(None, 'ALL')
        
        if status == 'OK':
            email_ids = messages[0].split()
            print(f"Found {len(email_ids)} total emails")
            
            if len(email_ids) > 0:
                print("\nRecent emails:")
                # Get the last 5 emails
                for i in range(min(5, len(email_ids))):
                    email_id = email_ids[-(i+1)]  # Start from the end (most recent)
                    status, msg_data = mail.fetch(email_id, '(RFC822)')
                    
                    if status == 'OK':
                        email_body = msg_data[0][1]
                        email_message = email.message_from_bytes(email_body)
                        
                        # Get subject
                        subject = decode_header(email_message["subject"])[0][0]
                        if isinstance(subject, bytes):
                            subject = subject.decode()
                        
                        # Get from
                        from_addr = email_message["from"]
                        
                        # Get date
                        date = email_message["date"]
                        
                        # Check if read
                        flags = email_message["flags"] if "flags" in email_message else ""
                        is_read = "\\Seen" in flags if flags else False
                        
                        print(f"  Email {email_id.decode()}:")
                        print(f"    From: {from_addr}")
                        print(f"    Subject: {subject}")
                        print(f"    Date: {date}")
                        print(f"    Read: {is_read}")
                        print()
            else:
                print("No emails found in INBOX")
        
        # Now check for unread emails specifically
        print("Searching for UNREAD emails...")
        status, messages = mail.search(None, 'UNSEEN')
        
        if status == 'OK':
            email_ids = messages[0].split()
            print(f"Found {len(email_ids)} unread emails")
            
            if len(email_ids) > 0:
                print("\nUnread emails:")
                for email_id in email_ids:
                    status, msg_data = mail.fetch(email_id, '(RFC822)')
                    
                    if status == 'OK':
                        email_body = msg_data[0][1]
                        email_message = email.message_from_bytes(email_body)
                        
                        subject = decode_header(email_message["subject"])[0][0]
                        if isinstance(subject, bytes):
                            subject = subject.decode()
                        
                        from_addr = email_message["from"]
                        print(f"  - From: {from_addr}, Subject: {subject}")
        
        mail.close()
        mail.logout()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_email_connection() 