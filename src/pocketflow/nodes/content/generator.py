"""
Content generator node for PocketFlow.

This node handles content generation using the content service.
"""

from typing import Dict, Any, Optional

from ...core.node import SimpleNode
from ...core.types import SharedState
from ...services.content_service import ContentService
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
            content_request = getattr(shared, 'content_request', None)
            if not content_request:
                self.logger.warning("No content request found")
                return {"route": "generation_failed", "error": "No content request"}
            
            self.logger.info(f"Generating content: {content_request.content_type} - {content_request.prompt}")
            
            # Check if this is a podcast request
            is_podcast_request = self._is_podcast_request(content_request, shared)
            
            if is_podcast_request:
                # Use podcastify tool for podcast generation
                file_path = self._generate_podcast_with_tool(content_request, shared)
            else:
                # Use regular content service for other content types
                service = ContentService()
                file_path = service.generate_content(content_request)
            
            if file_path:
                self.logger.info(f"Content generated successfully: {file_path}")
                
                # Store generated file path in shared state
                setattr(shared, 'attachment', file_path)
                setattr(shared, 'generated_file_path', file_path)
                
                # Set reply body based on content type
                if is_podcast_request:
                    setattr(shared, 'reply_body', "Here is your requested podcast!")
                else:
                    raw_ct = getattr(content_request, 'content_type', None)
                    ct_str = (raw_ct.value if hasattr(raw_ct, 'value') else str(raw_ct)).lower()
                    setattr(shared, 'reply_body', f"Here is your requested {ct_str}!")
                
                return {"route": "default"}
            else:
                self.logger.error("Content generation failed")
                setattr(shared, 'generation_error', 
                    "Sorry, your content could not be generated. Please check your request or try again later."
                )
                return {"route": "generation_failed", "error": "Content generation failed"}
                
        except ContentGenerationError as e:
            self.logger.error(f"Content generation error: {e}")
            setattr(shared, 'generation_error', str(e))
            return {"route": "generation_failed", "error": str(e)}
        except Exception as e:
            self.logger.error(f"Unexpected error in GenerateContentNode: {e}")
            setattr(shared, 'generation_error', str(e))
            return {"route": "generation_failed", "error": str(e)}
    
    def _is_podcast_request(self, content_request, shared: SharedState) -> bool:
        """
        Check if this is a podcast generation request.
        
        Args:
            content_request: The content generation request
            shared: Shared state
            
        Returns:
            True if this is a podcast request
        """
        # Check if the prompt contains podcast-related keywords
        prompt = content_request.prompt.lower()
        podcast_keywords = ['podcast', 'episode', 'audio show', 'radio show']
        
        if any(keyword in prompt for keyword in podcast_keywords):
            return True
        
        # Check if the chosen subtype indicates podcast
        chosen_subtype = getattr(shared, 'chosen_subtype', None)
        if chosen_subtype and 'podcast' in chosen_subtype.lower():
            return True
        
        # Check if the content type is sound and the prompt is podcast-like
        raw_ct = getattr(content_request, 'content_type', None)
        ct_str = (raw_ct.value if hasattr(raw_ct, 'value') else str(raw_ct)).lower()
        
        if ct_str == "sound" and any(keyword in prompt for keyword in podcast_keywords):
            return True
        
        return False
    
    def _generate_podcast_with_tool(self, content_request, shared: SharedState) -> Optional[str]:
        """
        Generate podcast using the podcastify tool.
        
        Args:
            content_request: The content generation request
            shared: Shared state
            
        Returns:
            Path to the generated audio file, or None if failed
        """
        try:
            from ...tools.registry import agent_tool_registry
            
            # Get the podcastify tool
            podcastify_tool = agent_tool_registry.get_tool("podcastify")
            if not podcastify_tool:
                self.logger.warning("Podcastify tool not found, falling back to content service")
                service = ContentService()
                return service.generate_content(content_request)
            
            # Extract topic from the prompt
            prompt = content_request.prompt
            duration = getattr(content_request, 'duration', 120)  # Default 2 minutes
            
            # Prepare parameters for podcastify tool
            tool_params = {
                "topic": prompt,
                "duration_minutes": max(1, duration // 60),  # Convert seconds to minutes
                "style": "conversational",
                "target_audience": "general",
                "voice_preference": "professional",
                "output_format": "wav"
            }
            
            self.logger.info(f"Using podcastify tool with parameters: {tool_params}")
            
            # Execute the podcastify tool
            result = podcastify_tool.execute(**tool_params)
            
            if result and hasattr(result, 'file_path'):
                return result.file_path
            elif result and isinstance(result, dict) and 'file_path' in result:
                return result['file_path']
            else:
                self.logger.warning("Podcastify tool returned unexpected result, falling back to content service")
                service = ContentService()
                return service.generate_content(content_request)
                
        except Exception as e:
            self.logger.error(f"Error using podcastify tool: {e}")
            self.logger.info("Falling back to content service")
            service = ContentService()
            return service.generate_content(content_request) 