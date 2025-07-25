import logging
from src.pocketflow.utils.logging import get_logger

logger = get_logger("websearch_utils")

def web_search(query: str) -> str:
    """Stub: Perform web search."""
    logger.info(f"Web search for: {query}")
    return f"Web search results for: {query}"
