#!/bin/bash
# Diagnostic script to check why emails to agent@klasholmgren.se aren't being processed

set -e

echo "=== Email Reception Diagnostic ==="
echo ""

# Check production .env configuration
echo "1. Checking production email configuration..."
if [ -f "/opt/pocketflow/.env" ]; then
    echo "   Production .env found"
    echo "   Email settings:"
    grep -E "EMAIL_(HOST|USERNAME|PORT)" /opt/pocketflow/.env | sed 's/\(PASSWORD=\).*/\1***/' || echo "   No email settings found in .env"
else
    echo "   ❌ Production .env not found at /opt/pocketflow/.env"
fi

echo ""
echo "2. Checking recent email logs..."
journalctl -u pocketflow --since "1 hour ago" --no-pager | grep -i "email" | tail -10

echo ""
echo "3. Testing email connection directly..."
sudo -u pocketflow /opt/pocketflow/venv/bin/python << 'PYTHON_SCRIPT'
import sys
import os
sys.path.insert(0, '/opt/pocketflow/src')

# Load environment
from dotenv import load_dotenv
load_dotenv('/opt/pocketflow/.env')

import imaplib
from datetime import datetime, timedelta

EMAIL_HOST = os.getenv('EMAIL_HOST')
EMAIL_USERNAME = os.getenv('EMAIL_USERNAME')
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')

print(f"   Connecting to: {EMAIL_HOST}")
print(f"   Username: {EMAIL_USERNAME}")

try:
    # Connect
    mail = imaplib.IMAP4_SSL(EMAIL_HOST)
    mail.login(EMAIL_USERNAME, EMAIL_PASSWORD)
    print("   ✅ IMAP connection successful")
    
    # Select INBOX
    mail.select('INBOX')
    
    # Check total emails
    status, messages = mail.search(None, 'ALL')
    email_ids = messages[0].split() if messages[0] else []
    print(f"   📧 Total emails in INBOX: {len(email_ids)}")
    
    # Check unread emails
    status, messages = mail.search(None, 'UNSEEN')
    unread_ids = messages[0].split() if messages[0] else []
    print(f"   📧 Unread emails: {len(unread_ids)}")
    
    # Check recent emails (last 24 hours)
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%d-%b-%Y")
    status, messages = mail.search(None, f'SINCE {yesterday}')
    recent_ids = messages[0].split() if messages[0] else []
    print(f"   📧 Recent emails (since {yesterday}): {len(recent_ids)}")
    
    # Check emails to agent@klasholmgren.se
    status, messages = mail.search(None, 'TO agent@klasholmgren.se')
    to_agent_ids = messages[0].split() if messages[0] else []
    print(f"   📧 Emails TO agent@klasholmgren.se: {len(to_agent_ids)}")
    
    # Check recent unread emails to agent
    status, messages = mail.search(None, f'(UNSEEN TO agent@klasholmgren.se SINCE {yesterday})')
    recent_unread_to_agent = messages[0].split() if messages[0] else []
    print(f"   📧 Recent unread emails TO agent@klasholmgren.se: {len(recent_unread_to_agent)}")
    
    # Show details of recent unread emails
    if recent_unread_to_agent:
        print("   Recent unread emails to agent:")
        for email_id in recent_unread_to_agent[-5:]:  # Last 5
            status, msg_data = mail.fetch(email_id, '(RFC822)')
            if msg_data[0]:
                import email
                email_body = msg_data[0][1]
                email_message = email.message_from_bytes(email_body)
                subject = email_message['Subject'] or '(No Subject)'
                from_addr = email_message['From'] or 'Unknown'
                date = email_message['Date'] or 'Unknown'
                print(f"      - ID: {email_id.decode()}, From: {from_addr}, Subject: {subject[:50]}, Date: {date}")
    
    mail.close()
    mail.logout()
    
except Exception as e:
    print(f"   ❌ Error: {e}")
    import traceback
    traceback.print_exc()

PYTHON_SCRIPT

echo ""
echo "4. Checking if emails might be in other folders..."
sudo -u pocketflow /opt/pocketflow/venv/bin/python << 'PYTHON_SCRIPT'
import sys
import os
sys.path.insert(0, '/opt/pocketflow/src')

from dotenv import load_dotenv
load_dotenv('/opt/pocketflow/.env')

import imaplib

EMAIL_HOST = os.getenv('EMAIL_HOST')
EMAIL_USERNAME = os.getenv('EMAIL_USERNAME')
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')

try:
    mail = imaplib.IMAP4_SSL(EMAIL_HOST)
    mail.login(EMAIL_USERNAME, EMAIL_PASSWORD)
    
    # List all folders
    status, folders = mail.list()
    print("   Available folders:")
    for folder in folders[:10]:  # First 10 folders
        print(f"      {folder.decode()}")
    
    mail.logout()
except Exception as e:
    print(f"   ❌ Error listing folders: {e}")

PYTHON_SCRIPT

echo ""
echo "=== Diagnostic Complete ==="
