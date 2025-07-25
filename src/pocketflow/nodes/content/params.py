"""
Content parameters node for PocketFlow.

This node prepares parameters for content generation.
"""

from typing import Dict, Any, Optional

from ...core.node import SimpleNode
from ...core.types import SharedState, ContentGenerationRequest
from ...utils.logging import get_logger


class ContentParamNode(SimpleNode):
    """Node for preparing content generation parameters."""
    
    def __init__(self, name: str = "content_params"):
        super().__init__(name)
        self.logger = get_logger("ContentParamNode")
    
    def process(self, shared: SharedState) -> Dict[str, Any]:
        """
        Prepare parameters for content generation.
        
        Args:
            shared: Shared state containing agent action and chosen parameters
            
        Returns:
            Processing result with routing information
        """
        try:
            agent_action = shared.agent_action or {}
            params = agent_action.get("parameters", {})
            
            # Get chosen subtype and duration from previous node
            subtype = params.get("subtype") or getattr(shared, 'chosen_subtype', None)
            duration = params.get("duration") or getattr(shared, 'chosen_duration', None)
            
            self.logger.info(f"Preparing content params: type={params.get('type')}, subtype={subtype}, duration={duration}")
            
            # Create content generation request
            content_request = ContentGenerationRequest(
                content_type=params.get("type"),
                prompt=params.get("prompt") or params.get("raw_prompt"),
                duration=duration,
                language=params.get("language", "en"),
                longform=params.get("longform", False),
                urls=params.get("urls")
            )
            
            # Store request in shared state for next node
            shared.content_request = content_request
            
            self.logger.info(f"Content request prepared: {content_request}")
            
            return {"route": "default"}
            
        except Exception as e:
            self.logger.error(f"Error in ContentParamNode: {e}")
            return {"route": "default", "error": str(e)} 