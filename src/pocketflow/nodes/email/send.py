"""
Send email node for PocketFlow.

This node handles sending emails with proper threading and attachments.
"""

from typing import Dict, Any, Optional

from ...core.node import SimpleNode
from ...core.types import SharedState, EmailSendRequest
from ...services import email_service
from ...utils.logging import get_logger
from ...utils.errors import EmailError


class SendEmailNode(SimpleNode):
    """Node for sending emails with proper threading."""
    
    def __init__(self, name: str = "send_email"):
        super().__init__(name)
        self.logger = get_logger("SendEmailNode")
    
    def process(self, shared: SharedState) -> Dict[str, Any]:
        """
        Send email based on agent action parameters.
        
        Args:
            shared: Shared state containing email context and agent action
            
        Returns:
            Processing result with routing information
        """
        try:
            self.logger.info("Preparing to send email...")
            
            # Get agent action and parameters
            agent_action = shared.get("agent_action", {})
            params = agent_action.get("parameters", {})
            email = shared.get("email", {})
            
            # Determine recipient
            to = params.get("to")
            if not to:
                to = shared.get("user") or self._extract_email(email.get("from", ""))
            
            # Determine subject
            subject = params.get("subject")
            if subject is None:
                subject = email.get("subject", "")
            if subject and not subject.lower().startswith("re:"):
                subject = f"Re: {subject}"
            
            # Prepare email body
            body = params.get("body", "")
            if not body or not isinstance(body, str) or not body.strip():
                body = "Sorry, there was an error generating your reply."
            
            # Add extra body content if available
            send_body_extra = shared.get("send_body_extra", "")
            if send_body_extra:
                body += f"\n\n{send_body_extra}"
            
            # Create email send request
            send_request = EmailSendRequest(
                to=to,
                subject=subject,
                body=body,
                cc=params.get("cc"),
                attachment=shared.get("attachment")
            )
            
            self.logger.info(f"Sending email to: {to}, subject: {subject}")
            
            # Send email using email service
            success = email_service.send_email(send_request)
            
            if success:
                self.logger.info("Email sent successfully")
                shared["sender_have_gotten_response"] = True
                return {"route": "default"}
            else:
                self.logger.error("Failed to send email")
                return {"route": "send_failed", "error": "Email sending failed"}
                
        except EmailError as e:
            self.logger.error(f"Email sending failed: {e}")
            return {"route": "send_failed", "error": str(e)}
        except Exception as e:
            self.logger.error(f"Unexpected error in SendEmailNode: {e}")
            return {"route": "send_failed", "error": str(e)}
    
    def _extract_email(self, sender: str) -> str:
        """Extract email address from sender string."""
        import re
        # Use raw string and single backslash for dot
        match = re.search(r'<([A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,})>', sender)
        if match:
            return match.group(1)
        # fallback: if sender is just the email
        match = re.search(r'([A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,})', sender)
        return match.group(1) if match else sender 