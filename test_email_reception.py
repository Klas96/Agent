#!/usr/bin/env python3
"""
Test script to check if emails to agent@klasholmgren.se are being received.
Run this to diagnose why emails aren't being processed.
"""

import imaplib
import email
from email.header import decode_header
from datetime import datetime, timedelta
import os
import sys

# Try to load from production .env first, then development
from dotenv import load_dotenv

# Try production first
if os.path.exists("/opt/pocketflow/.env"):
    load_dotenv("/opt/pocketflow/.env")
    print("📁 Loaded production .env from /opt/pocketflow/.env")
else:
    load_dotenv()
    print("📁 Loaded .env from current directory")

EMAIL_HOST = os.getenv('EMAIL_HOST', 'mailcluster.loopia.se')
EMAIL_USERNAME = os.getenv('EMAIL_USERNAME', 'agent@klasholmgren.se')
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')

if not EMAIL_PASSWORD:
    print("❌ ERROR: EMAIL_PASSWORD not found in environment variables")
    print("   Please set EMAIL_PASSWORD in your .env file")
    sys.exit(1)

print("=" * 60)
print("Email Reception Diagnostic")
print("=" * 60)
print(f"Host: {EMAIL_HOST}")
print(f"Username: {EMAIL_USERNAME}")
print(f"Password: {'*' * len(EMAIL_PASSWORD) if EMAIL_PASSWORD else 'NOT SET'}")
print()

try:
    # Connect to IMAP server
    print("🔍 Connecting to IMAP server...")
    mail = imaplib.IMAP4_SSL(EMAIL_HOST)
    
    # Login
    print("🔐 Logging in...")
    mail.login(EMAIL_USERNAME, EMAIL_PASSWORD)
    print("✅ Login successful!")
    
    # Select INBOX
    print("📂 Selecting INBOX...")
    status, messages = mail.select('INBOX')
    print(f"   Status: {status}")
    if messages[0]:
        print(f"   Total messages in INBOX: {messages[0].decode()}")
    
    print()
    print("=" * 60)
    print("Email Statistics")
    print("=" * 60)
    
    # Check total emails
    status, messages = mail.search(None, 'ALL')
    email_ids = messages[0].split() if messages[0] else []
    print(f"📧 Total emails in INBOX: {len(email_ids)}")
    
    # Check unread emails
    status, messages = mail.search(None, 'UNSEEN')
    unread_ids = messages[0].split() if messages[0] else []
    print(f"📧 Unread emails: {len(unread_ids)}")
    
    # Check recent emails (last 24 hours)
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%d-%b-%Y")
    status, messages = mail.search(None, f'SINCE {yesterday}')
    recent_ids = messages[0].split() if messages[0] else []
    print(f"📧 Recent emails (since {yesterday}): {len(recent_ids)}")
    
    # Check emails TO agent@klasholmgren.se
    status, messages = mail.search(None, 'TO agent@klasholmgren.se')
    to_agent_ids = messages[0].split() if messages[0] else []
    print(f"📧 Emails TO agent@klasholmgren.se: {len(to_agent_ids)}")
    
    # Check recent unread emails to agent
    status, messages = mail.search(None, f'(UNSEEN TO agent@klasholmgren.se SINCE {yesterday})')
    recent_unread_to_agent = messages[0].split() if messages[0] else []
    print(f"📧 Recent unread emails TO agent@klasholmgren.se: {len(recent_unread_to_agent)}")
    
    print()
    print("=" * 60)
    print("Recent Unread Emails to agent@klasholmgren.se")
    print("=" * 60)
    
    if recent_unread_to_agent:
        print(f"Found {len(recent_unread_to_agent)} recent unread emails:")
        for i, email_id in enumerate(recent_unread_to_agent[-10:], 1):  # Last 10
            try:
                status, msg_data = mail.fetch(email_id, '(RFC822 FLAGS)')
                if msg_data[0]:
                    email_body = msg_data[0][1]
                    email_message = email.message_from_bytes(email_body)
                    
                    # Get flags
                    flags = msg_data[0][0].decode() if len(msg_data) > 0 else ""
                    is_unread = '\\Seen' not in flags
                    
                    # Decode subject
                    subject_header = email_message['Subject']
                    if subject_header:
                        subject = decode_header(subject_header)[0][0]
                        if isinstance(subject, bytes):
                            subject = subject.decode()
                    else:
                        subject = "(No Subject)"
                    
                    from_addr = email_message['From'] or 'Unknown'
                    date = email_message['Date'] or 'Unknown'
                    
                    status_icon = "📨" if is_unread else "📖"
                    print(f"\n{status_icon} Email {i} (ID: {email_id.decode()}):")
                    print(f"   From: {from_addr}")
                    print(f"   Subject: {subject}")
                    print(f"   Date: {date}")
                    print(f"   Status: {'Unread' if is_unread else 'Read'}")
            except Exception as e:
                print(f"   ❌ Error reading email {email_id}: {e}")
    else:
        print("❌ No recent unread emails found to agent@klasholmgren.se")
        print()
        print("Possible reasons:")
        print("1. No emails have been sent to agent@klasholmgren.se")
        print("2. Emails are being marked as read automatically")
        print("3. Emails are going to a different folder (Spam, etc.)")
        print("4. Email server is filtering emails before they reach INBOX")
    
    print()
    print("=" * 60)
    print("All Recent Emails (Last 5, regardless of read status)")
    print("=" * 60)
    
    if recent_ids:
        print(f"Showing last 5 recent emails:")
        for i, email_id in enumerate(recent_ids[-5:], 1):
            try:
                status, msg_data = mail.fetch(email_id, '(RFC822 FLAGS)')
                if msg_data[0]:
                    email_body = msg_data[0][1]
                    email_message = email.message_from_bytes(email_body)
                    
                    # Get flags
                    flags = msg_data[0][0].decode() if len(msg_data) > 0 else ""
                    is_unread = '\\Seen' not in flags
                    
                    subject_header = email_message['Subject']
                    if subject_header:
                        subject = decode_header(subject_header)[0][0]
                        if isinstance(subject, bytes):
                            subject = subject.decode()
                    else:
                        subject = "(No Subject)"
                    
                    from_addr = email_message['From'] or 'Unknown'
                    to_addr = email_message['To'] or 'Unknown'
                    date = email_message['Date'] or 'Unknown'
                    
                    status_icon = "📨" if is_unread else "📖"
                    print(f"\n{status_icon} Email {i} (ID: {email_id.decode()}):")
                    print(f"   From: {from_addr}")
                    print(f"   To: {to_addr}")
                    print(f"   Subject: {subject}")
                    print(f"   Date: {date}")
                    print(f"   Status: {'Unread' if is_unread else 'Read'}")
            except Exception as e:
                print(f"   ❌ Error reading email {email_id}: {e}")
    else:
        print("No recent emails found")
    
    # Check other folders
    print()
    print("=" * 60)
    print("Available Folders")
    print("=" * 60)
    status, folders = mail.list()
    print("Available folders:")
    for folder in folders[:15]:  # First 15 folders
        print(f"   {folder.decode()}")
    
    mail.close()
    mail.logout()
    print()
    print("✅ Diagnostic complete!")
    
except imaplib.IMAP4.error as e:
    print(f"❌ IMAP Error: {e}")
    print("   Check your email credentials and server settings")
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
