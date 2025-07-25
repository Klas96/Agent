"""
Email service for PocketFlow.

This module provides email functionality including fetching, sending, and managing emails.
"""

import smtplib
import imaplib
import email
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging

from ..core.types import EmailData, EmailSendRequest
from ..config.settings import get_settings
from ..utils.errors import EmailError, RetryableError
from ..utils.logging import get_logger


class EmailService:
    """Service for handling email operations."""
    
    def __init__(self):
        self.settings = get_settings()
        self.logger = get_logger("EmailService")
        self._smtp_connection = None
        self._imap_connection = None
    
    def fetch_unread_emails(self) -> List[EmailData]:
        """
        Fetch unread emails from the configured email account.
        
        Returns:
            List of EmailData objects representing unread emails
            
        Raises:
            EmailError: If email fetching fails
        """
        imap_server = None
        try:
            self.logger.info("Fetching unread emails...")
            
            # Create a fresh IMAP connection for this operation
            imap_server = imaplib.IMAP4_SSL(self.settings.EMAIL_HOST)
            imap_server.login(self.settings.EMAIL_USERNAME, self.settings.EMAIL_PASSWORD)
            imap_server.select('INBOX')
            
            # Search for unread emails
            _, message_numbers = imap_server.search(None, 'UNSEEN')
            
            emails = []
            for num in message_numbers[0].split():
                try:
                    _, msg_data = imap_server.fetch(num, '(RFC822)')
                    email_body = msg_data[0][1]
                    email_message = email.message_from_bytes(email_body)
                    
                    # Extract email data
                    email_data = self._parse_email_message(email_message, num.decode())
                    if email_data:
                        emails.append(email_data)
                        
                except Exception as e:
                    self.logger.warning(f"Failed to parse email {num}: {e}")
                    continue
            
            self.logger.info(f"Fetched {len(emails)} unread emails")
            return emails
            
        except Exception as e:
            self.logger.error(f"Failed to fetch emails: {e}")
            raise EmailError(f"Email fetching failed: {e}")
        finally:
            if imap_server:
                try:
                    imap_server.close()
                except Exception as e:
                    self.logger.warning(f"Error closing IMAP connection: {e}")
    
    def send_email(self, request: EmailSendRequest) -> bool:
        """
        Send an email with optional attachment.
        
        Args:
            request: EmailSendRequest containing email details
            
        Returns:
            True if email sent successfully
            
        Raises:
            EmailError: If email sending fails
        """
        try:
            self.logger.info(f"Sending email to: {request.to}")
            
            # Create message
            msg = MIMEMultipart()
            msg['From'] = self.settings.EMAIL_USERNAME
            msg['To'] = request.to
            if request.cc:
                msg['Cc'] = request.cc
            msg['Subject'] = request.subject
            
            # Add body
            msg.attach(MIMEText(request.body, 'plain'))
            
            # Add attachment if specified
            if request.attachment:
                self._add_attachment(msg, request.attachment)
            
            # Send email
            smtp_server = self._get_smtp_server()
            recipients = [request.to]
            if request.cc:
                recipients.extend(request.cc.split(','))
            
            smtp_server.send_message(msg)
            smtp_server.quit()
            
            self.logger.info(f"Email sent successfully to {request.to}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to send email: {e}")
            raise EmailError(f"Email sending failed: {e}")
    
    def mark_as_read(self, email_id: str) -> bool:
        """
        Mark an email as read.
        
        Args:
            email_id: ID of the email to mark as read
            
        Returns:
            True if successfully marked as read
        """
        imap_server = None
        try:
            self.logger.info(f"Marking email {email_id} as read")
            
            # Create a fresh IMAP connection for this operation
            imap_server = imaplib.IMAP4_SSL(self.settings.EMAIL_HOST)
            imap_server.login(self.settings.EMAIL_USERNAME, self.settings.EMAIL_PASSWORD)
            imap_server.select('INBOX')
            
            # Mark as read by removing UNSEEN flag
            imap_server.store(email_id, '+FLAGS', '\\Seen')
            
            self.logger.info(f"Email {email_id} marked as read")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to mark email as read: {e}")
            return False
        finally:
            if imap_server:
                try:
                    imap_server.close()
                except Exception as e:
                    self.logger.warning(f"Error closing IMAP connection: {e}")
    
    def _get_smtp_server(self) -> smtplib.SMTP:
        """Get SMTP server connection."""
        if self._smtp_connection is None:
            self._smtp_connection = smtplib.SMTP(
                self.settings.EMAIL_HOST, 
                self.settings.EMAIL_PORT
            )
            if self.settings.EMAIL_USE_TLS:
                self._smtp_connection.starttls()
            self._smtp_connection.login(
                self.settings.EMAIL_USERNAME, 
                self.settings.EMAIL_PASSWORD
            )
        return self._smtp_connection
    
    def _get_imap_server(self) -> imaplib.IMAP4_SSL:
        """Get IMAP server connection."""
        if self._imap_connection is None:
            self._imap_connection = imaplib.IMAP4_SSL(self.settings.EMAIL_HOST)
        return self._imap_connection
    
    def _parse_email_message(self, email_message: email.message.Message, email_id: str) -> Optional[EmailData]:
        """Parse email message into EmailData object."""
        try:
            # Extract headers
            subject = email_message.get('Subject', '')
            from_header = email_message.get('From', '')
            to_header = email_message.get('To', '')
            
            # Extract body
            body = self._get_email_body(email_message)
            
            # Extract thread ID (using Message-ID as fallback)
            thread_id = email_message.get('In-Reply-To') or email_message.get('Message-ID', email_id)
            
            return EmailData(
                id=email_id,
                thread_id=thread_id,
                from_=from_header,  # Use the field name 'from_' which has alias 'from'
                to=to_header,
                subject=subject,
                body=body,
                received_at=datetime.now()  # TODO: Parse actual received date
            )
            
        except Exception as e:
            self.logger.warning(f"Failed to parse email message: {e}")
            return None
    
    def _get_email_body(self, email_message: email.message.Message) -> str:
        """Extract email body from message."""
        body = ""
        
        if email_message.is_multipart():
            for part in email_message.walk():
                if part.get_content_type() == "text/plain":
                    body = part.get_payload(decode=True).decode()
                    break
        else:
            body = email_message.get_payload(decode=True).decode()
        
        return body
    
    def _add_attachment(self, msg: MIMEMultipart, file_path: str):
        """Add attachment to email message."""
        try:
            with open(file_path, "rb") as attachment:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(attachment.read())
            
            encoders.encode_base64(part)
            part.add_header(
                'Content-Disposition',
                f'attachment; filename= {file_path.split("/")[-1]}'
            )
            msg.attach(part)
            
        except Exception as e:
            self.logger.error(f"Failed to add attachment {file_path}: {e}")
            raise EmailError(f"Failed to add attachment: {e}")
    
    def close_connections(self):
        """Close all email connections."""
        if self._smtp_connection:
            self._smtp_connection.quit()
            self._smtp_connection = None
        
        if self._imap_connection:
            self._imap_connection.close()
            self._imap_connection = None 