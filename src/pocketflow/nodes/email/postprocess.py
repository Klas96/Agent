"""
Email post-processing node for PocketFlow.

This module contains the PostprocessEmailNode for final email processing.
"""

from typing import Dict, Any, Optional
from ...core.node import SimpleNode
from ...core.types import SharedState
from ...utils.logging import get_logger
from ...utils.errors import EmailError
from ...services import email_service
from ...utils.email_utils import extract_email


class PostProcessNode(SimpleNode):
    """Node for post-processing and sending email responses."""
    
    def __init__(self, name: str = "post_process"):
        super().__init__(name)
        self.logger = get_logger("PostProcessNode")
    
    def process(self, shared: SharedState) -> Optional[Dict[str, Any]]:
        """Process and send email response."""
        self.logger.info(f"[DEBUG] PostProcessNode.prep called with shared: {shared}")
        
        if shared.get("sender_have_gotten_response") is True:
            self.logger.info("[DEBUG] PostProcessNode.prep: sender_have_gotten_response is True, skipping.")
            return None
            
        email = shared.get("email")
        if not email:
            self.logger.info("[DEBUG] PostProcessNode.prep: No email found, skipping.")
            return None
            
        user_email = shared.get("user", "")
        if not user_email:
            user_email = extract_email(email.get("from", ""))
            
        result = dict(email)
        result["out_of_tokens"] = shared.get("out_of_tokens", False)
        result["btc_address"] = shared.get("btc_address")
        result["user_email"] = user_email
        result["reply_body"] = shared.get("reply_body", "")
        result["attachment"] = shared.get("attachment")
        
        self.logger.info(f"[DEBUG] PostProcessNode.exec called with data: {result}")
        
        if result is None:
            self.logger.info("[DEBUG] PostProcessNode.exec: No data, returning None.")
            return None
            
        # Use the sender's email as the recipient for the reply
        recipient = result.get("user_email") or result.get("from")
        if not recipient:
            self.logger.error("[PostProcessNode] No recipient email found!")
            return None
            
        # Set up proper reply headers
        in_reply_to = result.get("message_id") or result.get("in_reply_to")
        references = result.get("message_id") or result.get("references")
        
        try:
            # Use the email service instead of direct function call
            send_request = EmailSendRequest(
                to=recipient,
                subject=f"Re: {result['subject']}",
                body=result.get("reply_body", ""),
                attachment=result.get("attachment"),
                in_reply_to=in_reply_to,
                references=references
            )
            
            success = email_service.send_email(send_request)
            self.logger.info(f"[DEBUG] PostProcessNode.post called with exec_res: {success}")
            return success
            
        except Exception as e:
            self.logger.error(f"[PostProcessNode] Error sending email: {e}")
            return None 