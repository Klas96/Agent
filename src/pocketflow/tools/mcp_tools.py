"""
MCP Tool wrappers that implement the Tool interface but call external MCP servers.

These tools act as adapters between the internal tool system and external MCP servers.
"""

from typing import Dict, Any
from .base import Tool, ToolResult
from ..services.mcp_client import LibriscribeMCPClient, PodcastfyMCPClient, MCPClient
from ..utils.logging import get_logger


class MCPToolWrapper(Tool):
    """Base wrapper for MCP tools."""
    
    def __init__(self, name: str, description: str, mcp_client: MCPClient, tool_name: str):
        """
        Initialize MCP tool wrapper.
        
        Args:
            name: Tool name for the agent
            description: Tool description
            mcp_client: MCP client instance
            tool_name: Name of the tool on the MCP server
        """
        super().__init__(name, description)
        self.mcp_client = mcp_client
        self.mcp_tool_name = tool_name
    
    def execute(self, **kwargs) -> ToolResult:
        """Execute the tool via MCP server."""
        try:
            result = self.mcp_client.call_tool(self.mcp_tool_name, **kwargs)
            
            if result.get('success'):
                return ToolResult(
                    success=True,
                    data=result.get('data'),
                    metadata={"mcp_tool": self.mcp_tool_name, "source": "mcp"}
                )
            else:
                return ToolResult(
                    success=False,
                    error=result.get('error', 'Unknown MCP error'),
                    metadata={"mcp_tool": self.mcp_tool_name}
                )
        except Exception as e:
            self.logger.error(f"MCP tool execution failed: {e}")
            return ToolResult(
                success=False,
                error=str(e),
                metadata={"mcp_tool": self.mcp_tool_name}
            )


class LibriscribeDocumentTool(MCPToolWrapper):
    """Tool for generating documents via Libriscribe MCP Server."""
    
    def __init__(self):
        client = LibriscribeMCPClient()
        super().__init__(
            name="generate_document",
            description="Generate professional documents (reports, books, etc.) using Libriscribe",
            mcp_client=client,
            tool_name="format_book"
        )
    
    @property
    def parameters(self) -> Dict[str, Dict[str, Any]]:
        return {
            "prompt": {
                "type": str,
                "required": True,
                "description": "Document generation prompt or topic"
            },
            "document_type": {
                "type": str,
                "required": False,
                "description": "Type of document (report, book, etc.)"
            },
            "title": {
                "type": str,
                "required": False,
                "description": "Document title"
            }
        }
    
    def execute(self, **kwargs) -> ToolResult:
        """Generate document using Libriscribe."""
        try:
            prompt = kwargs.get('prompt', '')
            document_type = kwargs.get('document_type', 'report')
            
            # Use Libriscribe's generate_document method
            file_path = self.mcp_client.generate_document(prompt, document_type, **kwargs)
            
            if file_path:
                return ToolResult(
                    success=True,
                    data={"file_path": file_path, "document_type": document_type},
                    metadata={"mcp_tool": "libriscribe", "source": "mcp"}
                )
            else:
                return ToolResult(
                    success=False,
                    error="Document generation failed",
                    metadata={"mcp_tool": "libriscribe"}
                )
        except Exception as e:
            self.logger.error(f"Document generation failed: {e}")
            return ToolResult(
                success=False,
                error=str(e),
                metadata={"mcp_tool": "libriscribe"}
            )


class LibriscribeResearchTool(MCPToolWrapper):
    """Tool for researching topics via Libriscribe MCP Server."""
    
    def __init__(self):
        client = LibriscribeMCPClient()
        super().__init__(
            name="research_topic",
            description="Research a topic for accuracy or inspiration using Libriscribe",
            mcp_client=client,
            tool_name="research_topic"
        )
    
    @property
    def parameters(self) -> Dict[str, Dict[str, Any]]:
        return {
            "topic": {
                "type": str,
                "required": True,
                "description": "Topic to research"
            },
            "depth": {
                "type": str,
                "required": False,
                "description": "Research depth (shallow, medium, deep)"
            }
        }


class LibriscribeOutlineTool(MCPToolWrapper):
    """Tool for creating document outlines via Libriscribe MCP Server."""
    
    def __init__(self):
        client = LibriscribeMCPClient()
        super().__init__(
            name="create_outline",
            description="Create a structured outline for a document or book",
            mcp_client=client,
            tool_name="create_outline"
        )
    
    @property
    def parameters(self) -> Dict[str, Dict[str, Any]]:
        return {
            "concept": {
                "type": str,
                "required": True,
                "description": "Document concept or synopsis"
            },
            "num_chapters": {
                "type": int,
                "required": False,
                "description": "Number of chapters/sections (default: 10)"
            },
            "include_characters": {
                "type": bool,
                "required": False,
                "description": "Whether to include character development (default: true)"
            }
        }


class PodcastfyTool(Tool):
    """Tool for generating podcasts via Podcastfy MCP Server."""
    
    def __init__(self):
        super().__init__(
            name="podcastify",
            description="Generate high-quality podcast episodes from topics or text using Podcastfy MCP Server"
        )
        self.mcp_client = PodcastfyMCPClient()
    
    @property
    def parameters(self) -> Dict[str, Dict[str, Any]]:
        return {
            "topic": {
                "type": str,
                "required": False,
                "description": "Podcast topic (use either topic or text)"
            },
            "text": {
                "type": str,
                "required": False,
                "description": "Text content to convert to podcast (use either topic or text)"
            },
            "duration_minutes": {
                "type": int,
                "required": False,
                "description": "Duration in minutes (default: 10)"
            },
            "style": {
                "type": str,
                "required": False,
                "description": "Podcast style (conversational, educational, storytelling)"
            },
            "voice_preference": {
                "type": str,
                "required": False,
                "description": "Voice style (professional, casual, friendly)"
            },
            "output_format": {
                "type": str,
                "required": False,
                "description": "Audio format (mp3, wav)"
            }
        }
    
    def execute(self, **kwargs) -> ToolResult:
        """Generate podcast using Podcastfy MCP Server."""
        try:
            topic = kwargs.get('topic')
            text = kwargs.get('text')
            duration_minutes = kwargs.get('duration_minutes', 10)
            
            if not topic and not text:
                return ToolResult(
                    success=False,
                    error="Either 'topic' or 'text' parameter is required"
                )
            
            # Use topic-based generation if topic is provided, otherwise use text
            if topic:
                file_path = self.mcp_client.generate_podcast_from_topic(
                    topic=topic,
                    duration_minutes=duration_minutes,
                    style=kwargs.get('style'),
                    voice_preference=kwargs.get('voice_preference'),
                    output_format=kwargs.get('output_format', 'mp3')
                )
            else:
                file_path = self.mcp_client.generate_podcast_from_text(
                    text=text,
                    style=kwargs.get('style'),
                    voice_preference=kwargs.get('voice_preference'),
                    output_format=kwargs.get('output_format', 'mp3')
                )
            
            if file_path:
                return ToolResult(
                    success=True,
                    data={"file_path": file_path},
                    metadata={"mcp_tool": "podcastfy", "source": "mcp"}
                )
            else:
                return ToolResult(
                    success=False,
                    error="Podcast generation failed",
                    metadata={"mcp_tool": "podcastfy"}
                )
                
        except Exception as e:
            self.logger.error(f"Podcast generation failed: {e}")
            return ToolResult(
                success=False,
                error=str(e),
                metadata={"mcp_tool": "podcastfy"}
            )
