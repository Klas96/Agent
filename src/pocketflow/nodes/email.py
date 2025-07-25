"""
Email processing nodes for PocketFlow.

This module contains nodes for email processing operations.
"""

from typing import Dict, Any, Optional
from .core.node import SimpleNode
from .core.types import SharedState
from .utils.logging import get_logger
from .utils.errors import EmailError
from .services import email_service
from .utils.email_utils import extract_email

# Import the dedicated email nodes
from .email.fetch import FetchEmailNode
from .email.send import SendEmailNode
from .email.context import ConversationContextNode
from .email.postprocess import PostProcessNode

# Re-export the nodes for backward compatibility
__all__ = [
    'FetchEmailNode',
    'SendEmailNode', 
    'ConversationContextNode',
    'PostProcessNode'
] 