"""
Research agent for PocketFlow.

This agent handles investigation and research tasks, and can intelligently
decide when to hand off to content generation based on findings.
"""

from typing import Dict, Any, List
from ..agents.base_agent import BaseAgent, AgentAction, AgentDecision
from ..core.types import SharedState
from ..services import websearch_service
from ..utils.logging import get_logger


class ResearchAgent(BaseAgent):
    """Agent specialized in research and investigation tasks."""
    
    def __init__(self):
        super().__init__("ResearchAgent")
        self.research_complete = False
        self.research_findings = {}
        self.content_generation_needed = False
    
    def analyze(self, shared: SharedState) -> AgentDecision:
        """Analyze the current state and decide what to do."""
        
        email = shared.get("email", {})
        body = email.get("body", "").lower()
        
        # If we haven't started research yet
        if not self.research_complete:
            return AgentDecision(
                action=AgentAction.INVESTIGATE,
                confidence=0.9,
                reasoning="Starting research investigation",
                parameters={"topic": body, "depth": "comprehensive"},
                next_agent=None
            )
        
        # If research is complete, check if we need content generation
        if self.research_complete and self.content_generation_needed:
            return AgentDecision(
                action=AgentAction.GENERATE_CONTENT,
                confidence=0.8,
                reasoning="Research complete, generating content based on findings",
                parameters={
                    "agent": "ContentAgent",
                    "content_type": "research_based",
                    "research_findings": self.research_findings
                },
                next_agent="ContentAgent"
            )
        
        # If research is complete and no content needed
        if self.research_complete:
            return AgentDecision(
                action=AgentAction.SEND_EMAIL,
                confidence=1.0,
                reasoning="Research complete, sending findings",
                parameters={"content": self.research_findings},
                next_agent="EmailAgent"
            )
        
        # Continue research
        return AgentDecision(
            action=AgentAction.INVESTIGATE,
            confidence=0.7,
            reasoning="Continuing research investigation",
            parameters={"topic": body, "depth": "follow_up"},
            next_agent=None
        )
    
    def execute(self, action: AgentAction, shared: SharedState, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the research action."""
        
        if action == AgentAction.INVESTIGATE:
            return self._execute_investigation(shared, parameters)
        elif action == AgentAction.GENERATE_CONTENT:
            return self._prepare_content_generation(shared, parameters)
        elif action == AgentAction.SEND_EMAIL:
            return self._send_research_findings(shared, parameters)
        else:
            return {"success": False, "error": f"Unknown action: {action}"}
    
    def _execute_investigation(self, shared: SharedState, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the investigation."""
        try:
            topic = parameters.get("topic", "")
            depth = parameters.get("depth", "comprehensive")
            
            self.logger.info(f"Starting investigation: {topic} (depth: {depth})")
            
            # Perform web search
            search_results = websearch_service.search({
                "query": topic,
                "max_results": 10 if depth == "comprehensive" else 5,
                "include_summaries": True
            })
            
            if not search_results.get("success"):
                return {"success": False, "error": "Search failed"}
            
            # Analyze results and determine if content generation is needed
            findings = search_results.get("results", [])
            summary = websearch_service.summarize_results(findings)
            
            # Check if the request implies content generation
            email = shared.get("email", {})
            body = email.get("body", "").lower()
            
            content_keywords = ["generate", "create", "make", "song", "music", "image", "document", "write"]
            self.content_generation_needed = any(keyword in body for keyword in content_keywords)
            
            # Store findings
            self.research_findings = {
                "topic": topic,
                "summary": summary,
                "sources": findings,
                "content_generation_needed": self.content_generation_needed
            }
            
            self.research_complete = True
            self.update_context({"research_findings": self.research_findings})
            
            self.logger.info(f"Research complete. Content generation needed: {self.content_generation_needed}")
            
            return {
                "success": True,
                "findings": self.research_findings,
                "content_generation_needed": self.content_generation_needed
            }
            
        except Exception as e:
            self.logger.error(f"Error in investigation: {e}")
            return {"success": False, "error": str(e)}
    
    def _prepare_content_generation(self, shared: SharedState, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare for content generation based on research."""
        try:
            # Update shared state with research findings
            shared["research_findings"] = self.research_findings
            shared["content_generation_context"] = {
                "based_on_research": True,
                "research_topic": self.research_findings.get("topic"),
                "research_summary": self.research_findings.get("summary")
            }
            
            self.logger.info("Prepared research findings for content generation")
            
            return {
                "success": True,
                "message": "Research findings prepared for content generation",
                "next_agent": "ContentAgent"
            }
            
        except Exception as e:
            self.logger.error(f"Error preparing content generation: {e}")
            return {"success": False, "error": str(e)}
    
    def _send_research_findings(self, shared: SharedState, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Send research findings via email."""
        try:
            findings = self.research_findings
            summary = findings.get("summary", "No summary available")
            sources = findings.get("sources", [])
            
            # Format the response
            response_body = f"""
Research Findings for: {findings.get('topic', 'Unknown topic')}

Summary:
{summary}

Sources:
"""
            for i, source in enumerate(sources[:5], 1):
                response_body += f"{i}. {source.get('title', 'No title')} - {source.get('url', 'No URL')}\n"
            
            # Update shared state for email sending
            shared["email_response"] = {
                "subject": f"Research Findings: {findings.get('topic', 'Your request')}",
                "body": response_body,
                "attachments": []
            }
            
            self.logger.info("Research findings prepared for email sending")
            
            return {
                "success": True,
                "message": "Research findings prepared for email",
                "next_agent": "EmailAgent"
            }
            
        except Exception as e:
            self.logger.error(f"Error sending research findings: {e}")
            return {"success": False, "error": str(e)}
    
    def get_capabilities(self) -> List[str]:
        """Get research agent capabilities."""
        return [
            "web_search",
            "research_investigation",
            "findings_summarization",
            "content_generation_preparation",
            "research_based_workflows"
        ]
    
    def reset(self):
        """Reset research agent state."""
        super().reset()
        self.research_complete = False
        self.research_findings = {}
        self.content_generation_needed = False
        self.logger.info("Research agent reset")
    
    def get_research_status(self) -> Dict[str, Any]:
        """Get current research status."""
        return {
            "research_complete": self.research_complete,
            "content_generation_needed": self.content_generation_needed,
            "findings": self.research_findings,
            "context": self.context
        } 