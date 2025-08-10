"""
Electrum utilities for Bitcoin wallet integration.
"""

import requests
import subprocess
import time
import os
from typing import Dict, Any, Optional, List
from src.pocketflow.config.settings import get_settings
from src.pocketflow.utils.errors import BitcoinError
from src.pocketflow.utils.logging import get_logger

# Set up simple logging
# logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s') # This line is removed as per the new_code
logger = get_logger("electrum_utils")

def get_electrum_rpc_config() -> Dict[str, Any]:
    """Get Electrum RPC configuration from centralized settings."""
    settings = get_settings()
    return {
        "host": settings.ELECTRUM_HOST,
        "port": settings.ELECTRUM_PORT,
        "username": settings.ELECTRUM_USERNAME or "myuser",
        "password": settings.ELECTRUM_PASSWORD or "mypass",
        "rpc_port": settings.ELECTRUM_PORT,  # Use the same port for RPC
        "rpc_user": settings.ELECTRUM_USERNAME or "myuser",
        "rpc_password": settings.ELECTRUM_PASSWORD or "mypass"
    }

def call_electrum_rpc(method: str, params: list = None) -> Optional[Dict[str, Any]]:
    """
    Make an RPC call to Electrum daemon.
    
    Args:
        method: RPC method name
        params: Method parameters
        
    Returns:
        Response data or None if failed
    """
    config = get_electrum_rpc_config()
    url = f"http://{config['host']}:{config['rpc_port']}/"
    
    headers = {
        "Content-Type": "application/json",
    }
    
    data = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": method,
        "params": params or []
    }
    
    try:
        response = requests.post(
            url,
            headers=headers,
            json=data,
            auth=(config["rpc_user"], config["rpc_password"]),
            timeout=10
        )
        response.raise_for_status()
        result = response.json()
        
        if "error" in result and result["error"] is not None:
            logger.error(f"Electrum RPC error: {result['error']}")
            raise BitcoinError(f"Electrum RPC error: {result['error']}")
            
        return result.get("result")
        
    except Exception as e:
        logger.error(f"Failed to call Electrum RPC {method}: {e}")
        raise BitcoinError(f"Failed to call Electrum RPC {method}: {e}")

def get_new_btc_address() -> Optional[str]:
    """
    Get a new Bitcoin address from Electrum wallet.
    
    Returns:
        New Bitcoin address or None if failed
    """
    logger.info("Getting new BTC address from Electrum wallet")
    
    try:
        # Use offline mode to generate address directly
        
        # Get the wallet path - use user_wallet instead of default_wallet
        wallet_path = "/home/pocketflow/.electrum/wallets/user_wallet"
        
        # Run electrum command to create new address
        result = subprocess.run([
            "/opt/pocketflow/venv/bin/electrum",
            "-D", "/opt/pocketflow/.electrum",
            "--wallet", wallet_path,
            "createnewaddress",
            "--offline"
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            address = result.stdout.strip()
            logger.info(f"Generated new BTC address: {address}")
            return address
        else:
            logger.error(f"Failed to generate BTC address: {result.stderr}")
            raise BitcoinError(f"Failed to generate BTC address: {result.stderr}")
            
    except Exception as e:
        logger.error(f"Failed to generate BTC address: {e}")
        raise BitcoinError(f"Failed to generate BTC address: {e}")

def get_btc_balance() -> Optional[float]:
    """
    Get current Bitcoin balance from Electrum wallet.
    
    Returns:
        Balance in BTC or None if failed
    """
    logger.info("Getting BTC balance from Electrum wallet")
    
    result = call_electrum_rpc("getbalance")
    if result:
        # Convert from satoshis to BTC
        balance_btc = result / 100000000.0
        logger.info(f"Current BTC balance: {balance_btc}")
        return balance_btc
    else:
        logger.error("Failed to get BTC balance")
        raise BitcoinError("Failed to get BTC balance")

def get_btc_usd_price() -> Optional[float]:
    """
    Get current BTC/USD price from BitcoinService or fallback to API.
    
    Returns:
        BTC price in USD or None if failed
    """
    logger.info("Getting BTC/USD price")
    
    try:
        # Use direct API call
        
        # Fallback to direct API call
        response = requests.get(
            "https://api.coingecko.com/api/v3/simple/price",
            params={
                "ids": "bitcoin",
                "vs_currencies": "usd"
            },
            timeout=10
        )
        response.raise_for_status()
        data = response.json()
        
        price = data.get("bitcoin", {}).get("usd")
        if price:
            logger.info(f"Current BTC price from API: ${price}")
            return float(price)
        else:
            logger.error("Failed to parse BTC price from API response")
            raise BitcoinError("Failed to parse BTC price from API response")
            
    except Exception as e:
        logger.error(f"Failed to get BTC/USD price: {e}")
        raise BitcoinError(f"Failed to get BTC/USD price: {e}")

def check_address_in_wallet(address: str) -> bool:
    """
    Check if a Bitcoin address exists in the wallet.
    
    Args:
        address: Bitcoin address to check
        
    Returns:
        True if address exists in wallet, False otherwise
    """
    logger.info(f"Checking if address {address} exists in wallet")
    
    try:
        # Get all wallet addresses
        addresses = get_wallet_addresses()
        if addresses:
            exists = address in addresses
            logger.info(f"Address {address} exists in wallet: {exists}")
            return exists
        else:
            logger.error("Failed to get wallet addresses")
            return False
            
    except Exception as e:
        logger.error(f"Failed to check address in wallet: {e}")
        return False

def get_wallet_addresses() -> Optional[list]:
    """
    Get all addresses in the Electrum wallet.
    
    Returns:
        List of addresses or None if failed
    """
    logger.info("Getting all wallet addresses")
    
    try:
        # Use electrum command to list addresses
        import subprocess
        import json
        
        # Use the default Electrum data directory in home
        wallet_path = "/home/pocketflow/.electrum/wallets/user_wallet"
        
        result = subprocess.run([
            "/opt/pocketflow/venv/bin/electrum",
            "-D", "/opt/pocketflow/.electrum",
            "--wallet", wallet_path,
            "listaddresses",
            "--offline"
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            # Parse the JSON output
            addresses = json.loads(result.stdout.strip())
            logger.info(f"Found {len(addresses)} addresses in wallet")
            return addresses
        else:
            logger.error(f"Electrum command failed: {result.stderr}")
            raise Exception(f"Failed to get wallet addresses: {result.stderr}")
            
    except Exception as e:
        logger.error(f"Failed to get wallet addresses: {e}")
        raise Exception(f"Failed to get wallet addresses: {e}")

def is_electrum_running() -> bool:
    """
    Check if Electrum daemon is running.
    
    Returns:
        True if running, False otherwise
    """
    logger.info("Checking if Electrum daemon is running")
    
    try:
        # Try to connect to Electrum daemon
        result = call_electrum_rpc("getinfo")
        if result:
            logger.info("Electrum daemon is running")
            return True
        else:
            logger.warning("Electrum daemon is not responding")
            return False
            
    except Exception as e:
        logger.error(f"Failed to check Electrum daemon status: {e}")
        return False
