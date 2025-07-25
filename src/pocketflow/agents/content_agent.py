"""
Content agent for PocketFlow.

This agent handles content generation tasks and can work with research findings
to create informed content.
"""

from typing import Dict, Any, List
from ..agents.base_agent import BaseAgent, AgentAction, AgentDecision
from ..core.types import SharedState
from ..services import content_service, llm_service
from ..utils.logging import get_logger


class ContentAgent(BaseAgent):
    """Agent specialized in content generation tasks."""
    
    def __init__(self):
        super().__init__("ContentAgent")
        self.content_generated = False
        self.generated_content = {}
        self.content_type = None
    
    def analyze(self, shared: SharedState) -> AgentDecision:
        """Analyze the current state and decide what to do."""
        
        email = shared.get("email", {})
        body = email.get("body", "").lower()
        
        # Check if we have research findings to work with
        research_findings = shared.get("research_findings", {})
        
        # If we haven't started content generation yet
        if not self.content_generated:
            return AgentDecision(
                action=AgentAction.GENERATE_CONTENT,
                confidence=0.9,
                reasoning="Starting content generation",
                parameters={
                    "content_type": "auto_detect",
                    "research_findings": research_findings,
                    "user_request": body
                },
                next_agent=None
            )
        
        # If content is generated, send it
        if self.content_generated:
            return AgentDecision(
                action=AgentAction.SEND_EMAIL,
                confidence=1.0,
                reasoning="Content generated, sending response",
                parameters={"content": self.generated_content},
                next_agent="EmailAgent"
            )
        
        # Continue content generation
        return AgentDecision(
            action=AgentAction.GENERATE_CONTENT,
            confidence=0.7,
            reasoning="Continuing content generation",
            parameters={"content_type": self.content_type},
            next_agent=None
        )
    
    def execute(self, action: AgentAction, shared: SharedState, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the content generation action."""
        
        if action == AgentAction.GENERATE_CONTENT:
            return self._execute_content_generation(shared, parameters)
        elif action == AgentAction.SEND_EMAIL:
            return self._prepare_email_sending(shared, parameters)
        else:
            return {"success": False, "error": f"Unknown action: {action}"}
    
    def _execute_content_generation(self, shared: SharedState, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute content generation."""
        try:
            content_type = parameters.get("content_type", "auto_detect")
            research_findings = parameters.get("research_findings", {})
            user_request = parameters.get("user_request", "")
            
            self.logger.info(f"Starting content generation: {content_type}")
            
            # Determine content type if auto-detect
            if content_type == "auto_detect":
                content_type = self._detect_content_type(user_request)
            
            self.content_type = content_type
            
            # Prepare generation parameters
            generation_params = self._prepare_generation_params(
                content_type, user_request, research_findings
            )
            
            # Generate content
            result = content_service.generate_content(generation_params)
            
            if not result.get("success"):
                return {"success": False, "error": "Content generation failed"}
            
            # Store generated content
            self.generated_content = {
                "type": content_type,
                "file_path": result.get("file_path"),
                "metadata": result.get("metadata", {}),
                "research_based": bool(research_findings),
                "research_topic": research_findings.get("topic") if research_findings else None
            }
            
            self.content_generated = True
            self.update_context({"generated_content": self.generated_content})
            
            self.logger.info(f"Content generated successfully: {content_type}")
            
            return {
                "success": True,
                "content": self.generated_content,
                "content_type": content_type
            }
            
        except Exception as e:
            self.logger.error(f"Error in content generation: {e}")
            return {"success": False, "error": str(e)}
    
    def _detect_content_type(self, user_request: str) -> str:
        """Detect the type of content to generate based on user request."""
        user_request_lower = user_request.lower()
        
        if any(word in user_request_lower for word in ["song", "music", "audio", "melody"]):
            return "sound"
        elif any(word in user_request_lower for word in ["image", "picture", "photo", "visual"]):
            return "image"
        elif any(word in user_request_lower for word in ["document", "report", "text", "article"]):
            return "document"
        elif any(word in user_request_lower for word in ["podcast", "audio", "recording"]):
            return "podcast"
        else:
            # Default to document for text-based content
            return "document"
    
    def _prepare_generation_params(self, content_type: str, user_request: str, research_findings: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare parameters for content generation."""
        
        # Base parameters
        params = {
            "content_type": content_type,
            "user_request": user_request,
            "duration": "2 minutes" if content_type == "sound" else None,
            "style": "professional" if content_type == "document" else "creative"
        }
        
        # If we have research findings, enhance the prompt for document generation
        if research_findings and content_type == "document":
            research_topic = research_findings.get("topic", "")
            research_summary = research_findings.get("summary", "")
            research_sources = research_findings.get("sources", [])
            
            # Create an enhanced prompt that incorporates research findings
            enhanced_prompt = f"""
Based on the following research findings, create a comprehensive {content_type}:

**Research Topic:** {research_topic}
**Research Summary:** {research_summary}

**User Request:** {user_request}

**Additional Context:** The research was conducted using {len(research_sources)} sources to ensure comprehensive coverage of the topic.

Please create a professional document that:
1. Incorporates the research findings
2. Addresses the user's specific request
3. Provides a well-structured and informative report
4. Uses the research data to support conclusions and recommendations

Make sure the document is comprehensive, well-organized, and professionally formatted.
"""
            
            params["prompt"] = enhanced_prompt
            params["research_based"] = True
            params["research_findings"] = research_findings
        
        # If we have research findings, incorporate them
        if research_findings:
            research_summary = research_findings.get("summary", "")
            research_topic = research_findings.get("topic", "")
            
            # Create enhanced prompt with research
            enhanced_prompt = f"""
Based on the following research findings, please {user_request}:

Research Topic: {research_topic}
Research Summary: {research_summary}

Please incorporate the research findings into the generated content to ensure accuracy and relevance.
"""
            
            params["enhanced_prompt"] = enhanced_prompt
            params["research_context"] = {
                "topic": research_topic,
                "summary": research_summary,
                "sources": research_findings.get("sources", [])
            }
        
        return params
    
    def _prepare_email_sending(self, shared: SharedState, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare content for email sending."""
        try:
            content = self.generated_content
            content_type = content.get("type", "unknown")
            file_path = content.get("file_path")
            
            # Create email response
            if content_type == "sound":
                subject = "Your Generated Song"
                body = "Here's your generated song as requested!"
            elif content_type == "image":
                subject = "Your Generated Image"
                body = "Here's your generated image as requested!"
            elif content_type == "document":
                subject = "Your Generated Document"
                body = "Here's your generated document as requested!"
            else:
                subject = "Your Generated Content"
                body = "Here's your generated content as requested!"
            
            # Add research context if available
            if content.get("research_based"):
                research_topic = content.get("research_topic")
                body += f"\n\nThis content was generated based on research about: {research_topic}"
            
            # Update shared state for email sending
            shared["email_response"] = {
                "subject": subject,
                "body": body,
                "attachments": [file_path] if file_path else []
            }
            
            self.logger.info("Content prepared for email sending")
            
            return {
                "success": True,
                "message": "Content prepared for email",
                "next_agent": "EmailAgent"
            }
            
        except Exception as e:
            self.logger.error(f"Error preparing email sending: {e}")
            return {"success": False, "error": str(e)}
    
    def get_capabilities(self) -> List[str]:
        """Get content agent capabilities."""
        return [
            "content_generation",
            "multi_format_generation",
            "research_based_content",
            "content_type_detection",
            "enhanced_prompting"
        ]
    
    def reset(self):
        """Reset content agent state."""
        super().reset()
        self.content_generated = False
        self.generated_content = {}
        self.content_type = None
        self.logger.info("Content agent reset")
    
    def get_content_status(self) -> Dict[str, Any]:
        """Get current content generation status."""
        return {
            "content_generated": self.content_generated,
            "content_type": self.content_type,
            "generated_content": self.generated_content,
            "context": self.context
        } 