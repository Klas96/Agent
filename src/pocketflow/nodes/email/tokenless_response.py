"""
Tokenless response node for PocketFlow.

This module contains the TokenlessResponseNode for sending responses to tokenless users.
"""

from typing import Dict, Any, Optional
from ...core.node import Node
from ...core.types import SharedState, EmailSendRequest
from ...utils.logging import get_logger
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
        
        # Get Bitcoin address for payment
        btc_address = getattr(shared, 'btc_address', None)
        
        # Get original email content
        original_body = email_data.get("body", "")
        original_subject = email_data.get("subject", "")
        
        # Set up proper reply headers for threading
        original_message_id = email_data.get("message_id")
        original_in_reply_to = email_data.get("in_reply_to")
        original_references = email_data.get("references")
        
        # Use the original message ID for threading
        in_reply_to = original_message_id
        references = original_references or original_message_id
        
        # If we have original references, append the message ID
        if original_references and original_message_id:
            references = f"{original_references} {original_message_id}"
        elif original_message_id:
            references = original_message_id
        
        return email_service, sender_email, original_body, original_subject, btc_address, in_reply_to, references
    
    def exec(self, prep_result):
        """Execute by sending the tokenless response email."""
        if not prep_result:
            return None
            
        email_service, sender_email, original_body, original_subject, btc_address, in_reply_to, references = prep_result
        
        # Create a helpful response for tokenless users
        if btc_address:
            response_body = f"""Hi there!

Thank you for your message. I'd be happy to help you with your request!

To get started, you'll need to purchase some tokens. You can do this by sending Bitcoin to the following address:

**Bitcoin Address:** `{btc_address}`

Once you've sent the payment, I'll be able to process your request and provide you with a detailed response.

If you have any questions about the payment process, feel free to ask!

Best regards,
PocketFlow Assistant"""
        else:
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