#!/usr/bin/env python3
"""
Debug script to understand email processing issues.
"""

import os
import imaplib
import email
from datetime import datetime, timedelta
import sys

# Add the source directory to the path
sys.path.insert(0, "/opt/pocketflow/src")

def debug_email_processing():
    """Debug email processing to understand why emails aren't detected."""
    
    print("🔍 Email Processing Debug")
    print("=" * 50)
    print(f"Time: {datetime.now()}")
    
    try:
        # Load environment variables from production
        import dotenv
        dotenv.load_dotenv("/opt/pocketflow/.env")
        
        email_host = os.getenv("EMAIL_HOST")
        email_username = os.getenv("EMAIL_USERNAME") 
        email_password = os.getenv("EMAIL_PASSWORD")
        
        print(f"🔧 Connecting to {email_host} as {email_username}")
        
        # Connect to IMAP
        mail = imaplib.IMAP4_SSL(email_host)
        mail.login(email_username, email_password)
        
        # Select INBOX
        mail.select('INBOX')
        
        # Check total emails
        status, messages = mail.search(None, 'ALL')
        email_ids = messages[0].split()
        print(f"📧 Total emails in inbox: {len(email_ids)}")
        
        # Check unread emails
        status, messages = mail.search(None, 'UNSEEN')
        unread_ids = messages[0].split()
        print(f"📧 Unread emails: {len(unread_ids)}")
        
        # Check recent emails (last 24 hours)
        yesterday = (datetime.now() - timedelta(days=1)).strftime("%d-%b-%Y")
        status, messages = mail.search(None, f'SINCE {yesterday}')
        recent_ids = messages[0].split()
        print(f"📧 Recent emails (since {yesterday}): {len(recent_ids)}")
        
        # Check emails from the user
        status, messages = mail.search(None, 'FROM klas0holmgren@gmail.com')
        user_emails = messages[0].split()
        print(f"📧 Emails from klas0holmgren@gmail.com: {len(user_emails)}")
        
        # Check recent emails from user
        status, messages = mail.search(None, f'FROM klas0holmgren@gmail.com SINCE {yesterday}')
        recent_user_emails = messages[0].split()
        print(f"📧 Recent emails from user: {len(recent_user_emails)}")
        
        if recent_user_emails:
            print("\n📋 Recent emails from user:")
            for i, email_id in enumerate(recent_user_emails[-5:]):  # Last 5
                status, msg_data = mail.fetch(email_id, '(RFC822)')
                email_body = msg_data[0][1]
                email_message = email.message_from_bytes(email_body)
                
                subject = email_message.get('subject', 'No subject')
                date = email_message.get('date', 'No date')
                print(f"  {i+1}. Subject: {subject}")
                print(f"     Date: {date}")
                print(f"     ID: {email_id.decode()}")
                
                # Check if this email is marked as read
                status, flags = mail.fetch(email_id, '(FLAGS)')
                flags_str = flags[0].decode()
                if '\\Seen' in flags_str:
                    print(f"     Status: READ")
                else:
                    print(f"     Status: UNREAD")
                print()
        
        # Check if there are any emails that could be marked as unread
        if recent_user_emails:
            print("🔄 Attempting to mark most recent email as unread...")
            latest_email_id = recent_user_emails[-1]
            
            # Mark as unread
            mail.store(latest_email_id, '-FLAGS', '\\Seen')
            
            # Verify
            status, flags = mail.fetch(latest_email_id, '(FLAGS)')
            flags_str = flags[0].decode()
            if '\\Seen' in flags_str:
                print("❌ Failed to mark as unread")
            else:
                print("✅ Successfully marked as unread")
        
        mail.close()
        mail.logout()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_email_processing() 