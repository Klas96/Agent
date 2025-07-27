"""
Bitcoin payment node for PocketFlow.

This node handles Bitcoin payment requests for token purchases.
"""

from typing import Dict, Any, Optional

from ...core.node import SimpleNode
from ...core.types import SharedState, PaymentRequest
from ...services.bitcoin_service import BitcoinService
from ...utils.logging import get_logger
from ...utils.errors import BitcoinError


class PurchaseTokensWithBitcoinNode(SimpleNode):
    """Node for handling Bitcoin payment requests for token purchases."""
    
    LLM_CALL_PRICE_USD = 0.01  # 1 token = $0.01 (matches LLM call price)
    DEFAULT_NUM_TOKENS = 10
    
    def __init__(self, name: str = "purchase_tokens_bitcoin"):
        super().__init__(name)
        self.logger = get_logger("PurchaseTokensWithBitcoinNode")
    
    def process(self, shared: SharedState) -> Dict[str, Any]:
        """
        Create Bitcoin payment request for token purchase.
        
        Args:
            shared: Shared state containing user email
            
        Returns:
            Processing result with routing information
        """
        try:
            # Extract email from shared state
            email = None
            if hasattr(shared, 'email') and shared.email:
                from_field = shared.email.get("from", "")
                if "<" in from_field and ">" in from_field:
                    email = from_field.split("<")[1].split(">")[0]
                else:
                    email = from_field
            elif hasattr(shared, 'user') and shared.user:
                email = shared.user
            
            if not email:
                self.logger.warning("No user email found")
                return {"route": "default", "error": "No user email found"}
            
            self.logger.info(f"Creating Bitcoin payment request for {email}")
            
            # Initialize Bitcoin service
            bitcoin_service = BitcoinService()
            
            # Get or create Bitcoin address for user
            btc_address = bitcoin_service.get_or_create_address(email)
            
            # Calculate payment amount
            num_tokens = self.DEFAULT_NUM_TOKENS
            btc_price_usd = bitcoin_service.get_btc_price()
            btc_per_token = self.LLM_CALL_PRICE_USD / btc_price_usd
            amount_btc = btc_per_token * num_tokens
            
            # Create payment request
            payment_request = PaymentRequest(
                user_email=email,
                amount_usd=num_tokens * self.LLM_CALL_PRICE_USD,
                btc_address=btc_address,
                description=f"Purchase {num_tokens} tokens for PocketFlow"
            )
            
            # Create payment request using Bitcoin service
            payment_info = bitcoin_service.create_payment_request(payment_request)
            
            # Build instructions for user
            instructions = (
                f"To buy {num_tokens} tokens, send {amount_btc:.8f} BTC "
                f"(≈ ${num_tokens * self.LLM_CALL_PRICE_USD:.2f}) to your personal address: {btc_address}.\n"
                f"Current BTC/USD price: ${btc_price_usd:.2f} (1 token = ${self.LLM_CALL_PRICE_USD:.4f})\n"
                "Once payment is received, your tokens will be credited automatically."
            )
            
            # Store payment info in shared state using attribute assignment
            setattr(shared, 'payment_info', payment_info)
            setattr(shared, 'btc_address', btc_address)
            setattr(shared, 'reply_body', instructions)
            
            self.logger.info(f"Payment request created: {payment_info}")
            
            return {"route": "send"}
            
        except BitcoinError as e:
            self.logger.error(f"Bitcoin service error: {e}")
            setattr(shared, 'reply_body', f"Sorry, I encountered an error while setting up the payment: {str(e)}")
            return {"route": "default", "error": str(e)}
        except Exception as e:
            self.logger.error(f"Unexpected error in PurchaseTokensWithBitcoinNode: {e}")
            setattr(shared, 'reply_body', f"Sorry, I encountered an error while setting up the payment: {str(e)}")
            return {"route": "default", "error": str(e)} 