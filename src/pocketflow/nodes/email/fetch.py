"""
Email fetching node for PocketFlow.

This module contains the FetchEmailNode for retrieving unread emails.
"""

from typing import Dict, Any, Optional, List
from ...core.node import Node
from ...core.types import SharedState, EmailData
from ...utils.logging import get_logger
from ...utils.errors import EmailError
from ...services.email_service import EmailService
from ...config.settings import get_settings
from ...utils.email_utils import extract_email

logger = get_logger("FetchEmailNode")

class FetchEmailNode(Node):
    """Node for fetching unread emails."""
    
    def prep(self, shared: SharedState):
        """Prepare by getting email service."""
        settings = get_settings()
        email_service = EmailService(settings)
        return email_service
    
    def exec(self, email_service: EmailService):
        """Execute by fetching unread emails."""
        emails = email_service.fetch_unread_emails()
        return emails
    
    def post(self, shared: SharedState, prep_res: EmailService, exec_res: List[EmailData]):
        """Post-process by storing email data in shared state."""
        if exec_res:
            email_data = exec_res[0]  # Process first email
            shared.email = {
                'id': email_data.id,
                'subject': email_data.subject,
                'from': email_data.from_,
                'body': email_data.body,
                'date': email_data.received_at,
                'message_id': email_data.message_id,
                'thread_id': email_data.thread_id,
                'in_reply_to': email_data.in_reply_to,
                'references': email_data.references
            }
            logger.info(f"Fetched email: {email_data.subject}")
            
            return "default"
        else:
            logger.info("No unread emails found")
            # Clear any existing email from shared state to prevent reprocessing
            shared.email = None
            # Also clear conversation context to prevent processing old conversations
            shared.conversation = None
            shared.conversations = {}
            return "finish" 