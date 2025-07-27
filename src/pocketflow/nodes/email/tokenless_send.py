"""
Tokenless email sending node for PocketFlow.

This module contains the TokenlessSendEmailNode for sending email responses to tokenless users.
"""

from typing import Dict, Any, Optional
from ...core.node import Node
from ...core.types import SharedState, EmailSendRequest
from ...utils.logging import get_logger
from ...utils.prompt_utils import replace_variables_in_text
from ...utils.user_utils import is_registered_user
from ...services.email_service import EmailService
from ...config.settings import get_settings

logger = get_logger("TokenlessSendEmailNode")

class TokenlessSendEmailNode(Node):
    """Node for sending emails to tokenless users based on agent actions."""
    
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

        # Replace variables in body and to field FIRST
        logger.info(f"About to replace variables in to field: '{to}'")
        body_with_vars_replaced = replace_variables_in_text(body, shared, sender_email)
        to_with_vars_replaced = replace_variables_in_text(to, shared, sender_email)
        
        logger.info(f"Replaced variables in email body and to field for {sender_email}")
        logger.info(f"Original to: '{to}', Replaced to: '{to_with_vars_replaced}'")
        
        # Check if user is trying to email themselves (this is allowed for replies)
        if to_with_vars_replaced == sender_email:
            logger.info(f"User {sender_email} is replying to themselves - this is allowed")
        else:
            # For tokenless users, validate that recipient is a registered user
            if not is_registered_user(to_with_vars_replaced):
                logger.error(f"Tokenless user {sender_email} trying to send to {to_with_vars_replaced} - blocked (not a registered user)")
                logger.info(f"Note: Only sending to registered users is allowed for tokenless users")
                # Return error action instead of None to inform the agent
                return "error"
            else:
                logger.info(f"Tokenless user {sender_email} sending to registered user {to_with_vars_replaced} - allowed")
        
        # Get payment info and Bitcoin address
        payment_info = getattr(shared, 'reply_body', None)
        btc_address = getattr(shared, 'btc_address', None)
        
        return email_service, to_with_vars_replaced, subject, body_with_vars_replaced, params, email, payment_info, btc_address
    
    def exec(self, prep_result):
        """Execute by sending the email."""
        if not prep_result:
            return None
            
        # Handle case where prep_result is "error" (string) from prep method
        if prep_result == "error":
            return None
            
        email_service, to, subject, body, params, email, payment_info, btc_address = prep_result
        
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
        
        # Modify subject for proper reply threading
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
            # For empty subjects (like your original emails), use empty subject for proper threading
            # This matches the format that Gmail expects for threading
            reply_subject = ""
        
        # Combine body with payment info if available
        if payment_info:
            combined_body = f"{body}\n\n---\n\n**Payment Information:**\n{payment_info}"
        else:
            # For tokenless users, always include a payment note with Bitcoin address
            if btc_address:
                payment_note = f"""---

**Payment Information:**
You're currently using the free trial. To access the full service with unlimited features, you can purchase tokens by sending Bitcoin to:

**Bitcoin Address:** `{btc_address}`

Payment details will be included in future responses if you're interested in upgrading.

*This is a tokenless user response*"""
            else:
                payment_note = """---

**Payment Information:**
You're currently using the free trial. To access the full service with unlimited features, you can purchase tokens. Payment details will be included in future responses if you're interested in upgrading.

*This is a tokenless user response*"""
            combined_body = f"{body}\n\n{payment_note}"
        
        # Create email send request
        send_request = EmailSendRequest(
            to=to,
            subject=reply_subject,
            body=combined_body,
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
        # Handle case where prep_res is "error" (string) from prep method
        if prep_res == "error":
            logger.error("Email sending blocked due to invalid recipient")
            return "error"
        
        if exec_res:
            logger.info("Email sent successfully")
            
            # Only mark as replied if the email was sent to the original sender
            if prep_res:
                email_service, to, subject, body, params, email, payment_info, btc_address = prep_res
                
                # Extract original sender email
                from_field = email.get("from", "")
                original_sender = None
                if "<" in from_field and ">" in from_field:
                    original_sender = from_field.split("<")[1].split(">")[0]
                else:
                    original_sender = from_field
                
                # Only mark as replied if email was sent to the original sender
                if original_sender and to == original_sender:
                    shared.sender_have_gotten_response = True
                    logger.info(f"Marked that original sender {original_sender} has received a reply")
                else:
                    logger.info(f"Email sent to {to} but original sender was {original_sender} - not marking as replied")
            
            return "default"
        else:
            logger.error("Failed to send email")
            return "error" 