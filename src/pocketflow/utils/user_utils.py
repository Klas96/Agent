"""
User utility functions for PocketFlow.

This module contains utility functions for user management and validation.
"""

from typing import Optional, Dict, Any
from .logging import get_logger

logger = get_logger("user_utils")

def is_registered_user(email_address: str) -> bool:
    """Check if an email address belongs to a registered user."""
    try:
        from ..services.database_service import DatabaseService
        db_service = DatabaseService()
        user = db_service.get_user(email_address)
        return user is not None
    except Exception as e:
        logger.warning(f"Could not check if {email_address} is a registered user: {e}")
        return False

def get_user_info(email_address: str) -> Optional[Dict[str, Any]]:
    """Get user information by email address."""
    try:
        from ..services.database_service import DatabaseService
        db_service = DatabaseService()
        user = db_service.get_user(email_address)
        if user:
            return {
                'email': user.email,
                'name': user.name,
                'personality': user.personality,
                'tokens': user.tokens,
                'created_at': user.created_at,
                'updated_at': user.updated_at
            }
        return None
    except Exception as e:
        logger.warning(f"Could not get user info for {email_address}: {e}")
        return None 