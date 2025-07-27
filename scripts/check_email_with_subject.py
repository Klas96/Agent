#!/usr/bin/env python3
"""
Check emails with subjects to find specific emails.
"""

import imaplib
import email
from email.header import decode_header
import os

def check_emails_with_subjects():
    """Check recent emails and show those with subjects."""
    
    # Email settings from .env
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
        
        # Search for recent emails
        print("📧 Searching for recent emails...")
        _, message_numbers = mail.search(None, 'ALL')
        
        email_list = message_numbers[0].split()
        
        if not email_list:
            print("📭 No emails found in inbox")
            return
        
        print(f"📬 Found {len(email_list)} emails in inbox")
        
        # Get the 10 most recent emails
        recent_emails = email_list[-10:] if len(email_list) > 10 else email_list
        
        emails_with_subjects = []
        
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
            
            # Check if email is marked as read/unread
            _, flags_data = mail.fetch(num, '(FLAGS)')
            flags = flags_data[0].decode()
            if '\\Seen' in flags:
                status = "📖 Read"
            else:
                status = "📨 Unread"
            
            # Only show emails with subjects or specific content
            if subject and subject.strip():
                emails_with_subjects.append({
                    'num': num,
                    'sender': sender,
                    'subject': subject,
                    'date': date,
                    'status': status
                })
                print(f"\n📧 Email {i} (with subject):")
                print(f"   From: {sender}")
                print(f"   Subject: {subject}")
                print(f"   Date: {date}")
                print(f"   Status: {status}")
            
            # Also check for emails with "What is my Name?" in body
            try:
                if email_message.is_multipart():
                    for part in email_message.walk():
                        if part.get_content_type() == "text/plain":
                            body = part.get_payload(decode=True).decode()
                            if "What is my Name?" in body:
                                print(f"\n🎯 Found 'What is my Name?' email:")
                                print(f"   From: {sender}")
                                print(f"   Subject: {subject}")
                                print(f"   Date: {date}")
                                print(f"   Status: {status}")
                                print(f"   Body preview: {body[:100]}...")
                else:
                    body = email_message.get_payload(decode=True).decode()
                    if "What is my Name?" in body:
                        print(f"\n🎯 Found 'What is my Name?' email:")
                        print(f"   From: {sender}")
                        print(f"   Subject: {subject}")
                        print(f"   Date: {date}")
                        print(f"   Status: {status}")
                        print(f"   Body preview: {body[:100]}...")
            except Exception as e:
                pass  # Skip if can't decode body
        
        if not emails_with_subjects:
            print("\n📭 No emails with subjects found in recent emails")
        
        mail.close()
        mail.logout()
        
    except Exception as e:
        print(f"❌ Error checking emails: {e}")

if __name__ == "__main__":
    check_emails_with_subjects() 