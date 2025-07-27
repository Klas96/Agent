#!/usr/bin/env python3
import imaplib
import email

def check_recent_emails():
    server = imaplib.IMAP4_SSL('mailcluster.loopia.se')
    server.login('agent@klasholmgren.se', '40qE7xKJuz')
    server.select('INBOX')
    
    # Get all emails
    _, data = server.search(None, 'ALL')
    email_ids = data[0].split()
    print(f"Total emails: {len(email_ids)}")
    
    # Get recent emails
    recent_ids = email_ids[-5:]  # Last 5 emails
    print("\nMost recent 5 emails:")
    
    for email_id in recent_ids:
        try:
            _, msg_data = server.fetch(email_id, '(RFC822.HEADER)')
            email_message = email.message_from_bytes(msg_data[0][1])
            subject = email_message.get('Subject', 'No subject')
            from_addr = email_message.get('From', 'Unknown')
            print(f"Email {email_id.decode()}: {subject} (from: {from_addr})")
        except Exception as e:
            print(f"Email {email_id.decode()}: Error reading - {e}")
    
    server.close()

if __name__ == "__main__":
    check_recent_emails() 