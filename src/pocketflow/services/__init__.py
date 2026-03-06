"""
Services package for PocketFlow.

This package contains all external service integrations.
"""

from .conversation_service import ConversationService
from .email_service import EmailService
from .llm_service import LLMService
from .database_service import DatabaseService
from .mcp_client import MCPClient, LibriscribeMCPClient, PodcastfyMCPClient, MPCManager, get_mpc_manager

# Services moved to MPC processes:
# - ContentService -> Content-MPC
# - DocumentService -> Content-MPC
# - WebSearchService -> Research-MPC
# - VectorService -> Research-MPC (if used for RAG)

__all__ = [
    "LLMService",
    "EmailService",
    "DatabaseService",
    "ConversationService",
    "MCPClient",
    "LibriscribeMCPClient",
    "PodcastfyMCPClient",
    "MPCManager",
    "get_mpc_manager",
] 