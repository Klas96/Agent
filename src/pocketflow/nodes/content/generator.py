"""
Content generator node for PocketFlow.

This node handles content generation using the content service.
"""

from typing import Dict, Any, Optional

from ...core.node import SimpleNode
from ...core.types import SharedState
from ...services import content_service
from ...utils.logging import get_logger
from ...utils.errors import ContentGenerationError


class GenerateContentNode(SimpleNode):
    """Node for generating content using the content service."""
    
    def __init__(self, name: str = "generate_content"):
        super().__init__(name)
        self.logger = get_logger("GenerateContentNode")
    
    def process(self, shared: SharedState) -> Dict[str, Any]:
        """
        Generate content based on the content request.
        
        Args:
            shared: Shared state containing content request
            
        Returns:
            Processing result with routing information
        """
        try:
            content_request = shared.get("content_request")
            if not content_request:
                self.logger.warning("No content request found")
                return {"route": "generation_failed", "error": "No content request"}
            
            self.logger.info(f"Generating content: {content_request.content_type} - {content_request.prompt}")
            
            # Generate content using content service
            file_path = content_service.generate_content(content_request)
            
            if file_path:
                self.logger.info(f"Content generated successfully: {file_path}")
                
                # Store generated file path in shared state
                shared["attachment"] = file_path
                shared["generated_file_path"] = file_path
                
                # Set reply body based on content type
                content_type = content_request.content_type
                if content_type == "sound":
                    if "podcast" in shared.get("chosen_subtype", "").lower():
                        shared["reply_body"] = "Here is your requested podcast!"
                    else:
                        shared["reply_body"] = "Here is your requested song!"
                else:
                    shared["reply_body"] = f"Here is your requested {content_type}!"
                
                return {"route": "default"}
            else:
                self.logger.error("Content generation failed")
                shared["generation_error"] = (
                    "Sorry, your content could not be generated. Please check your request or try again later."
                )
                return {"route": "generation_failed", "error": "Content generation failed"}
                
        except ContentGenerationError as e:
            self.logger.error(f"Content generation error: {e}")
            shared["generation_error"] = str(e)
            return {"route": "generation_failed", "error": str(e)}
        except Exception as e:
            self.logger.error(f"Unexpected error in GenerateContentNode: {e}")
            shared["generation_error"] = str(e)
            return {"route": "generation_failed", "error": str(e)} 