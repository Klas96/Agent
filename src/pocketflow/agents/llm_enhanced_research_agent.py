"""
LLM-Enhanced Research Agent for PocketFlow.

This agent uses LLMs to make intelligent decisions about research tasks
and when to hand off to content generation.
"""

from typing import Dict, Any, List
from ..agents.base_agent import BaseAgent, AgentAction, AgentDecision
from ..core.types import SharedState
from ..services import websearch_service, llm_service
from ..utils.logging import get_logger


class LLMEnhancedResearchAgent(BaseAgent):
    """Agent specialized in research and investigation tasks using LLMs for decision-making."""
    
    def __init__(self):
        super().__init__("LLMResearchAgent")
        self.research_complete = False
        self.research_findings = {}
        self.content_generation_needed = False
    
    def analyze(self, shared: SharedState) -> AgentDecision:
        """Use LLM to analyze the current state and decide what to do."""
        
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
        
        # If research is complete, use LLM to decide next steps
        if self.research_complete:
            return self._llm_decide_next_steps(shared, body)
        
        # Continue research
        return AgentDecision(
            action=AgentAction.INVESTIGATE,
            confidence=0.7,
            reasoning="Continuing research investigation",
            parameters={"topic": body, "depth": "follow_up"},
            next_agent=None
        )
    
    def _llm_decide_next_steps(self, shared: SharedState, original_request: str) -> AgentDecision:
        """Use LLM to decide what to do after research is complete."""
        
        # Prepare context for LLM
        research_summary = self.research_findings.get("summary", "")
        research_topic = self.research_findings.get("topic", "")
        
        prompt = f"""
You are a research agent that has completed an investigation. Based on the research findings and the original user request, decide what to do next.

Original User Request: "{original_request}"
Research Topic: "{research_topic}"
Research Summary: "{research_summary}"

Available Actions:
1. Generate content based on research findings
2. Send research findings via email
3. Continue with more research

Please analyze the original request and research findings to determine if the user wants:
- Content generation (song, image, document) based on the research
- Just the research findings
- More investigation

Respond with a JSON object:
{{
    "action": "generate_content" | "send_email" | "continue_research",
    "reasoning": "explanation of decision",
    "confidence": 0.0-1.0,
    "content_generation_needed": true/false,
    "next_agent": "ContentAgent" | "EmailAgent" | null
}}

Consider:
1. Does the original request ask for content generation?
2. Are the research findings sufficient for content generation?
3. Does the user want just the research or content based on it?
4. Is more research needed?

Respond only with the JSON object.
"""
        
        try:
            # Call LLM
            response = llm_service.call_llm([
                {"role": "system", "content": "You are a research agent that decides what to do after completing research."},
                {"role": "user", "content": prompt}
            ])
            
            # Parse LLM response
            import json
            try:
                response_text = response.get("content", "")
                
                # Extract JSON from response
                start_idx = response_text.find('{')
                end_idx = response_text.rfind('}') + 1
                
                if start_idx != -1 and end_idx > start_idx:
                    json_str = response_text[start_idx:end_idx]
                    decision = json.loads(json_str)
                else:
                    decision = self._parse_llm_response_fallback(original_request)
                
                self.logger.info(f"LLM research decision: {decision}")
                
                # Update internal state based on LLM decision
                self.content_generation_needed = decision.get("content_generation_needed", False)
                
                # Return appropriate action
                action = decision.get("action", "send_email")
                reasoning = decision.get("reasoning", "LLM analysis")
                confidence = decision.get("confidence", 0.8)
                next_agent = decision.get("next_agent")
                
                if action == "generate_content":
                    return AgentDecision(
                        action=AgentAction.GENERATE_CONTENT,
                        confidence=confidence,
                        reasoning=reasoning,
                        parameters={
                            "agent": "ContentAgent",
                            "content_type": "research_based",
                            "research_findings": self.research_findings
                        },
                        next_agent="ContentAgent"
                    )
                elif action == "send_email":
                    return AgentDecision(
                        action=AgentAction.SEND_EMAIL,
                        confidence=confidence,
                        reasoning=reasoning,
                        parameters={"content": self.research_findings},
                        next_agent="EmailAgent"
                    )
                else:
                    return AgentDecision(
                        action=AgentAction.INVESTIGATE,
                        confidence=confidence,
                        reasoning=reasoning,
                        parameters={"topic": research_topic, "depth": "follow_up"},
                        next_agent=None
                    )
                
            except json.JSONDecodeError as e:
                self.logger.warning(f"Failed to parse LLM JSON response: {e}")
                return self._parse_llm_response_fallback(original_request)
                
        except Exception as e:
            self.logger.error(f"Error calling LLM for research decision: {e}")
            return self._fallback_research_decision(original_request)
    
    def _parse_llm_response_fallback(self, original_request: str) -> Dict[str, Any]:
        """Fallback parsing for LLM response."""
        request_lower = original_request.lower()
        
        # Check for content generation keywords
        content_keywords = ["generate", "create", "make", "song", "music", "image", "document", "write"]
        has_content_request = any(keyword in request_lower for keyword in content_keywords)
        
        if has_content_request:
            return {
                "action": "generate_content",
                "reasoning": "Original request contains content generation keywords",
                "confidence": 0.8,
                "content_generation_needed": True,
                "next_agent": "ContentAgent"
            }
        else:
            return {
                "action": "send_email",
                "reasoning": "Original request appears to be research-only",
                "confidence": 0.7,
                "content_generation_needed": False,
                "next_agent": "EmailAgent"
            }
    
    def _fallback_research_decision(self, original_request: str) -> AgentDecision:
        """Fallback decision when LLM fails."""
        request_lower = original_request.lower()
        
        # Check for content generation keywords
        content_keywords = ["generate", "create", "make", "song", "music", "image", "document"]
        has_content_request = any(keyword in request_lower for keyword in content_keywords)
        
        if has_content_request:
            self.content_generation_needed = True
            return AgentDecision(
                action=AgentAction.GENERATE_CONTENT,
                confidence=0.7,
                reasoning="Fallback: Original request contains content generation keywords",
                parameters={
                    "agent": "ContentAgent",
                    "content_type": "research_based",
                    "research_findings": self.research_findings
                },
                next_agent="ContentAgent"
            )
        else:
            return AgentDecision(
                action=AgentAction.SEND_EMAIL,
                confidence=0.7,
                reasoning="Fallback: Sending research findings",
                parameters={"content": self.research_findings},
                next_agent="EmailAgent"
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
            
            # Analyze results
            findings = search_results.get("results", [])
            summary = websearch_service.summarize_results(findings)
            
            # Store findings
            self.research_findings = {
                "topic": topic,
                "summary": summary,
                "sources": findings
            }
            
            self.research_complete = True
            self.update_context({"research_findings": self.research_findings})
            
            self.logger.info("Research complete")
            
            return {
                "success": True,
                "findings": self.research_findings
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
        """Get LLM research agent capabilities."""
        return [
            "llm_based_decision_making",
            "web_search",
            "research_investigation",
            "findings_summarization",
            "intelligent_handoff_decisions",
            "research_based_workflows"
        ]
    
    def reset(self):
        """Reset LLM research agent state."""
        super().reset()
        self.research_complete = False
        self.research_findings = {}
        self.content_generation_needed = False
        self.logger.info("LLM Research agent reset")
    
    def get_research_status(self) -> Dict[str, Any]:
        """Get current research status."""
        return {
            "research_complete": self.research_complete,
            "content_generation_needed": self.content_generation_needed,
            "findings": self.research_findings,
            "context": self.context
        } 