"""
Email sending node for PocketFlow.

This module contains the SendEmailNode for sending email responses.
"""

from typing import Dict, Any, Optional
from ...core.node import Node
from ...core.types import SharedState, EmailSendRequest
from ...utils.logging import get_logger
from ...utils.prompt_utils import replace_variables_in_text
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
                from ...web.routes import get_user_by_email
                recipient_user = get_user_by_email(to)
                if not recipient_user:
                    logger.error(f"Recipient {to} is not a registered user. Blocked.")
                    return None
                logger.info(f"Recipient {to} is a registered user - proceeding")
            except Exception as e:
                logger.error(f"Error validating recipient {to}: {e}")
                return None
        
        # Replace variables in body and subject
        body_with_vars_replaced = replace_variables_in_text(body, shared, sender_email)
        subject_with_vars_replaced = replace_variables_in_text(subject, shared, sender_email)
        
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
        
        logger.info(f"Replaced variables in email body and subject for {sender_email}")
        
        return email_service, to, subject_with_vars_replaced, body_with_vars_replaced, params, email
    
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
            
            # Only mark as replied if the email was sent to the original sender
            if prep_res:
                email_service, to, subject, body, params, email = prep_res
                
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