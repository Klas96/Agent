#!/usr/bin/env python3
"""
Simple email checker to see what emails are in the inbox.
"""

import imaplib
import email
from email.header import decode_header
import os

def check_emails():
    """Check recent emails in the inbox."""
    
    # Email settings from .env
    EMAIL_HOST = "mailcluster.loopia.se"
    EMAIL_USERNAME = "agent@klasholmgren.se"
    EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD", "")
    
    if not EMAIL_PASSWORD:
        print("❌ EMAIL_PASSWORD not set in environment")
        return
    
    try:
        # Connect to IMAP server
        print(f"🔍 Connecting to {EMAIL_HOST}...")
        mail = imaplib.IMAP4(EMAIL_HOST)
        
        # Login
        print(f"🔐 Logging in as {EMAIL_USERNAME}...")
        mail.login(EMAIL_USERNAME, EMAIL_PASSWORD)
        
        # Select inbox
        mail.select('INBOX')
        
        # Search for recent emails (last 7 days)
        print("📧 Searching for recent emails...")
        _, message_numbers = mail.search(None, 'ALL')
        
        email_list = message_numbers[0].split()
        
        if not email_list:
            print("📭 No emails found in inbox")
            return
        
        print(f"📬 Found {len(email_list)} emails in inbox")
        
        # Get the 5 most recent emails
        recent_emails = email_list[-5:] if len(email_list) > 5 else email_list
        
        for i, num in enumerate(recent_emails, 1):
            _, msg_data = mail.fetch(num, '(RFC822)')
            email_body = msg_data[0][1]
            email_message = email.message_from_bytes(email_body)
            
            # Decode subject
            subject = decode_header(email_message["subject"])[0][0]
            if isinstance(subject, bytes):
                subject = subject.decode()
            
            # Decode sender
            sender = decode_header(email_message["from"])[0][0]
            if isinstance(sender, bytes):
                sender = sender.decode()
            
            # Get date
            date = email_message["date"]
            
            print(f"\n📧 Email {i}:")
            print(f"   From: {sender}")
            print(f"   Subject: {subject}")
            print(f"   Date: {date}")
            
            # Check if email is marked as read/unread
            _, flags_data = mail.fetch(num, '(FLAGS)')
            flags = flags_data[0].decode()
            if '\\Seen' in flags:
                status = "📖 Read"
            else:
                status = "📨 Unread"
            print(f"   Status: {status}")
        
        mail.close()
        mail.logout()
        
    except Exception as e:
        print(f"❌ Error checking emails: {e}")

if __name__ == "__main__":
    check_emails() 