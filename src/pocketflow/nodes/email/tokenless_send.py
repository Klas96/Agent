"""
Tokenless user email sending node for PocketFlow.

This module contains the TokenlessSendEmailNode for sending payment request emails
to users without tokens.
"""

from typing import Dict, Any, Optional
from ...core.node import Node
from ...core.types import SharedState, EmailSendRequest
from ...utils.logging import get_logger
from ...services.email_service import EmailService, EmailError
from ...config.settings import get_settings

logger = get_logger("TokenlessSendEmailNode")

class TokenlessSendEmailNode(Node):
    """Node for sending payment request emails to tokenless users."""
    
    def prep(self, shared: SharedState):
        """Prepare by getting email service and extracting send parameters."""
        settings = get_settings()
        email_service = EmailService(settings)
        
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
        
        # Get agent response from shared state (the main email content)
        agent_action = shared.agent_action
        if not agent_action or 'parameters' not in agent_action:
            logger.error("No agent action found in shared state")
            return None
        
        agent_body = agent_action.get('parameters', {}).get('body', '')
        if not agent_body:
            logger.error("No agent response body found in shared state")
            return None
        
        # Get payment info from shared state (set by PurchaseTokensWithBitcoinNode)
        payment_info = shared.reply_body
        if not payment_info:
            logger.error("No payment info found in shared state")
            return None
        
        return email_service, sender_email, agent_body, payment_info, email
    
    def exec(self, prep_result):
        """Execute by sending the payment request email."""
        if not prep_result:
            return None
            
        email_service, sender_email, agent_body, payment_info, email = prep_result
        
        # Enhanced threading - use original message ID and include subject context
        original_message_id = email.get("message_id")
        original_references = email.get("references")
        original_subject = email.get("subject", "")
        
        # For In-Reply-To, use the original message ID (this is the key for threading)
        in_reply_to = original_message_id
        
        # For References, build the proper chain
        # Gmail and most email clients expect References to be a space-separated list
        if original_references and original_references.strip():
            # If there are existing references, append the original message ID
            references = f"{original_references} {original_message_id}"
        else:
            # For first reply, References should be the same as In-Reply-To
            # This is the standard RFC format that Gmail expects
            references = original_message_id
        
        # Log threading details for debugging
        logger.info(f"Original email message_id: {original_message_id}")
        logger.info(f"Original email in_reply_to: {email.get('in_reply_to')}")
        logger.info(f"Original email references: {original_references}")
        logger.info(f"Setting In-Reply-To: {in_reply_to}")
        logger.info(f"Setting References: {references}")
        
        # Combine agent response with payment info as a note
        combined_body = f"{agent_body}\n\n---\n\n**Payment Information:**\n{payment_info}"
        
        # Subject line for proper threading - use the original subject if available
        original_subject = email.get("subject", "")
        if original_subject and original_subject.strip():
            # For non-empty subjects, use "Re:" prefix
            clean_subject = original_subject.strip()
            if clean_subject.startswith("Re:"):
                clean_subject = clean_subject[3:].strip()
            elif clean_subject.startswith("RE:"):
                clean_subject = clean_subject[3:].strip()
            elif clean_subject.startswith("re:"):
                clean_subject = clean_subject[3:].strip()
            
            # Add "Re:" prefix for proper threading
            reply_subject = f"Re: {clean_subject}"
        else:
            # For empty subjects, use a default subject that matches the original email content
            # Extract a few words from the email body to create a meaningful subject
            body_words = email.get("body", "").split()[:5]  # First 5 words
            if body_words:
                subject_snippet = " ".join(body_words).strip()
                if len(subject_snippet) > 50:
                    subject_snippet = subject_snippet[:50] + "..."
                reply_subject = f"Re: {subject_snippet}"
            else:
                reply_subject = "Re: Your email request"
            
        send_request = EmailSendRequest(
            to=sender_email,
            subject=reply_subject,
            body=combined_body,
            in_reply_to=in_reply_to,
            references=references
        )
        
        # Send the email with proper error handling
        try:
            success = email_service.send_email(send_request)
            return success
        except EmailError as e:
            logger.error(f"Email sending failed: {e}")
            # Re-raise the exception so it can be handled by the Node's error handling
            raise
    
    def exec_fallback(self, prep_result, exc):
        """Handle email sending failures gracefully."""
        if isinstance(exc, EmailError):
            logger.error(f"Email authentication failed: {exc}")
            # Return False to indicate failure, which will be handled in post()
            return False
        else:
            # For other exceptions, re-raise
            raise exc
    
    def post(self, shared: SharedState, prep_res, exec_res):
        """Post-process the email sending result."""
        if exec_res is True:  # Explicitly check for True, not just truthy
            logger.info("Payment request email sent successfully")
            return "default"
        else:
            logger.error("Failed to send payment request email - authentication or connection issue")
            # Store the error in shared state for debugging
            shared.last_error = "Email sending failed - check SMTP credentials and connection"
            return "send_failed" 