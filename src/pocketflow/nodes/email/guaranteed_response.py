"""
Guaranteed response node for PocketFlow.

This node ensures that every email receives a response, even if all other steps fail.
"""

from typing import Dict, Any, Optional
from ...core.node import Node
from ...core.types import SharedState, EmailSendRequest
from ...utils.logging import get_logger
from ...utils.email_utils import build_threading_headers
from ...services.email_service import EmailService
from ...config.settings import get_settings

logger = get_logger("GuaranteedResponseNode")


class GuaranteedResponseNode(Node):
    """
    Node that guarantees a response is sent, even if everything else fails.
    
    This node should be used as a final fallback to ensure users always receive
    a response to their emails, regardless of any errors in the processing flow.
    """
    
    def prep(self, shared: SharedState) -> Dict[str, Any]:
        """
        Prepare by extracting email information and checking if response was already sent.
        
        Returns:
            Dictionary containing email service, email data, and response status
        """
        try:
            settings = get_settings()
            email_service = EmailService(settings)
            
            # Extract email data
            email = getattr(shared, 'email', None) or {}
            
            # Check if response was already sent
            response_sent = getattr(shared, 'sender_have_gotten_response', False)
            
            # Extract sender email
            from_field = email.get("from", "")
            sender_email = None
            if "<" in from_field and ">" in from_field:
                sender_email = from_field.split("<")[1].split(">")[0]
            else:
                sender_email = from_field.strip()
            
            # Get any existing response or error information
            existing_response = getattr(shared, 'agent_response', None) or getattr(shared, 'reply_body', None)
            last_error = getattr(shared, 'last_error', None)
            
            return {
                "email_service": email_service,
                "email": email,
                "sender_email": sender_email,
                "response_sent": response_sent,
                "existing_response": existing_response,
                "last_error": last_error
            }
        except Exception as e:
            logger.error(f"Error in prep: {e}", exc_info=True)
            # Return minimal data to allow exec to still try
            return {
                "email_service": None,
                "email": getattr(shared, 'email', {}),
                "sender_email": None,
                "response_sent": False,
                "existing_response": None,
                "last_error": str(e)
            }
    
    def exec(self, prep_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute by attempting to send a response email.
        
        This method will always try to send a response, even if prep failed.
        """
        if not prep_result:
            logger.error("No prep result available, cannot send response")
            return {"success": False, "error": "No prep result"}
        
        email_service = prep_result.get("email_service")
        email = prep_result.get("email", {})
        sender_email = prep_result.get("sender_email")
        response_sent = prep_result.get("response_sent", False)
        existing_response = prep_result.get("existing_response")
        last_error = prep_result.get("last_error")
        
        # If response was already sent, we're done
        if response_sent:
            logger.info("Response already sent, skipping guaranteed response")
            return {"success": True, "skipped": True, "reason": "Response already sent"}
        
        # If no sender email, we can't send a response
        if not sender_email:
            logger.error("No sender email available, cannot send guaranteed response")
            return {"success": False, "error": "No sender email"}
        
        # If no email service, try to create one
        if not email_service:
            try:
                settings = get_settings()
                email_service = EmailService(settings)
            except Exception as e:
                logger.error(f"Failed to create email service: {e}")
                return {"success": False, "error": f"Email service unavailable: {e}"}
        
        # Build response body
        response_body = self._build_response_body(
            email=email,
            existing_response=existing_response,
            last_error=last_error
        )
        
        # Build threading headers
        try:
            in_reply_to, references = build_threading_headers(
                original_message_id=email.get("message_id"),
                original_in_reply_to=email.get("in_reply_to"),
                original_references=email.get("references"),
                thread_id=email.get("thread_id"),
                email_id=email.get("id")
            )
        except Exception as e:
            logger.warning(f"Failed to build threading headers: {e}")
            in_reply_to = None
            references = None
        
        # Build subject
        original_subject = email.get("subject", "")
        if original_subject and original_subject.strip():
            clean_subject = original_subject.strip()
            # Remove existing Re: prefixes
            for prefix in ["Re:", "RE:", "re:"]:
                if clean_subject.startswith(prefix):
                    clean_subject = clean_subject[len(prefix):].strip()
            reply_subject = f"Re: {clean_subject}"
        else:
            reply_subject = ""
        
        # Attempt to send email with retries
        max_attempts = 3
        for attempt in range(max_attempts):
            try:
                send_request = EmailSendRequest(
                    to=sender_email,
                    subject=reply_subject,
                    body=response_body,
                    in_reply_to=in_reply_to,
                    references=references
                )
                
                success = email_service.send_email(send_request)
                if success:
                    logger.info(f"Guaranteed response sent successfully (attempt {attempt + 1})")
                    return {"success": True, "attempt": attempt + 1}
                else:
                    logger.warning(f"Email send returned False (attempt {attempt + 1})")
                    if attempt < max_attempts - 1:
                        continue
                    return {"success": False, "error": "Email service returned False"}
                    
            except Exception as e:
                logger.error(f"Failed to send guaranteed response (attempt {attempt + 1}): {e}")
                if attempt < max_attempts - 1:
                    import time
                    time.sleep(1)  # Brief delay before retry
                    continue
                return {"success": False, "error": str(e)}
        
        return {"success": False, "error": "All send attempts failed"}
    
    def _build_response_body(self, email: Dict[str, Any], existing_response: Optional[str], last_error: Optional[str]) -> str:
        """Build an appropriate response body based on available information."""
        
        # If we have an existing response, use it
        if existing_response:
            return existing_response
        
        # If there was an error, explain it
        if last_error:
            return f"""Hi there!

I received your email, but I encountered an issue while processing it.

Error: {last_error}

I'm working on fixing this issue. In the meantime, you can try:
- Sending your request again
- Rephrasing your question
- Contacting support if the problem persists

Thanks for your patience!

Best regards,
PocketFlow Assistant"""
        
        # Generic acknowledgment
        subject = email.get("subject", "your request")
        return f"""Hi there!

I received your email about: {subject}

I'm currently processing your request. You should receive a detailed response shortly.

If you don't hear back within a few minutes, please try sending your message again.

Thanks for using PocketFlow!

Best regards,
PocketFlow Assistant"""
    
    def post(self, shared: SharedState, prep_res: Dict[str, Any], exec_res: Dict[str, Any]) -> str:
        """
        Post-process by marking response as sent and email as read.
        
        Returns:
            "default" to indicate completion
        """
        if exec_res.get("success") and not exec_res.get("skipped"):
            logger.info("Guaranteed response sent successfully")
            
            # Mark that user has received a reply
            shared.sender_have_gotten_response = True
            
            # Try to mark email as read
            email = getattr(shared, 'email', None)
            if email and email.get("id"):
                try:
                    settings = get_settings()
                    email_service = EmailService(settings)
                    email_service.mark_as_read(email['id'])
                    logger.info(f"Marked email {email['id']} as read")
                except Exception as e:
                    logger.warning(f"Failed to mark email as read: {e}")
        
        elif exec_res.get("skipped"):
            logger.info("Guaranteed response skipped (response already sent)")
        else:
            logger.error(f"Guaranteed response failed: {exec_res.get('error')}")
            # Even if sending failed, mark that we tried
            shared.sender_have_gotten_response = True
        
        return "default"
    
    def exec_fallback(self, prep_result: Any, exc: Exception) -> Optional[Dict[str, Any]]:
        """
        Fallback method that tries to send a minimal response even if exec fails.
        """
        logger.error(f"Exec failed, attempting fallback: {exc}")
        
        try:
            # Try to get minimal information from prep_result
            if isinstance(prep_result, dict):
                email = prep_result.get("email", {})
                sender_email = prep_result.get("sender_email")
                
                if sender_email:
                    # Try to send a minimal response
                    settings = get_settings()
                    email_service = EmailService(settings)
                    
                    minimal_response = f"""Hi there!

I received your email but encountered a technical issue while processing it.

Please try sending your message again, or contact support if the problem persists.

Thanks for your patience!

Best regards,
PocketFlow Assistant"""
                    
                    # Build threading headers for fallback email
                    try:
                        in_reply_to, references = build_threading_headers(
                            original_message_id=email.get("message_id"),
                            original_in_reply_to=email.get("in_reply_to"),
                            original_references=email.get("references"),
                            thread_id=email.get("thread_id"),
                            email_id=email.get("id")
                        )
                    except Exception as e:
                        logger.warning(f"Failed to build threading headers in fallback: {e}")
                        in_reply_to = None
                        references = None
                    
                    # Build subject
                    original_subject = email.get("subject", "")
                    if original_subject and original_subject.strip():
                        clean_subject = original_subject.strip()
                        for prefix in ["Re:", "RE:", "re:"]:
                            if clean_subject.startswith(prefix):
                                clean_subject = clean_subject[len(prefix):].strip()
                        reply_subject = f"Re: {clean_subject}"
                    else:
                        reply_subject = ""
                    
                    try:
                        send_request = EmailSendRequest(
                            to=sender_email,
                            subject=reply_subject,
                            body=minimal_response,
                            in_reply_to=in_reply_to,
                            references=references
                        )
                        success = email_service.send_email(send_request)
                        if success:
                            logger.info("Fallback response sent successfully")
                            return {"success": True, "fallback": True}
                    except Exception as fallback_error:
                        logger.error(f"Fallback send also failed: {fallback_error}")
        except Exception as e:
            logger.error(f"Fallback method failed: {e}")
        
        return None
