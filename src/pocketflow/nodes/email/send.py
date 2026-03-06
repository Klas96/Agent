"""
Email sending node for PocketFlow.

This module contains the SendEmailNode for sending email responses.
"""

from typing import Dict, Any, Optional
from ...core.node import Node
from ...core.types import SharedState, EmailSendRequest
from ...utils.logging import get_logger
from ...utils.prompt_utils import replace_variables_in_text
from ...utils.email_utils import build_threading_headers
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
            
        # Replace variables in recipient, body and subject BEFORE validation
        to_with_vars_replaced = replace_variables_in_text(to, shared, sender_email)
        body_with_vars_replaced = replace_variables_in_text(body, shared, sender_email)
        subject_with_vars_replaced = replace_variables_in_text(subject, shared, sender_email)
        
        # Replace variables in attachment path if present
        attachment = params.get("attachment")
        attachment_with_vars_replaced = None
        if attachment:
            attachment_with_vars_replaced = replace_variables_in_text(attachment, shared, sender_email)
            logger.info(f"Replaced variables in attachment path: '{attachment}' -> '{attachment_with_vars_replaced}'")
        
        # Validate recipient AFTER variable replacement
        if to_with_vars_replaced == sender_email:
            logger.info(f"User {sender_email} is replying to themselves - this is allowed")
        else:
            # For emails to other users, validate they exist in the database
            try:
                from ...services.database_service import DatabaseService
                db_service = DatabaseService()
                recipient_user = db_service.get_user(to_with_vars_replaced)
                if not recipient_user:
                    logger.error(f"Recipient {to_with_vars_replaced} is not a registered user. Blocked.")
                    return None
                logger.info(f"Recipient {to_with_vars_replaced} is a registered user - proceeding")
            except Exception as e:
                logger.error(f"Error validating recipient {to_with_vars_replaced}: {e}")
                return None
        
        # Check if there are tool results to include
        tool_result = getattr(shared, 'tool_result', None)
        if tool_result:
            # Format tool results for inclusion in email
            tool_name = tool_result.get('tool_name', 'Unknown Tool')
            if 'error' in tool_result:
                tool_info = f"\n\n**Tool Error:** {tool_result['error']}"
            else:
                result = tool_result.get('result', {})
                if isinstance(result, dict):
                    # Format structured tool results
                    tool_info = f"\n\n**Tool Results ({tool_name}):**\n"
                    for key, value in result.items():
                        if key != 'api':  # Skip internal API metadata
                            tool_info += f"- {key}: {value}\n"
                else:
                    tool_info = f"\n\n**Tool Results ({tool_name}):**\n{result}\n"
            
            # Append tool results to the body
            body_with_vars_replaced += tool_info
            logger.info(f"Added tool results from {tool_name} to email body")
        
        # Validate that body is not empty after variable replacement
        if not body_with_vars_replaced or not body_with_vars_replaced.strip():
            logger.warning("Email body is empty after variable replacement. Using fallback message.")
            # Use fallback message if body is empty
            original_subject = email.get("subject", "")
            body_with_vars_replaced = f"""Hi there!

I received your email about: {original_subject or 'your request'}

I'm processing your request, but I wasn't able to generate a specific response. Please try rephrasing your question or request.

Thanks for using PocketFlow!

Best regards,
PocketFlow Assistant"""
        
        logger.info(f"Replaced variables in email body and subject for {sender_email}")
        
        return email_service, to_with_vars_replaced, subject_with_vars_replaced, body_with_vars_replaced, attachment_with_vars_replaced, email, shared
    
    def exec(self, prep_result):
        """Execute by sending the email."""
        if not prep_result:
            return None
            
        email_service, to, subject, body, attachment, email, shared = prep_result
        
        # Build deterministic threading headers using helper function
        in_reply_to, references = build_threading_headers(
            original_message_id=email.get("message_id"),
            original_in_reply_to=email.get("in_reply_to"),
            original_references=email.get("references"),
            thread_id=email.get("thread_id"),
            email_id=email.get("id")
        )
        
        # Log threading headers for debugging
        logger.info(f"Threading headers - In-Reply-To: {in_reply_to}, References: {references}")
        logger.info(f"  Original message_id: {email.get('message_id')}")
        logger.info(f"  Original in_reply_to: {email.get('in_reply_to')}")
        logger.info(f"  Original references: {email.get('references')}")
        
        # Warn if no threading identifier available
        if not in_reply_to:
            logger.error("No threading identifier available - email will not be threaded properly!")
        
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
        
        # Create email send request
        send_request = EmailSendRequest(
            to=to,
            subject=reply_subject,
            body=body,
            cc=None,  # No CC support in current implementation
            attachment=attachment,
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
            
            # Only mark as replied if the email was sent to the original sender
            if prep_res:
                email_service, to, subject, body, attachment, email, shared = prep_res
                
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