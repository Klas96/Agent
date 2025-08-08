"""
Simplified Bitcoin utilities without Electrum dependency.

This module provides Bitcoin address generation and balance checking
using external APIs instead of Electrum wallet.
"""

import requests
import hashlib
import time
import json
from typing import Optional, Dict, Any, List
from ..utils.logging import get_logger
from ..utils.errors import BitcoinError


class SimpleBitcoinUtils:
    """Simplified Bitcoin utilities using external APIs."""
    
    def __init__(self):
        self.logger = get_logger("SimpleBitcoinUtils")
        self.api_endpoints = {
            "blockchain_info": "https://blockchain.info",
            "blockcypher": "https://api.blockcypher.com/v1/btc/main",
            "blockstream": "https://blockstream.info/api"
        }
        self.address_pool = []
        self.load_address_pool()
    
    def get_new_address(self, user_email: str) -> str:
        """
        Get a new Bitcoin address for user.
        
        Args:
            user_email: User's email address
            
        Returns:
            Bitcoin address string
            
        Raises:
            BitcoinError: If address generation fails
        """
        try:
            # Try deterministic generation first
            address = self._generate_deterministic_address(user_email)
            if address:
                self.logger.info(f"Generated deterministic address for {user_email}: {address}")
                return address
            
            # Fallback to external API
            address = self._generate_from_external_api(user_email)
            if address:
                self.logger.info(f"Generated API address for {user_email}: {address}")
                return address
            
            # Last resort: use address pool
            address = self._get_from_address_pool()
            if address:
                self.logger.info(f"Used pool address for {user_email}: {address}")
                return address
            
            raise BitcoinError("All address generation methods failed")
            
        except Exception as e:
            self.logger.error(f"Failed to generate address for {user_email}: {e}")
            raise BitcoinError(f"Address generation failed: {e}")
    
    def check_address_balance(self, address: str) -> float:
        """
        Check Bitcoin address balance using external API.
        
        Args:
            address: Bitcoin address to check
            
        Returns:
            Balance in BTC
        """
        try:
            # Try multiple APIs for reliability
            balance = self._get_balance_from_blockchain_info(address)
            if balance is not None:
                return balance
            
            balance = self._get_balance_from_blockcypher(address)
            if balance is not None:
                return balance
            
            balance = self._get_balance_from_blockstream(address)
            if balance is not None:
                return balance
            
            self.logger.warning(f"All balance APIs failed for {address}")
            return 0.0
            
        except Exception as e:
            self.logger.error(f"Failed to get balance for {address}: {e}")
            return 0.0
    
    def validate_address(self, address: str) -> bool:
        """
        Validate Bitcoin address format.
        
        Args:
            address: Bitcoin address to validate
            
        Returns:
            True if valid, False otherwise
        """
        try:
            # Basic validation: check length and format
            if not address or len(address) < 26 or len(address) > 35:
                return False
            
            # Check if it starts with common Bitcoin prefixes
            valid_prefixes = ['1', '3', 'bc1']
            if not any(address.startswith(prefix) for prefix in valid_prefixes):
                return False
            
            # Additional validation using API
            response = requests.get(f"{self.api_endpoints['blockchain_info']}/rawaddr/{address}")
            return response.status_code == 200
            
        except Exception as e:
            self.logger.error(f"Address validation failed for {address}: {e}")
            return False
    
    def _generate_deterministic_address(self, user_email: str) -> Optional[str]:
        """
        Generate deterministic address from user email.
        
        This creates a deterministic address based on the user's email,
        ensuring the same user always gets the same address.
        """
        try:
            # Create deterministic seed from email
            import hashlib
            seed = hashlib.sha256(user_email.encode()).hexdigest()
            
            # Generate a deterministic address using the seed
            # This is a simplified approach - in production you'd use a proper HD wallet
            # For now, we'll create a deterministic address using the seed
            address_chars = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"
            
            # Use the seed to generate a deterministic address
            address = "1"  # Start with legacy Bitcoin address prefix
            
            # Generate 25 more characters deterministically
            for i in range(25):
                # Use different parts of the seed for each character
                char_index = int(seed[i*2:i*2+2], 16) % len(address_chars)
                address += address_chars[char_index]
            
            # Validate the generated address
            if self.validate_address(address):
                self.logger.info(f"Generated deterministic address for {user_email}: {address}")
                return address
            else:
                self.logger.warning(f"Generated deterministic address failed validation for {user_email}")
                return None
            
        except Exception as e:
            self.logger.error(f"Deterministic address generation failed for {user_email}: {e}")
            return None
    
    def _generate_from_external_api(self, user_email: str) -> Optional[str]:
        """
        Generate address using external API.
        
        Args:
            user_email: User's email address to make generation unique
            
        Returns:
            Bitcoin address or None if failed
        """
        try:
            # Create a unique identifier for this user
            import hashlib
            user_hash = hashlib.md5(user_email.encode()).hexdigest()[:8]
            
            # Try BlockCypher API with POST request
            response = requests.post(f"{self.api_endpoints['blockcypher']}/addrs", timeout=10)
            if response.status_code == 201:
                data = response.json()
                address = data.get("address")
                if address:
                    self.logger.info(f"Generated BlockCypher address for {user_email}: {address}")
                    return address
            
            # Fallback to Blockchain.info API with user-specific parameters
            response = requests.get(
                f"{self.api_endpoints['blockchain_info']}/api/receive",
                params={"method": "create", "address": "random", "user": user_hash},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                address = data.get("input_address")
                if address:
                    self.logger.info(f"Generated Blockchain.info address for {user_email}: {address}")
                    return address
            
            return None
            
        except Exception as e:
            self.logger.error(f"External API address generation failed for {user_email}: {e}")
            return None
    
    def _get_from_address_pool(self) -> Optional[str]:
        """
        Get address from pre-generated pool.
        
        Returns:
            Bitcoin address or None if pool is empty
        """
        if self.address_pool:
            return self.address_pool.pop()
        return None
    
    def _get_balance_from_blockchain_info(self, address: str) -> Optional[float]:
        """Get balance using Blockchain.info API."""
        try:
            response = requests.get(
                f"{self.api_endpoints['blockchain_info']}/balance?active={address}",
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                balance_satoshi = data[address]["final_balance"]
                return balance_satoshi / 100000000  # Convert satoshis to BTC
            
            return None
            
        except Exception as e:
            self.logger.error(f"Blockchain.info balance check failed: {e}")
            return None
    
    def _get_balance_from_blockcypher(self, address: str) -> Optional[float]:
        """Get balance using BlockCypher API."""
        try:
            response = requests.get(
                f"{self.api_endpoints['blockcypher']}/addrs/{address}/balance",
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                balance_satoshi = data.get("final_balance", 0)
                return balance_satoshi / 100000000  # Convert satoshis to BTC
            
            return None
            
        except Exception as e:
            self.logger.error(f"BlockCypher balance check failed: {e}")
            return None
    
    def _get_balance_from_blockstream(self, address: str) -> Optional[float]:
        """Get balance using Blockstream API."""
        try:
            response = requests.get(
                f"{self.api_endpoints['blockstream']}/address/{address}",
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                balance_satoshi = data.get("chain_stats", {}).get("funded_txo_sum", 0)
                return balance_satoshi / 100000000  # Convert satoshis to BTC
            
            return None
            
        except Exception as e:
            self.logger.error(f"Blockstream balance check failed: {e}")
            return None
    
    def load_address_pool(self):
        """Load pre-generated addresses from file or database."""
        try:
            # For now, use a simple list of addresses
            # In production, you might load from a file or database
            self.address_pool = [
                # Add some pre-generated addresses here
                # These would be generated offline and stored securely
            ]
            
            self.logger.info(f"Loaded {len(self.address_pool)} addresses from pool")
            
        except Exception as e:
            self.logger.error(f"Failed to load address pool: {e}")
            self.address_pool = []
    
    def get_transaction_history(self, address: str) -> List[Dict[str, Any]]:
        """
        Get transaction history for an address.
        
        Args:
            address: Bitcoin address
            
        Returns:
            List of transaction dictionaries
        """
        try:
            response = requests.get(
                f"{self.api_endpoints['blockchain_info']}/rawaddr/{address}",
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get("txs", [])
            
            return []
            
        except Exception as e:
            self.logger.error(f"Failed to get transaction history for {address}: {e}")
            return []


# Global instance for easy access
simple_bitcoin_utils = SimpleBitcoinUtils()


# Convenience functions for backward compatibility
def get_new_btc_address(user_email: str = "system") -> Optional[str]:
    """Get a new Bitcoin address (replaces Electrum function)."""
    return simple_bitcoin_utils.get_new_address(user_email)

def get_wallet_addresses() -> List[str]:
    """Get all available addresses (replaces Electrum function)."""
    # For simplified system, return empty list
    # In production, you might return addresses from database
    return []

def check_address_in_wallet(address: str) -> bool:
    """Check if address is valid (replaces Electrum function)."""
    return simple_bitcoin_utils.validate_address(address)

def get_address_balance(address: str) -> float:
    """Get address balance (replaces Electrum function)."""
    return simple_bitcoin_utils.check_address_balance(address) 