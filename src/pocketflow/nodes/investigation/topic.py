"""
Investigate topic node for PocketFlow.

This node handles web search and investigation functionality.
"""

from typing import Dict, Any, Optional

from ...core.node import SimpleNode
from ...core.types import SharedState, InvestigationRequest
from ...services import websearch_service
from ...utils.logging import get_logger
from ...utils.errors import WebSearchError


class InvestigateTopicNode(SimpleNode):
    """Node for investigating topics using web search."""
    
    def __init__(self, name: str = "investigate_topic"):
        super().__init__(name)
        self.logger = get_logger("InvestigateTopicNode")
    
    def process(self, shared: SharedState) -> Dict[str, Any]:
        """
        Investigate a topic using web search.
        
        Args:
            shared: Shared state containing agent action
            
        Returns:
            Processing result with routing information
        """
        try:
            agent_action = shared.get("agent_action", {})
            params = agent_action.get("parameters", {})
            
            query = params.get("query")
            if not query:
                self.logger.warning("No query provided for investigation")
                return {"route": "default", "error": "No query provided"}
            
            self.logger.info(f"Investigating topic: {query}")
            
            # Create investigation request
            investigation_request = InvestigationRequest(
                query=query,
                max_results=params.get("max_results", 5)
            )
            
            # Perform web search
            results = websearch_service.search(investigation_request)
            
            if results:
                self.logger.info(f"Found {len(results)} search results")
                
                # Summarize results
                summary = websearch_service.summarize_results(results)
                
                # Store results in shared state
                shared["investigation_results"] = results
                shared["investigation_summary"] = summary
                shared["reply_body"] = f"Here's what I found about '{query}':\n\n{summary}"
                
                return {"route": "default"}
            else:
                self.logger.warning("No search results found")
                shared["reply_body"] = f"I couldn't find any information about '{query}'. Please try a different search term."
                return {"route": "default"}
                
        except WebSearchError as e:
            self.logger.error(f"Web search error: {e}")
            shared["reply_body"] = f"Sorry, I encountered an error while searching for '{query}': {str(e)}"
            return {"route": "default", "error": str(e)}
        except Exception as e:
            self.logger.error(f"Unexpected error in InvestigateTopicNode: {e}")
            shared["reply_body"] = f"Sorry, I encountered an error while searching for '{query}': {str(e)}"
            return {"route": "default", "error": str(e)} 