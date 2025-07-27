"""
Email post-processing node for PocketFlow.

This module contains the PostprocessEmailNode for final email processing.
"""

from typing import Dict, Any, Optional
from ...core.node import Node
from ...core.types import SharedState, EmailSendRequest
from ...utils.logging import get_logger
from ...services.email_service import EmailService
from ...config.settings import get_settings

logger = get_logger("PostProcessNode")

class PostProcessNode(Node):
    """Node for final email processing and sending responses."""
    
    def prep(self, shared: SharedState):
        """Prepare by getting email service and extracting response data."""
        settings = get_settings()
        email_service = EmailService(settings)
        
        # Extract response data from shared state
        result = {}
        if hasattr(shared, 'email') and shared.email:
            result.update(shared.email)
        
        # Get reply body from shared state
        if hasattr(shared, 'reply_body') and shared.reply_body:
            result['reply_body'] = shared.reply_body
        
        # Get attachment from shared state
        if hasattr(shared, 'attachment') and shared.attachment:
            result['attachment'] = shared.attachment
        
        return email_service, result
    
    def exec(self, prep_result):
        """Execute by sending the final response email."""
        if not prep_result:
            return None
            
        email_service, result = prep_result
        
        # Determine recipient
        recipient = result.get("from")
        if not recipient:
            logger.error("No recipient email address found")
            return None
        
        # Set up proper reply headers
        in_reply_to = result.get("in_reply_to") or result.get("message_id")
        references = result.get("references") or result.get("message_id")
        
        # Debug logging for threading headers
        logger.info(f"Setting threading headers - in_reply_to: {in_reply_to}, references: {references}")
        logger.info(f"Original email message_id: {result.get('message_id')}")
        logger.info(f"Original email in_reply_to: {result.get('in_reply_to')}")
        logger.info(f"Original email references: {result.get('references')}")
        
        try:
            # Use the email service instead of direct function call
            send_request = EmailSendRequest(
                to=recipient,
                subject=f"Re: {result['subject']}",
                body=result.get("reply_body", ""),
                attachment=result.get("attachment"),
                in_reply_to=in_reply_to,
                references=references
            )
            
            # Send the email
            success = email_service.send_email(send_request)
            return success
            
        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            return False
    
    def post(self, shared: SharedState, prep_res, exec_res):
        """Post-process by logging the result and marking email as read."""
        if exec_res:
            logger.info("Final response email sent successfully")
            
            # Mark the email as read after successful processing
            if hasattr(shared, 'email') and shared.email and shared.email.get('id'):
                try:
                    settings = get_settings()
                    email_service = EmailService(settings)
                    email_service.mark_as_read(shared.email['id'])
                    logger.info(f"Marked email {shared.email['id']} as read after successful processing")
                except Exception as e:
                    logger.warning(f"Failed to mark email as read: {e}")
            
            return "default"
        else:
            logger.error("Failed to send final response email")
            return "error" 