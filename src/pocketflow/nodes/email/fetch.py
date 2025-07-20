"""
Fetch email node for PocketFlow.

This node handles fetching unread emails and processing them.
"""

import re
from typing import Optional, List, Dict, Any

from ...core.node import SimpleNode
from ...core.types import SharedState, EmailData
from ...services import email_service
from ...utils.logging import get_logger
from ...utils.errors import EmailError


def extract_email(sender: str) -> str:
    """
    Extract email address from sender string.
    
    Args:
        sender: Sender string that may contain email
        
    Returns:
        Extracted email address
    """
    # Use raw string and single backslash for dot
    match = re.search(r'<([A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,})>', sender)
    if match:
        return match.group(1)
    # fallback: if sender is just the email
    match = re.search(r'([A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,})', sender)
    return match.group(1) if match else sender


class FetchEmailNode(SimpleNode):
    """Node for fetching and processing unread emails."""
    
    def __init__(self, name: str = "fetch_email"):
        super().__init__(name)
        self.logger = get_logger("FetchEmailNode")
    
    def process(self, shared: SharedState) -> Dict[str, Any]:
        """
        Fetch unread emails and process the first one.
        
        Args:
            shared: Shared state containing context
            
        Returns:
            Processing result with routing information
        """
        try:
            self.logger.info("Fetching unread emails...")
            
            # Fetch unread emails using email service
            emails = email_service.fetch_unread_emails()
            self.logger.info(f"Fetched {len(emails)} unread emails")
            
            if not emails:
                self.logger.info("No unread emails found")
                shared["email"] = None
                return {"route": "no_email"}
            
            # Process the first email
            email = emails[0]
            self.logger.info(f"Processing email: from={email.from_}, subject={email.subject}")
            
            # Greenlist check for sender
            sender_email = extract_email(email.from_).strip().lower() if email.from_ else None
            sender_domain = sender_email.split("@")[-1] if sender_email and "@" in sender_email else None
            
            # TODO: Implement greenlist checking
            # For now, accept all emails
            is_greenlisted = True
            
            if not is_greenlisted:
                self.logger.info(f"Sender {email.from_} not in greenlist. Skipping email.")
                shared["email"] = None
                return {"route": "no_email"}
            
            # Accept the email
            self.logger.info(f"Accepted email from {email.from_} (subject: {email.subject})")
            shared["email"] = {
                "id": email.id,
                "from": email.from_,
                "to": email.to,
                "subject": email.subject,
                "body": email.body,
                "thread_id": email.thread_id,
                "received_at": email.received_at
            }
            shared["user"] = extract_email(email.from_)
            
            # Mark email as read
            email_service.mark_as_read(email.id)
            
            return {"route": "default"}
            
        except EmailError as e:
            self.logger.error(f"Email fetching failed: {e}")
            shared["email"] = None
            return {"route": "no_email", "error": str(e)}
        except Exception as e:
            self.logger.error(f"Unexpected error in FetchEmailNode: {e}")
            shared["email"] = None
            return {"route": "no_email", "error": str(e)} 