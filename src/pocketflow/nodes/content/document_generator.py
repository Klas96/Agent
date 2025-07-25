"""
Document generator node for PocketFlow.

This node specializes in generating PDF documents using LaTeX templates.
"""

from typing import Dict, Any, Optional

from ...core.node import SimpleNode
from ...core.types import SharedState
from ...services import document_service
from ...utils.logging import get_logger


class DocumentGeneratorNode(SimpleNode):
    """Node for generating PDF documents using LaTeX templates."""
    
    def __init__(self, name: str = "document_generator"):
        super().__init__(name)
        self.logger = get_logger("DocumentGeneratorNode")
    
    def process(self, shared: SharedState) -> Dict[str, Any]:
        """
        Generate a PDF document using LaTeX templates.
        
        Args:
            shared: Shared state containing document request
            
        Returns:
            Processing result with routing information
        """
        try:
            # Get document request from shared state
            content_request = shared.get("content_request")
            if not content_request:
                self.logger.warning("No content request found")
                return {"route": "generation_failed", "error": "No content request"}
            
            # Check if this is a document request
            if content_request.content_type != "document":
                self.logger.info(f"Not a document request: {content_request.content_type}")
                return {"route": "default"}
            
            self.logger.info(f"Generating document: {content_request.prompt}")
            
            # Generate document using document service
            doc_service = document_service.DocumentService()
            pdf_path = doc_service.generate_document(content_request)
            
            if pdf_path:
                self.logger.info(f"Document generated successfully: {pdf_path}")
                
                # Store generated file path in shared state
                shared["attachment"] = pdf_path
                shared["generated_file_path"] = pdf_path
                shared["document_type"] = self._determine_document_type(content_request.prompt)
                
                # Set reply body based on document type
                doc_type = shared["document_type"]
                if doc_type == "business_report":
                    shared["reply_body"] = "Here is your business report! I've analyzed the topic and created a comprehensive business analysis with executive summary, recommendations, and conclusions."
                elif doc_type == "technical_report":
                    shared["reply_body"] = "Here is your technical report! I've created a detailed technical analysis with methodology, results, and discussion."
                else:
                    shared["reply_body"] = "Here is your report! I've created a comprehensive document based on your request."
                
                return {"route": "default"}
            else:
                self.logger.error("Document generation failed")
                shared["generation_error"] = (
                    "Sorry, your document could not be generated. Please check your request or try again later."
                )
                return {"route": "generation_failed", "error": "Document generation failed"}
                
        except Exception as e:
            self.logger.error(f"Document generation error: {e}")
            shared["generation_error"] = str(e)
            return {"route": "generation_failed", "error": str(e)}
    
    def _determine_document_type(self, prompt: str) -> str:
        """Determine the type of document based on the prompt."""
        prompt_lower = prompt.lower()
        
        if any(word in prompt_lower for word in ["business", "financial", "market", "company", "executive"]):
            return "business_report"
        elif any(word in prompt_lower for word in ["technical", "research", "analysis", "data", "methodology"]):
            return "technical_report"
        else:
            return "report" 