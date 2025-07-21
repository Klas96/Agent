"""
Content creator node for PocketFlow.

This node determines content subtypes and parameters for generation.
"""

from typing import Dict, Any, Optional

from ...core.node import SimpleNode
from ...core.types import SharedState
from ...services import llm_service
from ...utils.logging import get_logger


class ContentCreatorNode(SimpleNode):
    """Node for determining content subtypes and parameters."""
    
    def __init__(self, name: str = "content_creator"):
        super().__init__(name)
        self.logger = get_logger("ContentCreatorNode")
    
    def process(self, shared: SharedState) -> Dict[str, Any]:
        """
        Determine content subtype and parameters for generation.
        
        Args:
            shared: Shared state containing agent action
            
        Returns:
            Processing result with routing information
        """
        try:
            agent_action = shared.get("agent_action", {})
            params = agent_action.get("parameters", {})
            
            self.logger.info(f"Processing content creation with params: {params}")
            
            content_type = params.get("type")
            prompt = params.get("prompt") or params.get("raw_prompt")
            duration = params.get("duration")
            
            if not content_type or not prompt:
                self.logger.warning("Missing content type or prompt")
                return {"route": "default", "error": "Missing content type or prompt"}
            
            # Determine subtype based on content type and prompt
            subtype = self._determine_subtype(content_type, prompt)
            
            # Set default duration if not specified
            if duration is None:
                duration = self._determine_duration(prompt)
            
            # Store results in shared state
            shared["chosen_subtype"] = subtype
            shared["chosen_duration"] = duration
            
            self.logger.info(f"Determined subtype: {subtype}, duration: {duration}")
            
            return {"route": "default"}
            
        except Exception as e:
            self.logger.error(f"Error in ContentCreatorNode: {e}")
            return {"route": "default", "error": str(e)}
    
    def _determine_subtype(self, content_type: str, prompt: str) -> str:
        """
        Determine content subtype based on type and prompt.
        
        Args:
            content_type: Type of content to generate
            prompt: User's generation prompt
            
        Returns:
            Determined subtype
        """
        prompt_lower = prompt.lower()
        
        # Keyword-based subtype determination
        if content_type == "sound":
            if "song" in prompt_lower or "music" in prompt_lower:
                return "music"
            elif "podcast" in prompt_lower:
                return "podcast"
            else:
                return "sound"
        
        elif content_type == "image":
            if "photo" in prompt_lower or "photograph" in prompt_lower:
                return "photo"
            elif "drawing" in prompt_lower or "sketch" in prompt_lower:
                return "drawing"
            else:
                return "image"
        
        elif content_type == "document":
            if "summary" in prompt_lower or "report" in prompt_lower:
                return "summary"
            elif "essay" in prompt_lower or "article" in prompt_lower:
                return "essay"
            else:
                return "document"
        
        return "generic"
    
    def _determine_duration(self, prompt: str) -> int:
        """
        Determine duration based on prompt keywords.
        
        Args:
            prompt: User's generation prompt
            
        Returns:
            Duration in seconds
        """
        prompt_lower = prompt.lower()
        
        if "2-minute" in prompt_lower or "two minute" in prompt_lower:
            return 120
        elif "3-minute" in prompt_lower or "three minute" in prompt_lower:
            return 180
        elif "short" in prompt_lower:
            return 60
        elif "long" in prompt_lower:
            return 180
        else:
            return 120  # default 