"""
Services package for PocketFlow.

This package contains all external service integrations.
"""

from .email_service import EmailService
from .llm_service import LLMService
from .content_service import ContentService
from .bitcoin_service import BitcoinService
from .websearch_service import WebSearchService
from .database_service import DatabaseService

# Create service instances
email_service = EmailService()
llm_service = LLMService()
content_service = ContentService()
bitcoin_service = BitcoinService()
websearch_service = WebSearchService()
database_service = DatabaseService()

__all__ = [
    "EmailService",
    "LLMService", 
    "ContentService",
    "BitcoinService",
    "WebSearchService",
    "DatabaseService",
    "email_service",
    "llm_service",
    "content_service",
    "bitcoin_service",
    "websearch_service",
    "database_service",
] 