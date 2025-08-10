#!/usr/bin/env python3
"""
Simple test to check why emails aren't being processed as unread.
"""

import os
import imaplib
import email
from datetime import datetime, timedelta

# Load environment from production
import sys
sys.path.insert(0, "/opt/pocketflow")

try:
    from dotenv import load_dotenv
    load_dotenv("/opt/pocketflow/.env")
except:
    pass

def check_unread_emails():
    """Check for unread emails and mark one as unread for testing."""
    
    email_host = os.getenv("EMAIL_HOST")
    email_username = os.getenv("EMAIL_USERNAME") 
    email_password = os.getenv("EMAIL_PASSWORD")
    
    print(f"🔧 Connecting to {email_host} as {email_username}")
    
    try:
        # Connect to IMAP
        mail = imaplib.IMAP4_SSL(email_host)
        mail.login(email_username, email_password)
        mail.select('inbox')
        
        # Check current unread count
        status, unread_messages = mail.search(None, 'UNSEEN')
        unread_count = len(unread_messages[0].split()) if unread_messages[0] else 0
        print(f"📧 Current unread emails: {unread_count}")
        
        if unread_count == 0:
            print("🔄 No unread emails found. Looking for recent emails to mark as unread...")
            
            # Find recent emails from you
            since_date = (datetime.now() - timedelta(hours=2)).strftime("%d-%b-%Y")
            status, messages = mail.search(None, f'FROM "klas0holmgren@gmail.com" SINCE {since_date}')
            
            if status == 'OK' and messages[0]:
                recent_emails = messages[0].split()
                print(f"📬 Found {len(recent_emails)} recent emails from you")
                
                for email_id in recent_emails[-3:]:  # Check last 3 emails
                    # Get email details
                    status, msg_data = mail.fetch(email_id, '(RFC822)')
                    if status == 'OK':
                        email_message = email.message_from_bytes(msg_data[0][1])
                        subject = email_message['Subject'] or 'No Subject'
                        body = ""
                        
                        # Get email body
                        if email_message.is_multipart():
                            for part in email_message.walk():
                                if part.get_content_type() == "text/plain":
                                    body = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                                    break
                        else:
                            body = email_message.get_payload(decode=True).decode('utf-8', errors='ignore')
                        
                        print(f"\n📧 Email ID: {email_id.decode()}")
                        print(f"   Subject: {subject}")
                        print(f"   Body preview: {body[:100]}...")
                        
                        # Check if this looks like a podcast request
                        if any(keyword in body.lower() for keyword in ['podcast', 'generate', 'local llm']):
                            print(f"🎙️ This looks like a podcast request! Marking as unread...")
                            
                            # Mark as unread
                            mail.store(email_id, '-FLAGS', '\\Seen')
                            print(f"✅ Marked email {email_id.decode()} as unread")
                            break
            else:
                print("❌ No recent emails found from you")
        else:
            print(f"✅ Found {unread_count} unread emails already")
            
            # Show details of unread emails
            for email_id in unread_messages[0].split()[:3]:  # Show first 3
                status, msg_data = mail.fetch(email_id, '(RFC822)')
                if status == 'OK':
                    email_message = email.message_from_bytes(msg_data[0][1])
                    subject = email_message['Subject'] or 'No Subject'
                    print(f"📧 Unread email: {subject}")
        
        # Final check
        status, unread_after = mail.search(None, 'UNSEEN')
        unread_count_after = len(unread_after[0].split()) if unread_after[0] else 0
        print(f"\n📊 Final unread count: {unread_count_after}")
        
        mail.close()
        mail.logout()
        
        return unread_count_after > 0
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Simple Email Unread Test")
    print("=" * 40)
    print(f"Time: {datetime.now().isoformat()}")
    print()
    
    success = check_unread_emails()
    
    if success:
        print("\n✅ There are now unread emails for PocketFlow to process!")
        print("💡 The PocketFlow service should pick them up within 10 seconds.")
    else:
        print("\n⚠️  Still no unread emails. Try sending a new email to agent@klasholmgren.se") 