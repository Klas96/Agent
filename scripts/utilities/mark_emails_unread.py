#!/usr/bin/env python3
import imaplib

def mark_emails_unread():
    server = imaplib.IMAP4_SSL('mailcluster.loopia.se')
    server.login('agent@klasholmgren.se', '40qE7xKJuz')
    server.select('INBOX')
    
    # Get all emails
    _, data = server.search(None, 'ALL')
    email_ids = data[0].split()
    
    # Mark the 5 most recent emails as unread
    recent_ids = email_ids[-5:]  # Last 5 emails
    
    print(f"Marking {len(recent_ids)} recent emails as unread...")
    
    for email_id in recent_ids:
        try:
            # Remove the SEEN flag to mark as unread
            server.store(email_id, '-FLAGS', '\\Seen')
            print(f"Marked email {email_id.decode()} as unread")
        except Exception as e:
            print(f"Failed to mark email {email_id.decode()} as unread: {e}")
    
    # Verify unread count
    _, unread_data = server.search(None, 'UNSEEN')
    unread_count = len(unread_data[0].split())
    print(f"\nTotal unread emails: {unread_count}")
    
    server.close()

if __name__ == "__main__":
    mark_emails_unread() 