"""
MCP (Model Context Protocol) client service for communicating with external MCP servers.

This service allows PocketFlow to use external tools via MCP protocol instead of internal tools.
All non-Email/LLM functionality is now accessed via MPC processes.
"""

import requests
import json
import os
from pathlib import Path
from typing import Dict, Any, Optional, List
from ..config.settings import get_settings
from ..utils.logging import get_logger
from ..core.types import ContentGenerationRequest, ContentType


class MCPClient:
    """Client for communicating with MCP servers via HTTP."""
    
    def __init__(self, base_url: str, timeout: int = 300):
        """
        Initialize MCP client.
        
        Args:
            base_url: Base URL of the MCP server (e.g., "http://localhost:8002")
            timeout: Request timeout in seconds
        """
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.logger = get_logger(f"MCPClient({base_url})")
    
    def health_check(self) -> bool:
        """Check if the MCP server is healthy."""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=10)
            return response.status_code == 200
        except Exception as e:
            self.logger.error(f"Health check failed: {e}")
            return False
    
    def list_tools(self) -> List[Dict[str, Any]]:
        """
        List all available tools from the MCP server.
        
        Returns:
            List of tool definitions
        """
        try:
            response = requests.get(f"{self.base_url}/tools", timeout=10)
            response.raise_for_status()
            data = response.json()
            return data.get('tools', [])
        except Exception as e:
            self.logger.error(f"Failed to list tools: {e}")
            return []
    
    def call_tool(self, tool_name: str, **kwargs) -> Dict[str, Any]:
        """
        Call a tool on the MCP server.
        
        Args:
            tool_name: Name of the tool to call
            **kwargs: Tool parameters
            
        Returns:
            Tool execution result
        """
        try:
            self.logger.info(f"Calling MCP tool '{tool_name}' with params: {kwargs}")
            
            # Libriscribe MCP Server expects: {"name": "tool_name", "arguments": {...}}
            payload = {
                "name": tool_name,
                "arguments": kwargs
            }
            
            # Use the standard endpoint
            endpoint = f"{self.base_url}/tools/{tool_name}"
            
            try:
                response = requests.post(
                    endpoint,
                    json=payload,
                    timeout=self.timeout,
                    headers={"Content-Type": "application/json"}
                )
                
                response.raise_for_status()
                result = response.json()
                self.logger.info(f"Tool '{tool_name}' executed successfully")
                return {
                    "success": True,
                    "data": result,
                    "tool_name": tool_name
                }
                        
            except requests.exceptions.RequestException as e:
                raise
            
        except Exception as e:
            self.logger.error(f"Failed to call tool '{tool_name}': {e}")
            return {
                "success": False,
                "error": str(e),
                "tool_name": tool_name
            }


class PodcastfyMCPClient(MCPClient):
    """Specialized client for Podcastfy MCP Server."""
    
    def __init__(self, base_url: str = "http://localhost:8000", timeout: int = 600):
        """
        Initialize Podcastfy MCP client.
        
        Args:
            base_url: Base URL of Podcastfy server (default: http://localhost:8000)
            timeout: Request timeout in seconds (default: 600 for podcast generation)
        """
        super().__init__(base_url, timeout)
        self.logger = get_logger("PodcastfyMCPClient")
    
    def generate_podcast_from_topic(self, topic: str, duration_minutes: int = 10, **kwargs) -> Optional[str]:
        """
        Generate a podcast from a topic using Podcastfy MCP Server.
        
        Args:
            topic: Podcast topic
            duration_minutes: Duration in minutes
            **kwargs: Additional parameters (style, voice, etc.)
            
        Returns:
            Path to generated audio file, or None if failed
        """
        try:
            self.logger.info(f"Generating podcast via Podcastfy: {topic}")
            
            payload = {
                "topic": topic,
                "duration_minutes": duration_minutes,
                **kwargs
            }
            
            response = requests.post(
                f"{self.base_url}/generate/topic",
                json=payload,
                timeout=self.timeout,
                headers={"Content-Type": "application/json"}
            )
            
            response.raise_for_status()
            result = response.json()
            
            # Extract file path from result
            # The response structure may vary, check common fields
            file_path = (
                result.get('file_path') or
                result.get('audio_path') or
                result.get('output_path') or
                result.get('path') or
                result.get('data', {}).get('file_path') or
                result.get('data', {}).get('audio_path')
            )
            
            if file_path:
                self.logger.info(f"Podcast generated successfully: {file_path}")
                return file_path
            else:
                # If no file path, check if we need to save the audio data
                audio_data = result.get('audio') or result.get('data', {}).get('audio')
                if audio_data:
                    # Save audio data to file
                    from ..config.settings import get_settings
                    import uuid
                    
                    settings = get_settings()
                    output_dir = Path(settings.CONTENT_OUTPUT_DIR)
                    output_dir.mkdir(parents=True, exist_ok=True)
                    
                    filename = f"podcast_{uuid.uuid4().hex[:8]}.mp3"
                    file_path = output_dir / filename
                    
                    # Handle base64 encoded audio or binary data
                    if isinstance(audio_data, str):
                        import base64
                        audio_bytes = base64.b64decode(audio_data)
                        with open(file_path, 'wb') as f:
                            f.write(audio_bytes)
                    else:
                        with open(file_path, 'wb') as f:
                            f.write(audio_data)
                    
                    return str(file_path)
                else:
                    self.logger.warning("No file path or audio data in Podcastfy response")
                    return None
                    
        except Exception as e:
            self.logger.error(f"Error generating podcast via Podcastfy: {e}")
            return None
    
    def generate_podcast_from_text(self, text: str, **kwargs) -> Optional[str]:
        """
        Generate a podcast from text content.
        
        Args:
            text: Text content to convert to podcast
            **kwargs: Additional parameters
            
        Returns:
            Path to generated audio file, or None if failed
        """
        try:
            self.logger.info(f"Generating podcast from text via Podcastfy")
            
            payload = {
                "text": text,
                **kwargs
            }
            
            response = requests.post(
                f"{self.base_url}/generate/text",
                json=payload,
                timeout=self.timeout,
                headers={"Content-Type": "application/json"}
            )
            
            response.raise_for_status()
            result = response.json()
            
            # Extract file path (similar to generate_podcast_from_topic)
            file_path = (
                result.get('file_path') or
                result.get('audio_path') or
                result.get('output_path') or
                result.get('path')
            )
            
            if file_path:
                return file_path
            else:
                # Handle audio data if provided
                audio_data = result.get('audio') or result.get('data', {}).get('audio')
                if audio_data:
                    from ..config.settings import get_settings
                    import uuid
                    import base64
                    
                    settings = get_settings()
                    output_dir = Path(settings.CONTENT_OUTPUT_DIR)
                    output_dir.mkdir(parents=True, exist_ok=True)
                    
                    filename = f"podcast_{uuid.uuid4().hex[:8]}.mp3"
                    file_path = output_dir / filename
                    
                    if isinstance(audio_data, str):
                        audio_bytes = base64.b64decode(audio_data)
                        with open(file_path, 'wb') as f:
                            f.write(audio_bytes)
                    else:
                        with open(file_path, 'wb') as f:
                            f.write(audio_data)
                    
                    return str(file_path)
                return None
                
        except Exception as e:
            self.logger.error(f"Error generating podcast from text: {e}")
            return None


class LibriscribeMCPClient(MCPClient):
    """Specialized client for Libriscribe MCP Server."""
    
    def __init__(self, base_url: str = "http://localhost:8002", timeout: int = 600):
        """
        Initialize Libriscribe MCP client.
        
        Args:
            base_url: Base URL of Libriscribe server (default: http://localhost:8002)
            timeout: Request timeout in seconds (default: 600 for document generation)
        """
        super().__init__(base_url, timeout)
        self.logger = get_logger("LibriscribeMCPClient")
    
    def generate_document(self, prompt: str, document_type: str = "report", **kwargs) -> Optional[str]:
        """
        Generate a document using Libriscribe.
        
        For reports/documents, we use a workflow:
        1. Create an outline (structure the document)
        2. Write content sections
        3. Format as a complete document
        
        Args:
            prompt: Document generation prompt
            document_type: Type of document (report, book, etc.)
            **kwargs: Additional parameters
            
        Returns:
            Path to generated document file, or None if failed
        """
        try:
            self.logger.info(f"Generating {document_type} document via Libriscribe: {prompt}")
            
            # For document generation, we'll use format_book which can format complete documents
            # First, create an outline for the document structure
            outline_result = self.call_tool(
                'create_outline',
                concept=prompt,
                num_chapters=5 if document_type == "report" else 10,  # Reports are shorter
                include_characters=False  # Not needed for reports
            )
            
            if not outline_result.get('success'):
                self.logger.error(f"Failed to create outline: {outline_result.get('error')}")
                return None
            
            outline_data = outline_result.get('data', {})
            outline_content = outline_data.get('outline', '') or outline_data.get('content', '')
            
            if not outline_content:
                self.logger.warning("Outline creation returned no content, using prompt directly")
                outline_content = prompt
            
            # Now format the document using format_book
            # This will create a formatted document from the outline
            format_result = self.call_tool(
                'format_book',
                title=f"{document_type.title()}: {prompt[:50]}",
                outline=outline_content,
                format="markdown"  # Request markdown format (Libriscribe returns markdown)
            )
            
            if format_result.get('success'):
                format_data = format_result.get('data', {})
                
                # Libriscribe returns content as markdown/text, not file paths
                content = format_data.get('content') or format_data.get('document') or format_data.get('text', '')
                
                if not content:
                    self.logger.warning("No content in format_book result")
                    return None
                
                # Save content to a file
                from ..config.settings import get_settings
                import uuid
                
                settings = get_settings()
                output_dir = Path(settings.CONTENT_OUTPUT_DIR)
                output_dir.mkdir(parents=True, exist_ok=True)
                
                # Save as markdown file
                filename = f"document_{uuid.uuid4().hex[:8]}.md"
                file_path = output_dir / filename
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                self.logger.info(f"Document generated successfully: {file_path}")
                
                # Optionally convert to PDF if pandoc is available
                pdf_path = self._convert_markdown_to_pdf(file_path)
                if pdf_path:
                    return str(pdf_path)
                else:
                    # Return markdown file if PDF conversion fails
                    return str(file_path)
            else:
                self.logger.error(f"Document formatting failed: {format_result.get('error')}")
                return None
                
        except Exception as e:
            self.logger.error(f"Error generating document via Libriscribe: {e}")
            return None
    
    def _convert_markdown_to_pdf(self, markdown_path: Path) -> Optional[Path]:
        """
        Convert markdown file to PDF using pandoc.
        
        Args:
            markdown_path: Path to markdown file
            
        Returns:
            Path to PDF file, or None if conversion fails
        """
        try:
            import subprocess
            
            pdf_path = markdown_path.with_suffix('.pdf')
            
            # Try to convert using pandoc
            result = subprocess.run(
                ['pandoc', str(markdown_path), '-o', str(pdf_path), '--pdf-engine=pdflatex'],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0 and pdf_path.exists():
                self.logger.info(f"Converted markdown to PDF: {pdf_path}")
                return pdf_path
            else:
                self.logger.warning(f"PDF conversion failed: {result.stderr}")
                return None
                
        except FileNotFoundError:
            self.logger.warning("pandoc not found, skipping PDF conversion")
            return None
        except Exception as e:
            self.logger.warning(f"PDF conversion error: {e}")
            return None


class MPCManager:
    """
    Unified manager for all MPC (Multi-Process Communication) services.
    
    This manager provides a single interface to communicate with external MPC processes:
    - Content-MPC: Content generation (audio, images, documents)
    - Tools-MPC: Tool execution (calculator, file operations, etc.)
    - Research-MPC: Web search and investigation
    """
    
    def __init__(self):
        """Initialize MPC manager with all service clients."""
        settings = get_settings()
        self.logger = get_logger("MPCManager")
        
        # Get MPC URLs from environment or use defaults
        self.content_mpc_url = os.getenv("CONTENT_MPC_URL", "http://localhost:8001")
        self.tools_mpc_url = os.getenv("TOOLS_MPC_URL", "http://localhost:8003")
        self.research_mpc_url = os.getenv("RESEARCH_MPC_URL", "http://localhost:8004")
        
        # Initialize clients
        self.content_client = MCPClient(self.content_mpc_url, timeout=600)
        self.tools_client = MCPClient(self.tools_mpc_url, timeout=300)
        self.research_client = MCPClient(self.research_mpc_url, timeout=300)
        
        # Check health of all services
        self._check_health()
    
    def _check_health(self):
        """Check health of all MPC services."""
        services = {
            "Content-MPC": self.content_client,
            "Tools-MPC": self.tools_client,
            "Research-MPC": self.research_client
        }
        
        for name, client in services.items():
            if client.health_check():
                self.logger.info(f"{name} is healthy at {client.base_url}")
            else:
                self.logger.warning(f"{name} is not available at {client.base_url}")
    
    # ========== Content Generation Methods ==========
    
    def generate_content(self, request: ContentGenerationRequest) -> Optional[str]:
        """
        Generate content via Content-MPC.
        
        Args:
            request: ContentGenerationRequest with generation parameters
            
        Returns:
            Path to generated file, or None if failed
        """
        try:
            self.logger.info(f"Requesting content generation: {request.content_type}")
            
            # Prepare payload for Content-MPC
            payload = {
                "content_type": request.content_type.value if isinstance(request.content_type, ContentType) else request.content_type,
                "prompt": request.prompt,
                "duration": request.duration
            }
            
            # Call Content-MPC
            result = self.content_client.call_tool("generate", **payload)
            
            if result.get("success"):
                file_path = result.get("data", {}).get("file_path")
                if file_path:
                    self.logger.info(f"Content generated successfully: {file_path}")
                    return file_path
                else:
                    self.logger.warning("Content generation succeeded but no file path returned")
                    return None
            else:
                error = result.get("error", "Unknown error")
                self.logger.error(f"Content generation failed: {error}")
                return None
                
        except Exception as e:
            self.logger.error(f"Error calling Content-MPC: {e}")
            return None
    
    # ========== Tools Execution Methods ==========
    
    def execute_tool(self, tool_name: str, **parameters) -> Dict[str, Any]:
        """
        Execute a tool via Tools-MPC.
        
        Args:
            tool_name: Name of the tool to execute
            **parameters: Tool parameters
            
        Returns:
            Tool execution result
        """
        try:
            self.logger.info(f"Executing tool '{tool_name}' via Tools-MPC")
            result = self.tools_client.call_tool(tool_name, **parameters)
            return result
        except Exception as e:
            self.logger.error(f"Error executing tool '{tool_name}': {e}")
            return {
                "success": False,
                "error": str(e),
                "tool_name": tool_name
            }
    
    # ========== Research/Investigation Methods ==========
    
    def investigate_topic(self, topic: str, depth: str = "shallow", max_results: int = 10) -> Dict[str, Any]:
        """
        Investigate a topic via Research-MPC.
        
        Args:
            topic: Topic to investigate
            depth: Investigation depth ("shallow" or "deep")
            max_results: Maximum number of results
            
        Returns:
            Investigation results with findings and summary
        """
        try:
            self.logger.info(f"Investigating topic '{topic}' via Research-MPC")
            result = self.research_client.call_tool(
                "investigate",
                topic=topic,
                depth=depth,
                max_results=max_results
            )
            
            if result.get("success"):
                return result.get("data", {})
            else:
                return {
                    "findings": [],
                    "summary": f"Investigation failed: {result.get('error')}"
                }
        except Exception as e:
            self.logger.error(f"Error investigating topic: {e}")
            return {
                "findings": [],
                "summary": f"Investigation error: {str(e)}"
            }
    
    def web_search(self, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """
        Perform web search via Research-MPC.
        
        Args:
            query: Search query
            max_results: Maximum number of results
            
        Returns:
            List of search results
        """
        try:
            result = self.research_client.call_tool(
                "web_search",
                query=query,
                max_results=max_results
            )
            
            if result.get("success"):
                return result.get("data", {}).get("results", [])
            return []
        except Exception as e:
            self.logger.error(f"Error performing web search: {e}")
            return []


# Global MPC manager instance
_mpc_manager: Optional[MPCManager] = None


def get_mpc_manager() -> MPCManager:
    """Get or create the global MPC manager instance."""
    global _mpc_manager
    if _mpc_manager is None:
        _mpc_manager = MPCManager()
    return _mpc_manager
