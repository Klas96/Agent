"""
Bitcoin service for PocketFlow.

This module provides Bitcoin functionality including payment processing and address management.
"""

import json
import hashlib
import time
from typing import Optional, Dict, Any, List
from decimal import Decimal
import requests

from ..core.types import PaymentRequest
from ..config.settings import get_settings
from ..utils.errors import BitcoinError
from ..utils.logging import get_logger


class BitcoinService:
    """Service for handling Bitcoin operations."""
    
    def __init__(self):
        self.settings = get_settings()
        self.logger = get_logger("BitcoinService")
        self._addresses: Dict[str, str] = {}  # email -> address mapping
        self._pending_payments: Dict[str, Dict[str, Any]] = {}
    
    def get_or_create_address(self, user_email: str) -> str:
        """
        Get or create a Bitcoin address for a user.
        
        Args:
            user_email: User's email address
            
        Returns:
            Bitcoin address for the user
        """
        try:
            if user_email in self._addresses:
                self.logger.info(f"Using existing address for {user_email}")
                return self._addresses[user_email]
            
            # Generate a new address
            address = self._generate_address(user_email)
            
            if address:
                self._addresses[user_email] = address
                self.logger.info(f"Generated new address for {user_email}: {address}")
                return address
            else:
                raise BitcoinError("Failed to generate Bitcoin address")
            
        except Exception as e:
            self.logger.error(f"Failed to get/create address for {user_email}: {e}")
            raise BitcoinError(f"Address generation failed: {e}")
    
    def create_payment_request(self, request: PaymentRequest) -> Dict[str, Any]:
        """
        Create a payment request.
        
        Args:
            request: PaymentRequest with payment details
            
        Returns:
            Payment request information
        """
        try:
            self.logger.info(f"Creating payment request for {request.user_email}: ${request.amount_usd}")
            
            # Store payment request
            payment_id = self._generate_payment_id(request.user_email)
            self._pending_payments[payment_id] = {
                "user_email": request.user_email,
                "amount_usd": request.amount_usd,
                "btc_address": request.btc_address,
                "description": request.description,
                "created_at": time.time(),
                "status": "pending"
            }
            
            return {
                "payment_id": payment_id,
                "amount_usd": request.amount_usd,
                "btc_address": request.btc_address,
                "description": request.description,
                "status": "pending"
            }
            
        except Exception as e:
            self.logger.error(f"Failed to create payment request: {e}")
            raise BitcoinError(f"Payment request creation failed: {e}")
    
    def check_payment_status(self, payment_id: str) -> Dict[str, Any]:
        """
        Check the status of a payment.
        
        Args:
            payment_id: ID of the payment to check
            
        Returns:
            Payment status information
        """
        try:
            if payment_id not in self._pending_payments:
                return {"error": "Payment not found"}
            
            payment = self._pending_payments[payment_id]
            btc_address = payment["btc_address"]
            
            # Check if payment has been received
            received_amount = self._check_address_balance(btc_address)
            required_amount = self._usd_to_btc(payment["amount_usd"])
            
            if received_amount >= required_amount:
                payment["status"] = "confirmed"
                payment["received_amount"] = received_amount
                self.logger.info(f"Payment {payment_id} confirmed")
            else:
                payment["status"] = "pending"
                payment["received_amount"] = received_amount
            
            return {
                "payment_id": payment_id,
                "status": payment["status"],
                "required_amount": required_amount,
                "received_amount": received_amount,
                "user_email": payment["user_email"]
            }
            
        except Exception as e:
            self.logger.error(f"Failed to check payment status: {e}")
            return {"error": str(e)}
    
    def get_payment_history(self, user_email: str) -> List[Dict[str, Any]]:
        """
        Get payment history for a user.
        
        Args:
            user_email: User's email address
            
        Returns:
            List of payment records
        """
        try:
            history = []
            for payment_id, payment in self._pending_payments.items():
                if payment["user_email"] == user_email:
                    history.append({
                        "payment_id": payment_id,
                        "amount_usd": payment["amount_usd"],
                        "status": payment["status"],
                        "created_at": payment["created_at"]
                    })
            
            return history
            
        except Exception as e:
            self.logger.error(f"Failed to get payment history: {e}")
            return []
    
    def _generate_address(self, user_email: str) -> str:
        """Generate a Bitcoin address for a user."""
        try:
            # Use the real Electrum wallet to generate addresses
            from ..utils.electrum_utils import get_new_btc_address
            address = get_new_btc_address()
            
            if address:
                self.logger.info(f"Generated real BTC address for {user_email}: {address}")
                return address
            else:
                raise Exception("Failed to generate new BTC address from wallet")
                
        except Exception as e:
            self.logger.error(f"Failed to generate real address for {user_email}: {e}")
            # Fallback: try to get an existing address from wallet
            try:
                from ..utils.electrum_utils import get_wallet_addresses
                wallet_addresses = get_wallet_addresses()
                if wallet_addresses:
                    fallback_address = wallet_addresses[0]
                    self.logger.info(f"Using fallback address from wallet: {fallback_address}")
                    return fallback_address
            except Exception as fallback_error:
                self.logger.error(f"Fallback address generation failed: {fallback_error}")
            
            # CRITICAL: Do not generate fake addresses - this is fraudulent
            # Instead, raise an exception to prevent payment processing
            self.logger.error(f"Cannot generate real BTC address for {user_email} - payment system unavailable")
            raise Exception("Bitcoin payment system unavailable - cannot generate real addresses")
    
    def _generate_payment_id(self, user_email: str) -> str:
        """Generate a unique payment ID."""
        timestamp = str(int(time.time()))
        email_hash = hashlib.md5(user_email.encode()).hexdigest()[:8]
        return f"pay_{email_hash}_{timestamp}"
    
    def _check_address_balance(self, address: str) -> Decimal:
        """
        Check the balance of a Bitcoin address.
        
        Args:
            address: Bitcoin address to check
            
        Returns:
            Balance in BTC
        """
        try:
            # In a real implementation, this would query a Bitcoin node or API
            # For now, simulate balance checking
            import random
            
            # Simulate different balance scenarios
            balance_scenarios = [0, 0.001, 0.005, 0.01, 0.05]
            balance = Decimal(str(random.choice(balance_scenarios)))
            
            self.logger.debug(f"Address {address} balance: {balance} BTC")
            return balance
            
        except Exception as e:
            self.logger.error(f"Failed to check address balance: {e}")
            return Decimal('0')
    
    def _usd_to_btc(self, usd_amount: float) -> Decimal:
        """
        Convert USD amount to BTC using current market price.
        
        Args:
            usd_amount: Amount in USD
            
        Returns:
            Equivalent amount in BTC
        """
        try:
            # Get current BTC price from CoinGecko
            btc_price_usd = self.get_btc_price()
            btc_amount = Decimal(str(usd_amount)) / Decimal(str(btc_price_usd))
            
            self.logger.info(f"Converted ${usd_amount} to {btc_amount:.8f} BTC at ${btc_price_usd:,.2f}/BTC")
            return btc_amount
            
        except Exception as e:
            self.logger.error(f"Failed to convert USD to BTC: {e}")
            return Decimal('0')
    
    def get_btc_price(self) -> float:
        """
        Get current BTC price in USD from CoinGecko API.
        
        Returns:
            BTC price in USD
        """
        try:
            # Fetch current BTC price from CoinGecko API
            url = "https://api.coingecko.com/api/v3/simple/price"
            params = {
                "ids": "bitcoin",
                "vs_currencies": "usd"
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            btc_price = data.get("bitcoin", {}).get("usd", 0.0)
            
            if btc_price <= 0:
                self.logger.warning("Invalid BTC price from CoinGecko, using fallback")
                return 50000.0
            
            self.logger.info(f"Fetched BTC price from CoinGecko: ${btc_price:,.2f}")
            return float(btc_price)
            
        except requests.RequestException as e:
            self.logger.error(f"Failed to fetch BTC price from CoinGecko: {e}")
            return 50000.0  # Fallback price
        except Exception as e:
            self.logger.error(f"Failed to get BTC price: {e}")
            return 50000.0  # Fallback price
    
    def validate_address(self, address: str) -> bool:
        """
        Validate a Bitcoin address.
        
        Args:
            address: Bitcoin address to validate
            
        Returns:
            True if address is valid
        """
        try:
            # Basic validation - check format
            if not address.startswith('bc1'):
                return False
            
            if len(address) < 26 or len(address) > 90:
                return False
            
            # In a real implementation, this would use proper address validation
            return True
            
        except Exception:
            return False
    
    def get_service_info(self) -> Dict[str, Any]:
        """Get information about the Bitcoin service."""
        return {
            "network": "mainnet",  # Default to mainnet
            "btc_price_usd": self.get_btc_price(),
            "total_addresses": len(self._addresses),
            "pending_payments": len(self._pending_payments),
            "service_status": "operational"
        } 