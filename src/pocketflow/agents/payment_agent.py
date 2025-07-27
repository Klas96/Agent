"""
Payment agent for PocketFlow.

This agent handles Bitcoin payment processing, payment requests, and token
management for users.
"""

import time
from typing import Dict, Any, List
from ..agents.base_agent import BaseAgent, AgentAction, AgentDecision
from ..core.types import SharedState
from ..services import BitcoinService, EmailService
from ..utils.logging import get_logger


class PaymentAgent(BaseAgent):
    """Agent specialized in payment processing and token management."""
    
    def __init__(self):
        super().__init__("PaymentAgent")
        self.payment_requested = False
        self.payment_processed = False
        self.payment_details = {}
        self.user_tokens = 0
        self.bitcoin_service = BitcoinService()
        self.email_service = EmailService()
    
    def analyze(self, shared: SharedState) -> AgentDecision:
        """Analyze the current state and decide what to do."""
        
        user_email = shared.get("user", "")
        flow_type = shared.get("flow_type")
        
        # Check if user has tokens
        if self._user_has_tokens(user_email):
            return AgentDecision(
                action=AgentAction.FINISH,
                confidence=1.0,
                reasoning="User has sufficient tokens",
                parameters={"tokens_available": True},
                next_agent=None
            )
        
        # If we haven't requested payment yet
        if not self.payment_requested:
            return AgentDecision(
                action=AgentAction.REQUEST_PAYMENT,
                confidence=0.9,
                reasoning="User needs tokens, requesting payment",
                parameters={"user_email": user_email, "amount": "0.001 BTC"},
                next_agent=None
            )
        
        # If payment is processed, check if tokens were received
        if self.payment_processed:
            if self._user_has_tokens(user_email):
                return AgentDecision(
                    action=AgentAction.FINISH,
                    confidence=1.0,
                    reasoning="Payment received, tokens available",
                    parameters={"tokens_available": True},
                    next_agent=None
                )
            else:
                return AgentDecision(
                    action=AgentAction.WAIT_FOR_INPUT,
                    confidence=0.8,
                    reasoning="Payment processed but tokens not yet available",
                    parameters={"wait_time": "5 minutes"},
                    next_agent=None
                )
        
        # Continue payment processing
        return AgentDecision(
            action=AgentAction.REQUEST_PAYMENT,
            confidence=0.7,
            reasoning="Continuing payment request",
            parameters={"user_email": user_email, "amount": "0.001 BTC"},
            next_agent=None
        )
    
    def execute(self, action: AgentAction, shared: SharedState, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the payment action."""
        
        if action == AgentAction.REQUEST_PAYMENT:
            return self._request_payment(shared, parameters)
        elif action == AgentAction.WAIT_FOR_INPUT:
            return self._wait_for_payment(shared, parameters)
        elif action == AgentAction.SEND_EMAIL:
            return self._send_payment_email(shared, parameters)
        else:
            return {"success": False, "error": f"Unknown action: {action}"}
    
    def _request_payment(self, shared: SharedState, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Request payment from user."""
        try:
            user_email = parameters.get("user_email", "")
            amount = parameters.get("amount", "0.001 BTC")
            
            self.logger.info(f"Requesting payment from {user_email}: {amount}")
            
            # Generate Bitcoin address for payment using BitcoinService
            btc_address = self.bitcoin_service.get_or_create_address(user_email)
            
            if not btc_address:
                return {"success": False, "error": "Failed to generate payment address"}
            
            # Store payment details
            self.payment_details = {
                "address": btc_address,
                "amount": amount,
                "user_email": user_email,
                "payment_id": f"pay_{user_email}_{int(time.time())}"
            }
            
            self.payment_requested = True
            self.update_context({"payment_details": self.payment_details})
            
            # Send payment request email
            email_result = self._send_payment_request_email(shared, self.payment_details)
            
            self.logger.info("Payment request processed successfully")
            
            return {
                "success": True,
                "payment_address": result.get("address"),
                "amount": amount,
                "email_sent": email_result.get("success", False)
            }
            
        except Exception as e:
            self.logger.error(f"Error in payment request: {e}")
            return {"success": False, "error": str(e)}
    
    def _send_payment_request_email(self, shared: SharedState, payment_details: Dict[str, Any]) -> Dict[str, Any]:
        """Send payment request email to user."""
        try:
            user_email = payment_details.get("user_email", "")
            address = payment_details.get("address", "")
            amount = payment_details.get("amount", "")
            
            # Prepare email content
            subject = "PocketFlow - Payment Required"
            body = f"""
Hello!

To use PocketFlow's advanced features, you need to purchase tokens.

Payment Details:
- Amount: {amount}
- Bitcoin Address: {address}

Please send the payment to the Bitcoin address above. Once the payment is confirmed, you'll receive tokens to use PocketFlow's features.

Features you'll unlock:
- Content generation (songs, images, documents)
- Research and investigation
- Advanced email processing

Thank you for using PocketFlow!

Best regards,
The PocketFlow Team
"""
            
            # Send email
            email_response = {
                "to": user_email,
                "subject": subject,
                "body": body,
                "attachments": []
            }
            
            result = email_service.send_email(email_response)
            
            return {"success": result.get("success", False)}
            
        except Exception as e:
            self.logger.error(f"Error sending payment request email: {e}")
            return {"success": False, "error": str(e)}
    
    def _wait_for_payment(self, shared: SharedState, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Wait for payment confirmation."""
        try:
            wait_time = parameters.get("wait_time", "5 minutes")
            user_email = shared.get("user", "")
            
            self.logger.info(f"Waiting for payment confirmation: {wait_time}")
            
            # Check if payment was received using BitcoinService
            payment_id = self.payment_details.get("payment_id")
            if payment_id in self.bitcoin_service._pending_payments:
                payment_status = self.bitcoin_service.check_payment_status(payment_id)
                if payment_status.get("status") == "confirmed":
                    self.payment_processed = True
                    self.logger.info("Payment confirmed!")
                    
                    return {
                        "success": True,
                        "payment_confirmed": True,
                        "tokens_granted": True
                    }
                else:
                    self.logger.info("Payment not yet confirmed")
                    
                    return {
                        "success": True,
                        "payment_confirmed": False,
                        "tokens_granted": False
                    }
            else:
                self.logger.info("Payment not found")
                
                return {
                    "success": True,
                    "payment_confirmed": False,
                    "tokens_granted": False
                }
                self.payment_processed = True
                self.logger.info("Payment confirmed!")
                
                return {
                    "success": True,
                    "payment_confirmed": True,
                    "tokens_granted": True
                }
            else:
                self.logger.info("Payment not yet confirmed")
                
                return {
                    "success": True,
                    "payment_confirmed": False,
                    "tokens_granted": False
                }
            
        except Exception as e:
            self.logger.error(f"Error waiting for payment: {e}")
            return {"success": False, "error": str(e)}
    
    def _send_payment_email(self, shared: SharedState, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Send payment-related email."""
        try:
            user_email = shared.get("user", "")
            email_type = parameters.get("email_type", "payment_request")
            
            if email_type == "payment_confirmed":
                subject = "PocketFlow - Payment Confirmed!"
                body = """
Hello!

Great news! Your payment has been confirmed and your tokens have been added to your account.

You can now use all of PocketFlow's features:
- Generate songs, images, and documents
- Research and investigate topics
- Advanced email processing

Thank you for your payment!

Best regards,
The PocketFlow Team
"""
            else:
                subject = "PocketFlow - Payment Required"
                body = """
Hello!

To use PocketFlow's advanced features, you need to purchase tokens.

Please send 0.001 BTC to the address provided in your previous email.

Thank you!

Best regards,
The PocketFlow Team
"""
            
            # Send email
            email_response = {
                "to": user_email,
                "subject": subject,
                "body": body,
                "attachments": []
            }
            
            result = self.email_service.send_email(email_response)
            
            return {"success": result.get("success", False)}
            
        except Exception as e:
            self.logger.error(f"Error sending payment email: {e}")
            return {"success": False, "error": str(e)}
    
    def _user_has_tokens(self, user_email: str) -> bool:
        """Check if user has sufficient tokens."""
        try:
            # Check user's token balance using database service
            from ..services import DatabaseService
            db_service = DatabaseService()
            user_info = db_service.get_user(user_email)
            
            if user_info:
                self.user_tokens = user_info.get("tokens", 0)
                return self.user_tokens > 0
            else:
                return False
                
        except Exception as e:
            self.logger.error(f"Error checking user tokens: {e}")
            return False
    
    def get_capabilities(self) -> List[str]:
        """Get payment agent capabilities."""
        return [
            "bitcoin_payment_processing",
            "payment_address_generation",
            "payment_status_checking",
            "token_management",
            "payment_email_communication",
            "user_balance_tracking"
        ]
    
    def reset(self):
        """Reset payment agent state."""
        super().reset()
        self.payment_requested = False
        self.payment_processed = False
        self.payment_details = {}
        self.user_tokens = 0
        self.logger.info("Payment agent reset")
    
    def get_payment_status(self) -> Dict[str, Any]:
        """Get current payment status."""
        return {
            "payment_requested": self.payment_requested,
            "payment_processed": self.payment_processed,
            "payment_details": self.payment_details,
            "user_tokens": self.user_tokens,
            "context": self.context
        } 