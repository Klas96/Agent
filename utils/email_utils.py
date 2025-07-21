import os
import imaplib
import email
import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

def fetch_unread():
    """Fetch unread emails using IMAP."""
    try:
        # Get email configuration from environment
        email_user = os.getenv('EMAIL_USER')
        email_pass = os.getenv('EMAIL_PASS')
        imap_server = os.getenv('IMAP_SERVER')
        
        if not all([email_user, email_pass, imap_server]):
            logger.warning("Email configuration incomplete. Check EMAIL_USER, EMAIL_PASS, IMAP_SERVER")
            return []
        
        # Connect to IMAP server
        mail = imaplib.IMAP4_SSL(imap_server)
        mail.login(email_user, email_pass)
        mail.select('INBOX')
        
        # Search for unread emails
        status, messages = mail.search(None, 'UNSEEN')
        
        emails = []
        if status == 'OK':
            for num in messages[0].split():
                status, msg_data = mail.fetch(num, '(RFC822)')
                if status == 'OK':
                    email_body = msg_data[0][1]
                    email_message = email.message_from_bytes(email_body)
                    
                    # Extract email details
                    subject = email_message.get('Subject', '')
                    sender = email_message.get('From', '')
                    date = email_message.get('Date', '')
                    message_id = email_message.get('Message-ID', '')
                    
                    # Get email body
                    body = ""
                    if email_message.is_multipart():
                        for part in email_message.walk():
                            if part.get_content_type() == "text/plain":
                                body = part.get_payload(decode=True).decode()
                                break
                    else:
                        body = email_message.get_payload(decode=True).decode()
                    
                    emails.append({
                        'id': num.decode(),
                        'subject': subject,
                        'from': sender,
                        'body': body,
                        'date': date,
                        'message_id': message_id,
                        'thread_id': message_id or subject  # Use Message-ID if available, fallback to subject
                    })
        
        mail.close()
        mail.logout()
        return emails
        
    except Exception as e:
        logger.error(f"Error fetching emails: {e}")
        return []

def send_email(to_email, subject, body, attachment_path=None, cc=None, in_reply_to=None, references=None):
    """Send an email using SMTP."""
    try:
        # Get email configuration
        email_user = os.getenv('EMAIL_USER')
        email_pass = os.getenv('EMAIL_PASS')
        smtp_server = os.getenv('SMTP_SERVER')
        smtp_port = int(os.getenv('SMTP_PORT', '587'))
        
        if not all([email_user, email_pass, smtp_server]):
            logger.error("SMTP configuration incomplete")
            return False
        
        # Create message
        msg = MIMEMultipart()
        msg['From'] = email_user
        msg['To'] = to_email
        msg['Subject'] = subject
        
        # Add threading headers for replies
        if in_reply_to:
            msg['In-Reply-To'] = in_reply_to
        if references:
            msg['References'] = references
        
        if cc:
            msg['Cc'] = cc
        
        # Add body
        msg.attach(MIMEText(body, 'plain'))
        
        # Add attachment if provided
        if attachment_path and os.path.exists(attachment_path):
            with open(attachment_path, "rb") as attachment:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(attachment.read())
            
            encoders.encode_base64(part)
            part.add_header(
                'Content-Disposition',
                f'attachment; filename= {os.path.basename(attachment_path)}'
            )
            msg.attach(part)
        
        # Send email
        server = smtplib.SMTP(smtp_server, smtp_port, timeout=30)  # Add 30 second timeout
        server.starttls()
        server.login(email_user, email_pass)
        
        recipients = [to_email]
        if cc:
            recipients.extend(cc.split(','))
        
        server.sendmail(email_user, recipients, msg.as_string())
        server.quit()
        
        logger.info(f"Email sent to {to_email}")
        return True
        
    except Exception as e:
        logger.error(f"Error sending email: {e}")
        return False

def mark_as_read(email_id):
    """Mark an email as read."""
    try:
        email_user = os.getenv('EMAIL_USER')
        email_pass = os.getenv('EMAIL_PASS')
        imap_server = os.getenv('IMAP_SERVER')
        
        if not all([email_user, email_pass, imap_server]):
            return False
        
        mail = imaplib.IMAP4_SSL(imap_server)
        mail.login(email_user, email_pass)
        mail.select('INBOX')
        
        # Mark as read by removing UNSEEN flag
        mail.store(email_id, '+FLAGS', '\\Seen')
        mail.close()
        mail.logout()
        
        return True
        
    except Exception as e:
        logger.error(f"Error marking email as read: {e}")
        return False

def load_greenlist():
    """Load greenlist emails from environment or file."""
    # For now, return a simple greenlist
    # You can extend this to load from a file or database
    return [
        "klas0holmgren@gmail.com",
        "nallenalle99@gmail.com"
    ]
