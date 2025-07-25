"""
Email fetching node for PocketFlow.

This module contains the FetchEmailNode for retrieving unread emails.
"""

from typing import Dict, Any, Optional
from ...core.node import SimpleNode
from ...core.types import SharedState
from ...utils.logging import get_logger
from ...utils.errors import EmailError
from ...services import email_service
from utils.email_utils import extract_email


class FetchEmailNode(SimpleNode):
    """Node for fetching unread emails."""
    
    def process(self, shared: SharedState) -> Optional[Dict[str, Any]]:
        """Fetch unread emails and store in shared state."""
        logger = get_logger("FetchEmailNode")
        
        try:
            logger.info("Fetching unread emails...")
            emails = email_service.fetch_unread_emails()
            
            if emails:
                # Store the first unread email in shared state
                email_data = emails[0]
                shared.email = {
                    'id': email_data.id,
                    'subject': email_data.subject,
                    'from': email_data.sender,
                    'body': email_data.body,
                    'date': email_data.date,
                    'message_id': email_data.message_id,
                    'thread_id': email_data.thread_id
                }
                logger.info(f"Fetched email: {email_data.subject}")
                return {"route": "default"}
            else:
                logger.info("No unread emails found")
                return None
                
        except Exception as e:
            logger.error(f"Error fetching emails: {e}")
            raise EmailError(f"Failed to fetch emails: {e}") 