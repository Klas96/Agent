"""
Tokenless response node for PocketFlow.

This module contains the TokenlessResponseNode for sending responses to tokenless users.
"""

from typing import Dict, Any, Optional
from ...core.node import Node
from ...core.types import SharedState, EmailSendRequest
from ...utils.logging import get_logger
from ...utils.email_utils import build_threading_headers
from ...services.email_service import EmailService
from ...config.settings import get_settings

logger = get_logger("TokenlessResponseNode")

class TokenlessResponseNode(Node):
    """Node for sending responses to tokenless users with payment information."""
    
    def prep(self, shared: SharedState):
        """Prepare by getting email service and extracting data."""
        settings = get_settings()
        email_service = EmailService(settings)
        
        # Extract email data
        if not hasattr(shared, 'email') or not shared.email:
            logger.error("No email data found in shared state")
            return None
            
        email_data = shared.email
        
        # Extract sender email from "from" field
        from_field = email_data.get("from", "")
        sender_email = None
        if "<" in from_field and ">" in from_field:
            sender_email = from_field.split("<")[1].split(">")[0]
        else:
            sender_email = from_field
            
        if not sender_email:
            logger.error("Could not extract sender email from: %s", from_field)
            return None
        
        # Get original email content
        original_body = email_data.get("body", "")
        original_subject = email_data.get("subject", "")
        
        # Build deterministic threading headers using helper function
        in_reply_to, references = build_threading_headers(
            original_message_id=email_data.get("message_id"),
            original_in_reply_to=email_data.get("in_reply_to"),
            original_references=email_data.get("references"),
            thread_id=email_data.get("thread_id"),
            email_id=email_data.get("id")
        )
        
        # Log threading headers for debugging
        logger.info(f"Threading headers - In-Reply-To: {in_reply_to}, References: {references}")
        logger.info(f"  Original message_id: {email_data.get('message_id')}")
        logger.info(f"  Original in_reply_to: {email_data.get('in_reply_to')}")
        logger.info(f"  Original references: {email_data.get('references')}")
        logger.info(f"  Original email_id: {email_data.get('id')}")
        
        # Warn if no threading identifier available
        if not in_reply_to:
            logger.error("No threading identifier available - email will not be threaded properly!")
        
        return email_service, sender_email, original_body, original_subject, in_reply_to, references
    
    def exec(self, prep_result):
        """Execute by sending the tokenless response email."""
        if not prep_result:
            return None
            
        email_service, sender_email, original_body, original_subject, in_reply_to, references = prep_result
        
        # Create a helpful response for tokenless users
        response_body = f"""Hi there!

Thank you for your message. I'd be happy to help you with your request!

To get started, you'll need to purchase some tokens. Please try sending your message again and I'll provide you with payment instructions.

Best regards,
PocketFlow Assistant"""
        
        # Create email send request
        send_request = EmailSendRequest(
            to=sender_email,
            subject=f"Re: {original_subject}" if original_subject else "Re: Your request",
            body=response_body,
            in_reply_to=in_reply_to,
            references=references
        )
        
        # Send the email
        try:
            success = email_service.send_email(send_request)
            if success:
                logger.info(f"Tokenless response sent successfully to {sender_email}")
                return True
            else:
                logger.error(f"Failed to send tokenless response to {sender_email}")
                return False
        except Exception as e:
            logger.error(f"Error sending tokenless response: {e}")
            return False
    
    def post(self, shared: SharedState, prep_res, exec_res):
        """Post-process by logging the result and marking as replied."""
        if exec_res:
            logger.info("Tokenless response sent successfully")
            # Mark that the original sender has received a reply
            shared.sender_have_gotten_response = True
            return "default"
        else:
            logger.error("Failed to send tokenless response")
            return "error" 