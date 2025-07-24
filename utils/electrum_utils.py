"""
Electrum utilities for Bitcoin wallet integration.
"""

import os
import requests
import json
import logging
from typing import Optional, Dict, Any

# Set up simple logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("ElectrumUtils")

def get_electrum_rpc_config() -> Dict[str, Any]:
    """Get Electrum RPC configuration from environment variables."""
    return {
        "host": os.environ.get("ELECTRUM_HOST", "localhost"),
        "port": int(os.environ.get("ELECTRUM_PORT", "7777")),  # Fixed default port
        "username": os.environ.get("ELECTRUM_USERNAME", "myuser"),
        "password": os.environ.get("ELECTRUM_PASSWORD", "mypass"),
        "rpc_port": int(os.environ.get("ELECTRUM_RPCPORT", "7777")),
        "rpc_user": os.environ.get("ELECTRUM_RPCUSER", "myuser"),
        "rpc_password": os.environ.get("ELECTRUM_RPCPASSWORD", "mypass")
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
            return None
            
        return result.get("result")
        
    except Exception as e:
        logger.error(f"Failed to call Electrum RPC {method}: {e}")
        return None

def get_new_btc_address() -> Optional[str]:
    """
    Get a new Bitcoin address from Electrum wallet.
    
    Returns:
        New Bitcoin address or None if failed
    """
    logger.info("Getting new BTC address from Electrum wallet")
    
    try:
        # Use offline mode to generate address directly
        import subprocess
        import os
        
        # Get the wallet path - use user_wallet instead of default_wallet
        wallet_path = "/home/pocketflow/.electrum/wallets/user_wallet"
        
        # Run electrum command to create new address
        result = subprocess.run([
            "/opt/pocketflow/venv/bin/electrum",
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
            return None
            
    except Exception as e:
        logger.error(f"Failed to generate BTC address: {e}")
        return None

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
        return None

def get_btc_usd_price() -> Optional[float]:
    """
    Get current BTC/USD price from a public API.
    
    Returns:
        BTC price in USD or None if failed
    """
    logger.info("Getting BTC/USD price")
    
    try:
        # Use CoinGecko API (free, no API key required)
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
            logger.info(f"Current BTC price: ${price}")
            return float(price)
        else:
            logger.error("Failed to parse BTC price from API response")
            return None
            
    except Exception as e:
        logger.error(f"Failed to get BTC/USD price: {e}")
        return None

def check_address_in_wallet(address: str) -> bool:
    """
    Check if a Bitcoin address belongs to the wallet.
    
    Args:
        address: Bitcoin address to check
        
    Returns:
        True if address is in wallet, False otherwise
    """
    logger.info(f"Checking if address {address} is in wallet")
    
    result = call_electrum_rpc("is_mine", [address])
    if result is not None:
        is_mine = bool(result)
        logger.info(f"Address {address} {'IS' if is_mine else 'is NOT'} in wallet")
        return is_mine
    else:
        logger.error(f"Failed to check address {address}")
        return False

def get_wallet_addresses() -> Optional[list]:
    """
    Get all addresses in the wallet.
    
    Returns:
        List of addresses or None if failed
    """
    logger.info("Getting all wallet addresses")
    
    result = call_electrum_rpc("listaddresses")
    if result:
        addresses = result
        logger.info(f"Found {len(addresses)} addresses in wallet")
        return addresses
    else:
        logger.error("Failed to get wallet addresses")
        return None

def is_electrum_running() -> bool:
    """
    Check if Electrum daemon is running and accessible.
    
    Returns:
        True if Electrum is running, False otherwise
    """
    try:
        result = call_electrum_rpc("version")
        if result:
            logger.info(f"Electrum daemon is running, version: {result}")
            return True
        else:
            logger.warning("Electrum daemon is not responding")
            return False
    except Exception as e:
        logger.error(f"Failed to check Electrum status: {e}")
        return False
