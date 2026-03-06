"""
MPC wrapper node for content generation.

This node calls the Content-MPC process to generate content instead of using local services.
"""

from typing import Dict, Any, Optional
from ...core.node import Node
from ...core.types import SharedState, ContentGenerationRequest
from ...services.mcp_client import get_mpc_manager
from ...utils.logging import get_logger

logger = get_logger("MPCContentGeneratorNode")


class MPCContentGeneratorNode(Node):
    """Node that generates content via Content-MPC process."""
    
    def prep(self, shared: SharedState):
        """Prepare by creating content generation request from agent action or shared state."""
        # First check if content_request already exists
        content_request = getattr(shared, 'content_request', None)
        
        if content_request:
            # Ensure it's a ContentGenerationRequest
            if isinstance(content_request, dict):
                from ...core.types import ContentType
                content_type = ContentType(content_request.get("content_type"))
                content_request = ContentGenerationRequest(
                    content_type=content_type,
                    prompt=content_request.get("prompt", ""),
                    duration=content_request.get("duration")
                )
            return content_request
        
        # If no content_request, create from agent action
        agent_action = getattr(shared, 'agent_action', None)
        if not agent_action or agent_action.get("action") != "generate":
            logger.error("No content_request or generate action found")
            return None
        
        params = agent_action.get("parameters", {})
        content_type_str = params.get("type")
        prompt = params.get("prompt") or params.get("raw_prompt", "")
        duration = params.get("duration")
        
        if not content_type_str or not prompt:
            logger.error("Missing content type or prompt in agent action")
            return None
        
        # Convert content type string to ContentType enum
        from ...core.types import ContentType
        try:
            content_type = ContentType(content_type_str.lower())
        except ValueError:
            logger.error(f"Invalid content type: {content_type_str}")
            return None
        
        # Create ContentGenerationRequest
        content_request = ContentGenerationRequest(
            content_type=content_type,
            prompt=prompt,
            duration=duration
        )
        
        # Store in shared state for future reference
        shared.content_request = content_request
        
        return content_request
    
    def exec(self, prep_res):
        """Execute content generation via Content-MPC."""
        if not prep_res:
            return None
        
        try:
            mpc_manager = get_mpc_manager()
            file_path = mpc_manager.generate_content(prep_res)
            
            if file_path:
                logger.info(f"Content generated successfully via MPC: {file_path}")
                return file_path
            else:
                logger.error("Content generation failed via MPC")
                return None
                
        except Exception as e:
            logger.error(f"Error generating content via MPC: {e}", exc_info=True)
            return None
    
    def post(self, shared: SharedState, prep_res, exec_res):
        """Post-process by storing generated file path."""
        if exec_res:
            shared.generated_file_path = exec_res
            logger.info(f"Stored generated file path: {exec_res}")
            return "default"
        else:
            shared.generation_error = "Content generation failed via MPC"
            logger.error("Content generation failed")
            return "error"
