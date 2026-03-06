#!/usr/bin/env python3
"""
Test email content to see what's in recent emails.
"""

import os
import imaplib
import email
from email.header import decode_header

def test_email_content():
    """Test email content of recent emails."""
    
    print("Testing email content...")
    
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
        
        # Get the last 3 emails
        status, messages = mail.search(None, 'ALL')
        if status == 'OK':
            email_ids = messages[0].split()
            
            print(f"\nChecking the last 3 emails:")
            for i in range(min(3, len(email_ids))):
                email_id = email_ids[-(i+1)]
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
                    
                    print(f"\nEmail {email_id.decode()}:")
                    print(f"  From: {from_addr}")
                    print(f"  Subject: '{subject}'")
                    print(f"  Date: {date}")
                    
                    # Get email body
                    body = ""
                    if email_message.is_multipart():
                        for part in email_message.walk():
                            if part.get_content_type() == "text/plain":
                                body = part.get_payload(decode=True).decode()
                                break
                    else:
                        body = email_message.get_payload(decode=True).decode()
                    
                    print(f"  Body: '{body[:200]}...'")
                    print(f"  Body length: {len(body)} characters")
        
        mail.close()
        mail.logout()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_email_content() 