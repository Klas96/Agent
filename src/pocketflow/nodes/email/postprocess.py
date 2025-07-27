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
        """Prepare by getting email service and checking if reply was sent."""
        settings = get_settings()
        email_service = EmailService(settings)
        
        # Extract response data from shared state
        result = {}
        if hasattr(shared, 'email') and shared.email:
            result.update(shared.email)
        
        # Check if user has already received a reply
        reply_sent = getattr(shared, 'sender_have_gotten_response', False)
        logger.info(f"Checking if reply was sent: {reply_sent}")
        
        # Get reply body from shared state (if available)
        if hasattr(shared, 'reply_body') and shared.reply_body:
            result['reply_body'] = shared.reply_body
        
        # Get attachment from shared state
        if hasattr(shared, 'attachment') and shared.attachment:
            result['attachment'] = shared.attachment
        
        return email_service, result, reply_sent
    
    def exec(self, prep_result):
        """Execute by sending the final response email."""
        if not prep_result:
            return None
            
        email_service, result, reply_sent = prep_result
        
        # Extract sender email from "from" field (e.g., "Klas Holmgren <klas0holmgren@gmail.com>")
        from_field = result.get("from", "")
        sender_email = None
        if "<" in from_field and ">" in from_field:
            sender_email = from_field.split("<")[1].split(">")[0]
        else:
            sender_email = from_field
            
        if not sender_email:
            logger.error("Could not extract sender email from: %s", from_field)
            return None
        
        # If reply was already sent, no need to send another
        if reply_sent:
            logger.info("Reply already sent to user, skipping post-process email")
            return True
        
        # Set up proper reply headers for threading
        original_message_id = result.get("message_id")
        original_in_reply_to = result.get("in_reply_to")
        original_references = result.get("references")
        
        # Use the original message ID for threading
        in_reply_to = original_message_id
        references = original_references or original_message_id
        
        # If we have original references, append the message ID
        if original_references and original_message_id:
            references = f"{original_references} {original_message_id}"
        elif original_message_id:
            references = original_message_id
        
        # Debug logging for threading headers
        logger.info(f"Setting threading headers - in_reply_to: {in_reply_to}, references: {references}")
        logger.info(f"Original email message_id: {original_message_id}")
        logger.info(f"Original email in_reply_to: {original_in_reply_to}")
        logger.info(f"Original email references: {original_references}")
        
        # Determine what happened and create appropriate response
        original_body = result.get("body", "")
        original_subject = result.get("subject", "")
        
        # Create default response based on what happened
        if result.get("last_error"):
            # There was an error in processing
            response_body = f"""Hi there!

I received your email but encountered an issue while processing it: {result.get('last_error')}

I'm working on fixing this issue. In the meantime, you can try:
- Sending your request again
- Rephrasing your question
- Contacting support if the problem persists

Thanks for your patience!

Best regards,
PocketFlow Assistant"""
        elif result.get("reply_body"):
            # Use existing reply body if available
            response_body = result.get("reply_body")
        else:
            # No specific response available, send generic acknowledgment
            response_body = f"""Hi there!

I received your email about: {original_subject or 'your request'}

I'm currently processing your request. You should receive a detailed response shortly.

If you don't hear back within a few minutes, please try sending your message again.

Thanks for using PocketFlow!

Best regards,
PocketFlow Assistant"""
        
        # Modify subject for proper reply threading
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
            # For empty subjects, use empty subject for proper threading
            reply_subject = ""
        
        try:
            # Use the email service instead of direct function call
            send_request = EmailSendRequest(
                to=sender_email,
                subject=reply_subject,
                body=response_body,
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
            
            # Mark that user has received a reply
            shared.sender_have_gotten_response = True
            logger.info("Marked that user has received a reply")
            
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