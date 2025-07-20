"""
Payment processing flow for PocketFlow.

This flow handles Bitcoin payment processing and token management.
"""

from typing import Dict, Any, Optional

from ..core.flow import Flow, FlowBuilder
from ..core.types import FlowType, SharedState
from ..nodes import (
    PurchaseTokensWithBitcoinNode,
    SendEmailNode
)
from ..utils.logging import get_logger


class PaymentProcessingFlow:
    """Flow for handling Bitcoin payment processing."""
    
    def __init__(self):
        self.logger = get_logger("PaymentProcessingFlow")
        self._flow = self._build_flow()
    
    def _build_flow(self) -> Flow:
        """Build the payment processing flow."""
        return (FlowBuilder("payment_processing", FlowType.PAYMENT_PENDING, requires_tokens=False)
                .add_step("payment_request", PurchaseTokensWithBitcoinNode("payment_request"))
                .add_step("send_email", SendEmailNode("send_email"))
                .set_start("payment_request")
                .add_end_step("send_email")
                .add_end_step("finish")
                # Payment request routing
                .add_routing("payment_request", "send", "send_email")
                .add_routing("payment_request", "default", "finish")
                # Email sending routing
                .add_routing("send_email", "send_failed", "finish")
                .add_routing("send_email", "default", "finish")
                .build())
    
    def run(self, shared: SharedState) -> Dict[str, Any]:
        """
        Run the payment processing flow.
        
        Args:
            shared: Shared state containing payment context
            
        Returns:
            Flow execution result
        """
        try:
            self.logger.info("Starting payment processing flow")
            result = self._flow.run(shared)
            
            if result.success:
                self.logger.info("Payment processing flow completed successfully")
            else:
                self.logger.error(f"Payment processing flow failed: {result.error}")
            
            return {
                "success": result.success,
                "error": result.error,
                "final_state": dict(shared) if shared else None
            }
            
        except Exception as e:
            self.logger.error(f"Unexpected error in PaymentProcessingFlow: {e}")
            return {
                "success": False,
                "error": str(e),
                "final_state": dict(shared) if shared else None
            }
    
    def get_flow_info(self) -> Dict[str, Any]:
        """Get information about the flow."""
        return {
            "name": "payment_processing",
            "type": FlowType.PAYMENT_PENDING,
            "requires_tokens": False,
            "steps": [
                "payment_request",
                "send_email"
            ],
            "capabilities": [
                "bitcoin_payment_requests",
                "address_management",
                "payment_tracking",
                "email_sending"
            ],
            "specializations": [
                "payment_focused",
                "bitcoin_integration",
                "token_management"
            ]
        }


# Global payment processing flow instance
payment_processing_flow = PaymentProcessingFlow() 