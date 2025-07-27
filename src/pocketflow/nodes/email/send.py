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
        if not agent_action or agent_action.get("action") != "send":
            logger.error("No send action found in agent_action")
            return None
            
        params = agent_action.get("parameters", {})
        to = params.get("to")
        subject = params.get("subject", "")
        body = params.get("body", "")
        
        if not to:
            logger.error("No recipient email address found")
            return None
            
        # Extract sender email from the original email
        email = shared.email
        if not email:
            logger.error("No email data found in shared state")
            return None
            
        # Extract sender email from "from" field (e.g., "Klas Holmgren <klas0holmgren@gmail.com>")
        from_field = email.get("from", "")
        sender_email = None
        if "<" in from_field and ">" in from_field:
            sender_email = from_field.split("<")[1].split(">")[0]
        else:
            sender_email = from_field
            
        # Validate recipient
        if not sender_email:
            logger.error("Could not extract sender email from: %s", from_field)
            return None
            
        # Check if user is trying to email themselves (this is allowed for replies)
        if to == sender_email:
            logger.info(f"User {sender_email} is replying to themselves - this is allowed")
        else:
            # For emails to other users, validate they exist in the database
            try:
                from ..web.routes import get_user_by_email
                recipient_user = get_user_by_email(to)
                if not recipient_user:
                    logger.error(f"Recipient {to} is not a registered user. Blocked.")
                    return None
                logger.info(f"Recipient {to} is a registered user - proceeding")
            except Exception as e:
                logger.error(f"Error validating recipient {to}: {e}")
                return None
        
        return email_service, to, subject, body, params, email
    
    def exec(self, prep_result):
        """Execute by sending the email."""
        if not prep_result:
            return None
            
        email_service, to, subject, body, params, email = prep_result
        
        # Set up proper reply headers for email threading
        original_message_id = email.get("message_id")
        original_references = email.get("references")
        
        # For In-Reply-To, use the original message ID
        in_reply_to = email.get("in_reply_to") or original_message_id
        
        # For References, build the proper chain
        if original_references and original_message_id:
            # Append the original message_id to existing references
            # Ensure proper spacing and format
            references = f"{original_references} {original_message_id}"
        else:
            # For first reply, References should be the same as In-Reply-To
            # This is the standard format that most email clients expect
            references = in_reply_to
        
        # Debug logging for threading headers
        logger.info(f"Original email message_id: {email.get('message_id')}")
        logger.info(f"Original email in_reply_to: {email.get('in_reply_to')}")
        logger.info(f"Original email references: {email.get('references')}")
        logger.info(f"Setting In-Reply-To: {in_reply_to}")
        logger.info(f"Setting References: {references}")
        
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