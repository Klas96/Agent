"""
Web search service for PocketFlow.

This module provides web search functionality for investigation and research.
"""

import requests
from typing import List, Dict, Any, Optional
import json
import time

from ..core.types import InvestigationRequest
from ..config.settings import get_settings
from ..utils.errors import WebSearchError
from ..utils.logging import get_logger


class WebSearchService:
    """Service for handling web search operations."""
    
    def __init__(self):
        self.settings = get_settings()
        self.logger = get_logger("WebSearchService")
        self._search_cache: Dict[str, Dict[str, Any]] = {}
    
    def search(self, request: InvestigationRequest) -> List[Dict[str, Any]]:
        """
        Perform web search for investigation.
        
        Args:
            request: InvestigationRequest with search parameters
            
        Returns:
            List of search results
            
        Raises:
            WebSearchError: If search fails
        """
        try:
            self.logger.info(f"Performing web search: {request.query}")
            
            # Check cache first
            cache_key = f"{request.query}_{request.max_results}"
            if cache_key in self._search_cache:
                cached_result = self._search_cache[cache_key]
                if time.time() - cached_result["timestamp"] < 3600:  # 1 hour cache
                    self.logger.info("Returning cached search results")
                    return cached_result["results"]
            
            # Perform search
            results = self._perform_search(request.query, request.max_results)
            
            # Cache results
            self._search_cache[cache_key] = {
                "results": results,
                "timestamp": time.time()
            }
            
            self.logger.info(f"Found {len(results)} search results")
            return results
            
        except Exception as e:
            self.logger.error(f"Web search failed: {e}")
            raise WebSearchError(f"Web search failed: {e}")
    
    def _perform_search(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """
        Perform the actual web search.
        
        Args:
            query: Search query
            max_results: Maximum number of results to return
            
        Returns:
            List of search results
        """
        try:
            # In a real implementation, this would use a search API
            # For now, simulate search results
            results = []
            
            # Simulate different types of search results
            result_templates = [
                {
                    "title": f"Search result for: {query}",
                    "url": f"https://example.com/search?q={query}",
                    "snippet": f"This is a search result about {query}. It contains relevant information that might be useful for your investigation.",
                    "source": "example.com"
                },
                {
                    "title": f"Information about {query}",
                    "url": f"https://info.com/{query.replace(' ', '-')}",
                    "snippet": f"Here you can find detailed information about {query}. This source provides comprehensive coverage of the topic.",
                    "source": "info.com"
                },
                {
                    "title": f"Latest news on {query}",
                    "url": f"https://news.com/topic/{query.replace(' ', '-')}",
                    "snippet": f"Recent developments and news articles related to {query}. Stay updated with the latest information.",
                    "source": "news.com"
                }
            ]
            
            # Generate results based on templates
            for i in range(min(max_results, len(result_templates))):
                template = result_templates[i]
                result = {
                    "title": template["title"],
                    "url": template["url"],
                    "snippet": template["snippet"],
                    "source": template["source"],
                    "rank": i + 1
                }
                results.append(result)
            
            return results
            
        except Exception as e:
            self.logger.error(f"Search execution failed: {e}")
            return []
    
    def search_with_filters(self, query: str, filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Perform search with additional filters.
        
        Args:
            query: Search query
            filters: Search filters (date range, source type, etc.)
            
        Returns:
            List of filtered search results
        """
        try:
            self.logger.info(f"Performing filtered search: {query} with filters: {filters}")
            
            # Get base results
            base_results = self._perform_search(query, 20)  # Get more results for filtering
            
            # Apply filters
            filtered_results = self._apply_filters(base_results, filters)
            
            return filtered_results
            
        except Exception as e:
            self.logger.error(f"Filtered search failed: {e}")
            return []
    
    def _apply_filters(self, results: List[Dict[str, Any]], filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Apply filters to search results.
        
        Args:
            results: List of search results
            filters: Filters to apply
            
        Returns:
            Filtered results
        """
        filtered_results = results
        
        # Apply source filter
        if "source" in filters:
            source_filter = filters["source"].lower()
            filtered_results = [
                r for r in filtered_results 
                if source_filter in r.get("source", "").lower()
            ]
        
        # Apply date filter (simplified)
        if "date_range" in filters:
            # In a real implementation, this would filter by actual dates
            # For now, just limit results
            filtered_results = filtered_results[:5]
        
        # Apply relevance filter
        if "min_relevance" in filters:
            # In a real implementation, this would use relevance scores
            # For now, just take top results
            filtered_results = filtered_results[:filters["min_relevance"]]
        
        return filtered_results
    
    def get_search_suggestions(self, query: str) -> List[str]:
        """
        Get search suggestions for a query.
        
        Args:
            query: Partial search query
            
        Returns:
            List of search suggestions
        """
        try:
            # In a real implementation, this would use a suggestions API
            # For now, return simple suggestions
            suggestions = [
                f"{query} information",
                f"{query} news",
                f"{query} guide",
                f"{query} tutorial",
                f"{query} examples"
            ]
            
            return suggestions[:5]  # Limit to 5 suggestions
            
        except Exception as e:
            self.logger.error(f"Failed to get search suggestions: {e}")
            return []
    
    def summarize_results(self, results: List[Dict[str, Any]]) -> str:
        """
        Summarize search results.
        
        Args:
            results: List of search results
            
        Returns:
            Summary of the results
        """
        try:
            if not results:
                return "No search results found."
            
            summary_parts = []
            summary_parts.append(f"Found {len(results)} search results:")
            
            for i, result in enumerate(results[:3], 1):  # Summarize top 3
                summary_parts.append(f"{i}. {result['title']} - {result['snippet'][:100]}...")
            
            if len(results) > 3:
                summary_parts.append(f"... and {len(results) - 3} more results.")
            
            return "\n".join(summary_parts)
            
        except Exception as e:
            self.logger.error(f"Failed to summarize results: {e}")
            return "Error summarizing search results."
    
    def get_service_info(self) -> Dict[str, Any]:
        """Get information about the web search service."""
        return {
            "cache_size": len(self._search_cache),
            "service_status": "operational",
            "supported_filters": ["source", "date_range", "min_relevance"]
        }
    
    def clear_cache(self):
        """Clear the search cache."""
        self._search_cache.clear()
        self.logger.info("Search cache cleared") 