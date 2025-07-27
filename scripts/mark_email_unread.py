#!/usr/bin/env python3
"""
Script to mark the most recent email as unread for testing.
"""

import imaplib
import os

def mark_latest_email_unread():
    """Mark the most recent email as unread."""
    
    # Email settings
    EMAIL_HOST = "mailcluster.loopia.se"
    EMAIL_USERNAME = "agent@klasholmgren.se"
    EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD", "40qE7xKJuz")
    
    try:
        # Connect to IMAP server
        print(f"🔍 Connecting to {EMAIL_HOST}...")
        mail = imaplib.IMAP4(EMAIL_HOST)
        
        # Login
        print(f"🔐 Logging in as {EMAIL_USERNAME}...")
        mail.login(EMAIL_USERNAME, EMAIL_PASSWORD)
        
        # Select inbox
        mail.select('INBOX')
        
        # Get all emails
        _, message_numbers = mail.search(None, 'ALL')
        email_list = message_numbers[0].split()
        
        if not email_list:
            print("📭 No emails found")
            return
        
        # Get the most recent email
        latest_email_num = email_list[-1]
        print(f"📧 Marking email {latest_email_num} as unread...")
        
        # Remove the \Seen flag to mark as unread
        mail.store(latest_email_num, '-FLAGS', '\\Seen')
        
        print("✅ Email marked as unread!")
        
        # Verify the change
        _, flags_data = mail.fetch(latest_email_num, '(FLAGS)')
        flags = flags_data[0].decode()
        if '\\Seen' in flags:
            print("❌ Email still appears as read")
        else:
            print("✅ Email is now unread")
        
        mail.close()
        mail.logout()
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    mark_latest_email_unread() 