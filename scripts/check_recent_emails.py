#!/usr/bin/env python3
"""
Check recent emails in the inbox.
"""

import os
import sys
import imaplib
import email
from email.header import decode_header
from datetime import datetime, timedelta

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from pocketflow.config.settings import get_settings

def check_recent_emails():
    """Check recent emails in the inbox."""
    settings = get_settings()
    
    # Connect to IMAP server
    imap_server = settings.email.imap_server
    imap_port = settings.email.imap_port
    email_address = settings.email.email_address
    password = settings.email.password
    
    print(f"Connecting to {imap_server}:{imap_port}...")
    
    try:
        # Connect to the IMAP server
        mail = imaplib.IMAP4_SSL(imap_server, imap_port)
        mail.login(email_address, password)
        
        # Select the inbox
        mail.select('INBOX')
        
        # Search for emails from the last 24 hours
        yesterday = datetime.now() - timedelta(days=1)
        date_str = yesterday.strftime("%d-%b-%Y")
        
        # Search for recent emails (both read and unread)
        status, messages = mail.search(None, f'SINCE {date_str}')
        
        if status != 'OK':
            print("Failed to search emails")
            return
        
        email_ids = messages[0].split()
        print(f"Found {len(email_ids)} emails since {date_str}")
        
        if not email_ids:
            print("No recent emails found")
            return
        
        # Get the last 10 emails
        recent_ids = email_ids[-10:] if len(email_ids) > 10 else email_ids
        
        print(f"\nChecking last {len(recent_ids)} emails:")
        print("-" * 80)
        
        for email_id in recent_ids:
            status, msg_data = mail.fetch(email_id, '(RFC822)')
            
            if status != 'OK':
                continue
            
            email_body = msg_data[0][1]
            email_message = email.message_from_bytes(email_body)
            
            # Get email details
            subject = decode_header(email_message["subject"])[0][0]
            if isinstance(subject, bytes):
                subject = subject.decode()
            
            from_addr = decode_header(email_message["from"])[0][0]
            if isinstance(from_addr, bytes):
                from_addr = from_addr.decode()
            
            date = email_message["date"]
            
            # Check if email is read/unread
            status, flags_data = mail.fetch(email_id, '(FLAGS)')
            flags = flags_data[0].decode()
            is_read = '\\Seen' in flags
            
            print(f"ID: {email_id.decode()}")
            print(f"From: {from_addr}")
            print(f"Subject: {subject}")
            print(f"Date: {date}")
            print(f"Read: {'Yes' if is_read else 'No'}")
            print("-" * 80)
        
        mail.close()
        mail.logout()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_recent_emails() 