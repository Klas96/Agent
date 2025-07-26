"""
Email sending node for PocketFlow.

This module contains the SendEmailNode for sending email responses.
"""

from typing import Dict, Any, Optional
from ...core.node import Node
from ...core.types import SharedState, EmailSendRequest
from ...utils.logging import get_logger
from ...services.email_service import EmailService
from ...config.settings import get_settings

logger = get_logger("SendEmailNode")

class SendEmailNode(Node):
    """Node for sending emails based on agent actions."""
    
    def prep(self, shared: SharedState):
        """Prepare by getting email service and extracting send parameters."""
        settings = get_settings()
        email_service = EmailService(settings)
        
        # Extract send parameters from agent action
        agent_action = shared.agent_action
        if not agent_action or agent_action.get('action') != 'send':
            logger.warning("No send action found in agent_action")
            return None
            
        params = agent_action.get('parameters', {})
        to = params.get('to')
        subject = params.get('subject')  # Don't set default here
        body = params.get('body', '')
        
        if not to:
            logger.error("No recipient email address found")
            return None
        
        # Get email data from shared state
        email = shared.email if hasattr(shared, 'email') else {}
        
        # Create proper subject for replies if not provided by agent
        if not subject:
            original_subject = email.get('subject', '')
            if original_subject:
                subject = f"Re: {original_subject}"
            else:
                subject = "Re: Your email"  # Fallback for empty subjects
        
        # Debug logging for subject
        logger.info(f"Final subject being used: {subject}")
        logger.info(f"Original email subject: {email.get('subject', '')}")
        logger.info(f"Agent provided subject: {params.get('subject')}")
            
        return email_service, to, subject, body, params, email
    
    def exec(self, prep_result):
        """Execute by sending the email."""
        if not prep_result:
            return None
            
        email_service, to, subject, body, params, email = prep_result
        
        # Set up proper reply headers for email threading
        in_reply_to = email.get("in_reply_to") or email.get("message_id")
        references = email.get("references") or email.get("message_id")
        
        # Create email send request
        send_request = EmailSendRequest(
            to=to,
            subject=subject,
            body=body,
            cc=params.get("cc"),
            attachment=params.get("attachment"),
            in_reply_to=in_reply_to,
            references=references
        )
        
        # Send the email
        success = email_service.send_email(send_request)
        return success
    
    def post(self, shared: SharedState, prep_res, exec_res):
        """Post-process by logging the result."""
        if exec_res:
            logger.info("Email sent successfully")
            return "default"
        else:
            logger.error("Failed to send email")
            return "error" 