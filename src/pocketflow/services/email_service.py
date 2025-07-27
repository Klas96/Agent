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
import os
import json

from ..core.types import EmailData, EmailSendRequest
from ..config.settings import Settings
from ..utils.errors import EmailError
from ..utils.logging import get_logger


class EmailService:
    """Service for handling email operations."""
    
    def __init__(self, settings: Settings):
        """Initialize the email service."""
        self.settings = settings
        self.logger = logging.getLogger(__name__)
        self._smtp_connection = None
        self._imap_connection = None
        self.logger.info("EmailService initialized")

    def _get_smtp_server(self):
        """Get or create SMTP server connection."""
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

    def _get_imap_server(self):
        """Get or create IMAP server connection."""
        if self._imap_connection is None:
            self._imap_connection = imaplib.IMAP4_SSL(self.settings.EMAIL_HOST)
            self._imap_connection.login(
                self.settings.EMAIL_USERNAME, 
                self.settings.EMAIL_PASSWORD
            )
            self._imap_connection.select('INBOX')
        return self._imap_connection
    
    def fetch_unread_emails(self) -> List[EmailData]:
        """Fetch unread emails from the inbox."""
        imap_server = None
        try:
            # Create a fresh IMAP connection for this operation
            imap_server = imaplib.IMAP4_SSL(self.settings.EMAIL_HOST)
            imap_server.login(
                self.settings.EMAIL_USERNAME, 
                self.settings.EMAIL_PASSWORD
            )
            imap_server.select('INBOX')
            
            emails = []
            
            self.logger.info("Fetching unread emails...")
            
            # Search for unread emails only
            _, message_numbers = imap_server.search(None, 'UNSEEN')
            if message_numbers[0]:
                self.logger.info(f"Found {len(message_numbers[0].split())} unread emails")
                for num in message_numbers[0].split():
                    email_id = num.decode()
                    
                    try:
                        _, msg_data = imap_server.fetch(num, '(RFC822)')
                        email_body = msg_data[0][1]
                        email_message = email.message_from_bytes(email_body)
                        
                        # Extract email data
                        email_data = self._parse_email_message(email_message, email_id)
                        if email_data:
                            emails.append(email_data)
                            # Mark as read immediately to prevent reprocessing
                            self.mark_as_read(email_id)
                            self.logger.info(f"Added unread email {email_id} to processing queue and marked as read")
                            
                    except Exception as e:
                        self.logger.warning(f"Failed to parse email {num}: {e}")
                        continue
            else:
                self.logger.info("No unread emails found")
                
                # Check for very recent emails (last 2 minutes) that might have been marked as read
                from datetime import datetime, timedelta
                two_minutes_ago = (datetime.now() - timedelta(minutes=2)).strftime("%d-%b-%Y")
                
                try:
                    # Search for emails from the last 2 minutes
                    _, recent_message_numbers = imap_server.search(None, f'SINCE {two_minutes_ago}')
                    if recent_message_numbers[0]:
                        recent_emails = recent_message_numbers[0].split()
                        # Only process the 1 most recent email to avoid spam
                        for num in recent_emails[-1:]:
                            email_id = num.decode()
                            
                            try:
                                _, msg_data = imap_server.fetch(num, '(RFC822)')
                                email_body = msg_data[0][1]
                                email_message = email.message_from_bytes(email_body)
                                
                                # Extract email data
                                email_data = self._parse_email_message(email_message, email_id)
                                if email_data and email_data.from_email == "klas0holmgren@gmail.com":
                                    emails.append(email_data)
                                    # Mark as read immediately to prevent reprocessing
                                    self.mark_as_read(email_id)
                                    self.logger.info(f"Added recent email {email_id} to processing queue and marked as read")
                            except Exception as e:
                                self.logger.error(f"Error processing recent email {email_id}: {e}")
                                continue
                except Exception as e:
                    self.logger.error(f"Error checking recent emails: {e}")
            
            self.logger.info(f"Fetched {len(emails)} emails total")
            return emails
            
        except Exception as e:
            self.logger.error(f"Failed to fetch emails: {e}")
            return []
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
        smtp_server = None
        try:
            self.logger.info(f"Sending email to: {request.to}")
            
            # Create message
            msg = MIMEMultipart()
            msg['From'] = self.settings.EMAIL_USERNAME
            msg['To'] = request.to
            if request.cc:
                msg['Cc'] = request.cc
            msg['Subject'] = request.subject
            
            # Add threading headers for proper email threading
            if request.in_reply_to:
                msg['In-Reply-To'] = request.in_reply_to
                self.logger.info(f"Setting In-Reply-To header: {request.in_reply_to}")
            if request.references:
                msg['References'] = request.references
                self.logger.info(f"Setting References header: {request.references}")
            
            # Add Message-ID for proper threading
            import uuid
            message_id = f"<pocketflow-{uuid.uuid4()}@mail.gmail.com>"
            msg['Message-ID'] = message_id
            self.logger.info(f"Setting Message-ID header: {message_id}")
            
            # Add additional headers that some email clients require for threading
            msg['X-Mailer'] = 'PocketFlow Email Agent'
            msg['X-Thread-Id'] = request.in_reply_to if request.in_reply_to else message_id
            
            # Add body
            msg.attach(MIMEText(request.body, 'plain', 'utf8'))
            
            # Add attachment if specified
            if request.attachment:
                self._add_attachment(msg, request.attachment)
            
            # Create a fresh SMTP connection for this operation
            smtp_server = smtplib.SMTP(
                self.settings.EMAIL_HOST, 
                self.settings.EMAIL_PORT
            )
            if self.settings.EMAIL_USE_TLS:
                smtp_server.starttls()
            smtp_server.login(
                self.settings.EMAIL_USERNAME, 
                self.settings.EMAIL_PASSWORD
            )
            
            # Send email
            recipients = [request.to]
            if request.cc:
                recipients.extend(request.cc.split(','))
            
            smtp_server.send_message(msg)
            
            self.logger.info(f"Email sent successfully to {request.to}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to send email: {e}")
            raise EmailError(f"Email sending failed: {e}")
        finally:
            if smtp_server:
                try:
                    smtp_server.quit()
                except Exception as e:
                    self.logger.warning(f"Error closing SMTP connection: {e}")
    
    def mark_as_read(self, email_id: str) -> bool:
        """Mark an email as read by setting the \Seen flag."""
        imap_server = None
        try:
            # Create a fresh IMAP connection for this operation
            imap_server = imaplib.IMAP4_SSL(self.settings.EMAIL_HOST)
            imap_server.login(
                self.settings.EMAIL_USERNAME, 
                self.settings.EMAIL_PASSWORD
            )
            imap_server.select('INBOX')
            
            # Set the \Seen flag
            imap_server.store(email_id, '+FLAGS', '\\Seen')
            self.logger.info(f"Marked email {email_id} as read")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to mark email {email_id} as read: {e}")
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
            message_id = email_message.get('Message-ID', '')
            in_reply_to = email_message.get('In-Reply-To', '')
            references = email_message.get('References', '')
            
            # Extract body
            body = self._get_email_body(email_message)
            
            # Extract thread ID (using Message-ID as fallback)
            thread_id = in_reply_to or message_id or email_id
            
            return EmailData(
                id=email_id,
                thread_id=thread_id,
                from_=from_header,  # Use the field name 'from_' which has alias 'from'
                to=to_header,
                subject=subject,
                body=body,
                received_at=datetime.now(),  # TODO: Parse actual received date
                message_id=message_id if message_id else None,
                in_reply_to=in_reply_to if in_reply_to else None,
                references=references if references else None
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