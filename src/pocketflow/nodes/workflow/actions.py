"""
Action nodes for PocketFlow n8n-like workflow system.

This module provides action nodes that perform specific tasks.
"""

import json
import os
from typing import Dict, Any, List
from datetime import datetime
from pathlib import Path

from .base import ActionNode, NodeInput, NodeOutput, NodeMetadata
from ..core.types import SharedState
from ..services.email_service import EmailService
from ..services.content_service import ContentService
from ..services.websearch_service import WebSearchService
from ..services.llm_service import LLMService
from ..config.settings import get_settings


class SendEmailAction(ActionNode):
    """
    Action node that sends emails.
    
    Based on the existing email sending functionality.
    """
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.email_service = EmailService()
        self.settings = get_settings()
        
    def execute(self, shared: SharedState) -> Dict[str, Any]:
        """
        Send an email using the configured parameters.
        
        Args:
            shared: Shared state
            
        Returns:
            Dictionary with send result
        """
        try:
            # Get email parameters from config or shared state
            to_email = self.get_input_value("to_email")
            if not to_email and "email" in shared:
                to_email = shared["email"].get("from", "")
            
            subject = self.get_input_value("subject", "Response from PocketFlow")
            body = self.get_input_value("body", "")
            
            # Get email configuration
            host = self.get_input_value("host", self.settings.EMAIL_HOST)
            port = self.get_input_value("port", self.settings.EMAIL_PORT)
            username = self.get_input_value("username", self.settings.EMAIL_USERNAME)
            password = self.get_input_value("password", self.settings.EMAIL_PASSWORD)
            use_tls = self.get_input_value("use_tls", self.settings.EMAIL_USE_TLS)
            
            if not to_email:
                raise ValueError("No recipient email address specified")
            
            if not body:
                raise ValueError("No email body specified")
            
            self.logger.info(f"Sending email to: {to_email}")
            
            # Send the email
            success = self.email_service.send_email(
                to_email=to_email,
                subject=subject,
                body=body,
                host=host,
                port=port,
                username=username,
                password=password,
                use_tls=use_tls
            )
            
            if success:
                self.logger.info(f"Email sent successfully to {to_email}")
                
                # Set outputs
                self.set_output(shared, "sent_to", to_email)
                self.set_output(shared, "sent_at", datetime.now().isoformat())
                self.set_output(shared, "subject", subject)
                
                return {
                    "success": True,
                    "sent_to": to_email,
                    "sent_at": datetime.now().isoformat(),
                    "message": f"Email sent successfully to {to_email}"
                }
            else:
                raise Exception("Failed to send email")
                
        except Exception as e:
            self.logger.error(f"Error sending email: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    @classmethod
    def get_metadata(cls) -> NodeMetadata:
        """Get metadata for SendEmailAction."""
        return NodeMetadata(
            name="SendEmailAction",
            description="Sends an email response",
            category="action",
            inputs=[
                NodeInput("to_email", "string", "Recipient email address", True),
                NodeInput("subject", "string", "Email subject", False, "Response from PocketFlow"),
                NodeInput("body", "string", "Email body", True),
                NodeInput("host", "string", "SMTP host", False),
                NodeInput("port", "number", "SMTP port", False),
                NodeInput("username", "string", "Email username", False),
                NodeInput("password", "string", "Email password", False),
                NodeInput("use_tls", "boolean", "Use TLS", False, True)
            ],
            outputs=[
                NodeOutput("sent_to", "string", "Email address the message was sent to"),
                NodeOutput("sent_at", "string", "When the email was sent"),
                NodeOutput("subject", "string", "Subject of the sent email")
            ],
            icon="send",
            color="#4CAF50"
        )


class GenerateContentAction(ActionNode):
    """
    Action node that generates content (audio, image, etc.).
    
    Based on the existing content generation functionality.
    """
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.content_service = ContentService()
        self.settings = get_settings()
        
    def execute(self, shared: SharedState) -> Dict[str, Any]:
        """
        Generate content based on the specified type and parameters.
        
        Args:
            shared: Shared state
            
        Returns:
            Dictionary with generation result
        """
        try:
            content_type = self.get_input_value("content_type", "audio")
            prompt = self.get_input_value("prompt", "")
            output_format = self.get_input_value("output_format", "mp3")
            
            if not prompt:
                raise ValueError("No prompt specified for content generation")
            
            self.logger.info(f"Generating {content_type} content: {prompt[:50]}...")
            
            # Generate content based on type
            if content_type == "audio":
                result = self.content_service.generate_audio(
                    prompt=prompt,
                    output_format=output_format
                )
            elif content_type == "image":
                result = self.content_service.generate_image(
                    prompt=prompt,
                    output_format=output_format
                )
            else:
                raise ValueError(f"Unsupported content type: {content_type}")
            
            if result.get("success"):
                # Set outputs
                self.set_output(shared, "content_url", result.get("url", ""))
                self.set_output(shared, "content_type", content_type)
                self.set_output(shared, "generated_at", datetime.now().isoformat())
                
                return {
                    "success": True,
                    "content_url": result.get("url", ""),
                    "content_type": content_type,
                    "generated_at": datetime.now().isoformat(),
                    "message": f"Generated {content_type} content successfully"
                }
            else:
                raise Exception(result.get("error", "Content generation failed"))
                
        except Exception as e:
            self.logger.error(f"Error generating content: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    @classmethod
    def get_metadata(cls) -> NodeMetadata:
        """Get metadata for GenerateContentAction."""
        return NodeMetadata(
            name="GenerateContentAction",
            description="Generates audio, image, or other content",
            category="action",
            inputs=[
                NodeInput("content_type", "string", "Type of content to generate", True),
                NodeInput("prompt", "string", "Prompt for content generation", True),
                NodeInput("output_format", "string", "Output format", False, "mp3")
            ],
            outputs=[
                NodeOutput("content_url", "string", "URL or path to generated content"),
                NodeOutput("content_type", "string", "Type of content generated"),
                NodeOutput("generated_at", "string", "When the content was generated")
            ],
            icon="create",
            color="#9C27B0"
        )


class GenerateLatexAction(ActionNode):
    """
    Action node that generates LaTeX documents.
    
    Based on the existing LaTeX template functionality.
    """
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.settings = get_settings()
        
    def execute(self, shared: SharedState) -> Dict[str, Any]:
        """
        Generate a LaTeX document using templates.
        
        Args:
            shared: Shared state
            
        Returns:
            Dictionary with generation result
        """
        try:
            template_name = self.get_input_value("template", "report")
            title = self.get_input_value("title", "Generated Report")
            content = self.get_input_value("content", "")
            author = self.get_input_value("author", "PocketFlow")
            
            if not content:
                raise ValueError("No content specified for LaTeX generation")
            
            self.logger.info(f"Generating LaTeX document with template: {template_name}")
            
            # Load template
            template_path = Path("templates/latex") / f"{template_name}.tex"
            if not template_path.exists():
                raise ValueError(f"Template not found: {template_name}")
            
            with open(template_path, 'r') as f:
                template_content = f.read()
            
            # Replace placeholders
            latex_content = template_content.replace("{{TITLE}}", title)
            latex_content = latex_content.replace("{{AUTHOR}}", author)
            latex_content = latex_content.replace("{{CONTENT}}", content)
            
            # Generate output filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_filename = f"{template_name}_{timestamp}.tex"
            output_path = Path(self.settings.CONTENT_OUTPUT_DIR) / output_filename
            
            # Ensure output directory exists
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write LaTeX file
            with open(output_path, 'w') as f:
                f.write(latex_content)
            
            self.logger.info(f"LaTeX document generated: {output_path}")
            
            # Set outputs
            self.set_output(shared, "latex_file", str(output_path))
            self.set_output(shared, "template_used", template_name)
            self.set_output(shared, "generated_at", datetime.now().isoformat())
            
            return {
                "success": True,
                "latex_file": str(output_path),
                "template_used": template_name,
                "generated_at": datetime.now().isoformat(),
                "message": f"LaTeX document generated: {output_filename}"
            }
            
        except Exception as e:
            self.logger.error(f"Error generating LaTeX: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    @classmethod
    def get_metadata(cls) -> NodeMetadata:
        """Get metadata for GenerateLatexAction."""
        return NodeMetadata(
            name="GenerateLatexAction",
            description="Generates LaTeX documents using templates",
            category="action",
            inputs=[
                NodeInput("template", "string", "LaTeX template name", False, "report"),
                NodeInput("title", "string", "Document title", False, "Generated Report"),
                NodeInput("content", "string", "Document content", True),
                NodeInput("author", "string", "Document author", False, "PocketFlow")
            ],
            outputs=[
                NodeOutput("latex_file", "string", "Path to generated LaTeX file"),
                NodeOutput("template_used", "string", "Template used for generation"),
                NodeOutput("generated_at", "string", "When the document was generated")
            ],
            icon="description",
            color="#FF5722"
        )


class WebSearchAction(ActionNode):
    """
    Action node that performs web searches.
    
    Based on the existing web search functionality.
    """
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.websearch_service = WebSearchService()
        
    def execute(self, shared: SharedState) -> Dict[str, Any]:
        """
        Perform a web search and return results.
        
        Args:
            shared: Shared state
            
        Returns:
            Dictionary with search results
        """
        try:
            query = self.get_input_value("query", "")
            max_results = self.get_input_value("max_results", 5)
            
            if not query:
                raise ValueError("No search query specified")
            
            self.logger.info(f"Performing web search: {query}")
            
            # Perform search
            results = self.websearch_service.search(
                query=query,
                max_results=max_results
            )
            
            if results:
                # Set outputs
                self.set_output(shared, "search_results", results)
                self.set_output(shared, "query", query)
                self.set_output(shared, "result_count", len(results))
                
                return {
                    "success": True,
                    "search_results": results,
                    "query": query,
                    "result_count": len(results),
                    "message": f"Found {len(results)} search results for '{query}'"
                }
            else:
                return {
                    "success": False,
                    "message": f"No results found for query: {query}"
                }
                
        except Exception as e:
            self.logger.error(f"Error performing web search: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    @classmethod
    def get_metadata(cls) -> NodeMetadata:
        """Get metadata for WebSearchAction."""
        return NodeMetadata(
            name="WebSearchAction",
            description="Performs web searches and returns results",
            category="action",
            inputs=[
                NodeInput("query", "string", "Search query", True),
                NodeInput("max_results", "number", "Maximum number of results", False, 5)
            ],
            outputs=[
                NodeOutput("search_results", "array", "Search results"),
                NodeOutput("query", "string", "Search query used"),
                NodeOutput("result_count", "number", "Number of results found")
            ],
            icon="search",
            color="#607D8B"
        )


class HttpRequestAction(ActionNode):
    """
    Action node that makes HTTP requests.
    """
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        
    def execute(self, shared: SharedState) -> Dict[str, Any]:
        """
        Make an HTTP request to the specified URL.
        
        Args:
            shared: Shared state
            
        Returns:
            Dictionary with request result
        """
        try:
            import requests
            
            url = self.get_input_value("url", "")
            method = self.get_input_value("method", "GET")
            headers = self.get_input_value("headers", {})
            data = self.get_input_value("data", {})
            timeout = self.get_input_value("timeout", 30)
            
            if not url:
                raise ValueError("No URL specified")
            
            self.logger.info(f"Making {method} request to: {url}")
            
            # Make request
            response = requests.request(
                method=method,
                url=url,
                headers=headers,
                json=data if method in ["POST", "PUT", "PATCH"] else None,
                params=data if method == "GET" else None,
                timeout=timeout
            )
            
            # Set outputs
            self.set_output(shared, "status_code", response.status_code)
            self.set_output(shared, "response_headers", dict(response.headers))
            self.set_output(shared, "response_body", response.text)
            
            return {
                "success": response.status_code < 400,
                "status_code": response.status_code,
                "response_headers": dict(response.headers),
                "response_body": response.text,
                "url": url,
                "method": method,
                "message": f"HTTP {method} request completed with status {response.status_code}"
            }
            
        except Exception as e:
            self.logger.error(f"Error making HTTP request: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    @classmethod
    def get_metadata(cls) -> NodeMetadata:
        """Get metadata for HttpRequestAction."""
        return NodeMetadata(
            name="HttpRequestAction",
            description="Makes HTTP requests to external APIs",
            category="action",
            inputs=[
                NodeInput("url", "string", "Request URL", True),
                NodeInput("method", "string", "HTTP method", False, "GET"),
                NodeInput("headers", "object", "Request headers", False, {}),
                NodeInput("data", "object", "Request data", False, {}),
                NodeInput("timeout", "number", "Request timeout in seconds", False, 30)
            ],
            outputs=[
                NodeOutput("status_code", "number", "HTTP status code"),
                NodeOutput("response_headers", "object", "Response headers"),
                NodeOutput("response_body", "string", "Response body")
            ],
            icon="http",
            color="#795548"
        ) 