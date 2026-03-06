"""
Email agent for PocketFlow.

This agent handles email processing, conversation management, and communication
with users through email.
"""

from typing import Dict, Any, List
from ..agents.base_agent import BaseAgent, AgentAction, AgentDecision
from ..core.types import SharedState, EmailSendRequest
from ..services.email_service import EmailService
from ..services import llm_service
from ..utils.logging import get_logger
from ..utils.email_utils import build_threading_headers
from ..config.settings import get_settings


class EmailAgent(BaseAgent):
    """Agent specialized in email processing and communication."""
    
    def __init__(self):
        super().__init__("EmailAgent")
        self.email_processed = False
        self.conversation_context = {}
        self.response_prepared = False
    
    def analyze(self, shared: SharedState) -> AgentDecision:
        """Analyze the current state and decide what to do."""
        
        email = shared.get("email", {})
        body = email.get("body", "")
        
        # If we haven't processed the email yet
        if not self.email_processed:
            return AgentDecision(
                action=AgentAction.PROCESS_WITH_LLM,
                confidence=0.9,
                reasoning="Processing email with LLM",
                parameters={"email_body": body, "process_type": "conversation"},
                next_agent=None
            )
        
        # If we have a prepared response, send it
        if self.response_prepared:
            return AgentDecision(
                action=AgentAction.SEND_EMAIL,
                confidence=1.0,
                reasoning="Response prepared, sending email",
                parameters={"response": self.conversation_context.get("response")},
                next_agent=None
            )
        
        # Continue processing
        return AgentDecision(
            action=AgentAction.PROCESS_WITH_LLM,
            confidence=0.7,
            reasoning="Continuing email processing",
            parameters={"email_body": body, "process_type": "refinement"},
            next_agent=None
        )
    
    def execute(self, action: AgentAction, shared: SharedState, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the email action."""
        
        if action == AgentAction.PROCESS_WITH_LLM:
            return self._process_email_with_llm(shared, parameters)
        elif action == AgentAction.SEND_EMAIL:
            return self._send_email_response(shared, parameters)
        elif action == AgentAction.FETCH_EMAIL:
            return self._fetch_email(shared, parameters)
        else:
            return {"success": False, "error": f"Unknown action: {action}"}
    
    def _process_email_with_llm(self, shared: SharedState, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Process email with LLM for conversation management."""
        try:
            email_body = parameters.get("email_body", "")
            process_type = parameters.get("process_type", "conversation")
            
            self.logger.info(f"Processing email with LLM: {process_type}")
            
            # Get conversation context
            conversation_history = shared.get("conversation_history", [])
            user_email = shared.get("user", "")
            
            # Prepare context for LLM
            context = {
                "user_email": user_email,
                "conversation_history": conversation_history,
                "current_email": email_body,
                "process_type": process_type
            }
            
            # Call LLM for processing
            llm_response = self._call_llm_for_email_processing(context)
            
            if not llm_response.get("success"):
                return {"success": False, "error": "LLM processing failed"}
            
            # Store processed response
            self.conversation_context = {
                "response": llm_response.get("response", ""),
                "intent": llm_response.get("intent", "general"),
                "confidence": llm_response.get("confidence", 0.8),
                "requires_action": llm_response.get("requires_action", False)
            }
            
            self.email_processed = True
            self.response_prepared = True
            self.update_context({"conversation_context": self.conversation_context})
            
            self.logger.info("Email processed successfully with LLM")
            
            return {
                "success": True,
                "response": self.conversation_context,
                "intent": self.conversation_context.get("intent")
            }
            
        except Exception as e:
            self.logger.error(f"Error in email processing: {e}")
            return {"success": False, "error": str(e)}
    
    def _call_llm_for_email_processing(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Call LLM for email processing."""
        try:
            user_email = context.get("user_email", "")
            conversation_history = context.get("conversation_history", [])
            current_email = context.get("current_email", "")
            process_type = context.get("process_type", "conversation")
            
            # Prepare conversation history for LLM
            history_text = ""
            for i, msg in enumerate(conversation_history[-5:], 1):  # Last 5 messages
                history_text += f"Message {i}: {msg.get('content', '')}\n"
            
            prompt = f"""
You are an intelligent email assistant processing a user's email.

User: {user_email}
Current Email: {current_email}
Process Type: {process_type}

Conversation History:
{history_text}

Please analyze this email and provide an appropriate response. Consider:
1. The user's intent and needs
2. The conversation context
3. Whether any specific actions are required
4. The tone and style of the response

Respond with a JSON object:
{{
    "response": "your response text",
    "intent": "general|question|request|complaint|feedback",
    "confidence": 0.0-1.0,
    "requires_action": true/false,
    "suggested_actions": ["action1", "action2"]
}}

Keep responses helpful, concise, and appropriate for email communication.
"""
            
            # Call LLM
            response = llm_service.call_llm([
                {"role": "system", "content": "You are a helpful email assistant that processes user emails and provides appropriate responses."},
                {"role": "user", "content": prompt}
            ])
            
            # Parse LLM response
            import json
            try:
                response_text = response.get("content", "")
                
                # Extract JSON from response
                start_idx = response_text.find('{')
                end_idx = response_text.rfind('}') + 1
                
                if start_idx != -1 and end_idx > start_idx:
                    json_str = response_text[start_idx:end_idx]
                    result = json.loads(json_str)
                else:
                    # Fallback response
                    result = {
                        "response": "Thank you for your email. I'm here to help!",
                        "intent": "general",
                        "confidence": 0.7,
                        "requires_action": False,
                        "suggested_actions": []
                    }
                
                return {"success": True, **result}
                
            except json.JSONDecodeError as e:
                self.logger.warning(f"Failed to parse LLM JSON response: {e}")
                return {
                    "success": True,
                    "response": "Thank you for your email. I'm here to help!",
                    "intent": "general",
                    "confidence": 0.6,
                    "requires_action": False,
                    "suggested_actions": []
                }
                
        except Exception as e:
            self.logger.error(f"Error calling LLM for email processing: {e}")
            return {"success": False, "error": str(e)}
    
    def _send_email_response(self, shared: SharedState, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Send email response to user with proper threading."""
        try:
            response = parameters.get("response", self.conversation_context.get("response", ""))
            user_email = shared.get("user", "")
            
            self.logger.info(f"Sending email response to {user_email}")
            
            # Get email service
            settings = get_settings()
            email_service = EmailService(settings)
            
            # Get original email data for threading
            email = shared.get("email", {})
            original_subject = email.get("subject", "")
            
            # Build threading headers
            in_reply_to, references = build_threading_headers(
                original_message_id=email.get("message_id"),
                original_in_reply_to=email.get("in_reply_to"),
                original_references=email.get("references"),
                thread_id=email.get("thread_id"),
                email_id=email.get("id")
            )
            
            # Log threading headers for debugging
            self.logger.info(f"Threading headers - In-Reply-To: {in_reply_to}, References: {references}")
            
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
            
            # Prepare email send request with threading headers
            send_request = EmailSendRequest(
                to=user_email,
                subject=reply_subject,
                body=response,
                in_reply_to=in_reply_to,
                references=references
            )
            
            # Send email
            success = email_service.send_email(send_request)
            
            if not success:
                return {"success": False, "error": "Failed to send email"}
            
            # Update conversation history
            conversation_history = shared.get("conversation_history", [])
            conversation_history.append({
                "type": "assistant",
                "content": response,
                "timestamp": "now"
            })
            shared["conversation_history"] = conversation_history
            
            self.logger.info("Email response sent successfully with threading headers")
            
            return {
                "success": True,
                "message": "Email response sent",
                "email_sent": True
            }
            
        except Exception as e:
            self.logger.error(f"Error sending email response: {e}")
            return {"success": False, "error": str(e)}
    
    def _fetch_email(self, shared: SharedState, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Fetch email from the email service."""
        try:
            user_email = shared.get("user", "")
            
            self.logger.info(f"Fetching email for {user_email}")
            
            # Get email service
            settings = get_settings()
            email_service = EmailService(settings)
            
            # Fetch unread emails
            emails = email_service.fetch_unread_emails()
            
            if not emails:
                self.logger.info("No new emails found")
                return {
                    "success": True,
                    "emails_found": 0,
                    "email": None
                }
            
            # Update shared state with fetched email
            if emails:
                # Convert EmailData to dict format
                email_data = emails[0]
                shared["email"] = {
                    "id": email_data.id,
                    "subject": email_data.subject,
                    "from": email_data.from_,
                    "body": email_data.body,
                    "date": email_data.received_at,
                    "message_id": email_data.message_id,
                    "thread_id": email_data.thread_id,
                    "in_reply_to": email_data.in_reply_to,
                    "references": email_data.references
                }
                self.logger.info("Email fetched successfully")
            
            return {
                "success": True,
                "emails_found": len(emails),
                "email": shared["email"] if emails else None
            }
            
        except Exception as e:
            self.logger.error(f"Error fetching email: {e}")
            return {"success": False, "error": str(e)}
    
    def get_capabilities(self) -> List[str]:
        """Get email agent capabilities."""
        return [
            "email_processing",
            "conversation_management",
            "llm_enhanced_responses",
            "email_sending",
            "context_aware_communication",
            "intent_recognition"
        ]
    
    def reset(self):
        """Reset email agent state."""
        super().reset()
        self.email_processed = False
        self.conversation_context = {}
        self.response_prepared = False
        self.logger.info("Email agent reset")
    
    def get_email_status(self) -> Dict[str, Any]:
        """Get current email processing status."""
        return {
            "email_processed": self.email_processed,
            "response_prepared": self.response_prepared,
            "conversation_context": self.conversation_context,
            "context": self.context
        } 