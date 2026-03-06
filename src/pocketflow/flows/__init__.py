"""
Flows package for PocketFlow.

This package contains production-ready flow definitions.
"""

from .email_processor import EmailProcessorFlow
from .tokenless_user import TokenlessUserFlow
# ContentGenerationFlow and InvestigationFlow removed - use email_processor with MPC nodes
# from .content_generation import ContentGenerationFlow
# from .investigation import InvestigationFlow

__all__ = [
    "EmailProcessorFlow",
    "TokenlessUserFlow",
    # "ContentGenerationFlow",  # Removed - use email_processor with MPC
    # "InvestigationFlow",  # Removed - use email_processor with MPC
] 