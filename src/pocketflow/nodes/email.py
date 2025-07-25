"""
Email nodes for PocketFlow.

This module provides email-related nodes for the PocketFlow system.
Note: Individual email nodes are now in the email/ subdirectory.
"""

from typing import Dict, Any, Optional
from .core.node import SimpleNode
from .core.types import SharedState, EmailSendRequest
from .utils.logging import get_logger
from .services import email_service
from utils.email_utils import extract_email

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