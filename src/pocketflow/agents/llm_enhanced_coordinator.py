"""
LLM-Enhanced Coordinator Agent for PocketFlow.

This agent uses LLMs to make intelligent decisions about which agents
should handle different parts of a request, rather than relying on keywords.
"""

from typing import Dict, Any, List, Optional
from ..agents.base_agent import BaseAgent, AgentAction, AgentDecision
from ..core.types import SharedState, FlowType
from ..services import llm_service
from ..utils.logging import get_logger


class LLMEnhancedCoordinatorAgent(BaseAgent):
    """Coordinator agent that uses LLMs for intelligent decision-making."""
    
    def __init__(self):
        super().__init__("LLMCoordinator")
        self.available_agents: Dict[str, BaseAgent] = {}
        self.current_agent: Optional[str] = None
        self.task_complete = False
    
    def register_agent(self, agent: BaseAgent):
        """Register an agent with the coordinator."""
        self.available_agents[agent.name] = agent
        self.logger.info(f"Registered agent: {agent.name}")
    
    def analyze(self, shared: SharedState) -> AgentDecision:
        """Use LLM to analyze the situation and decide which agent should handle it."""
        try:
            # Get user context
            user_email = shared.get("user")
            flow_type = shared.get("flow_type", FlowType.TOKENED_USER)
            email = shared.get("email", {})
            body = email.get("body", "")
            subject = email.get("subject", "")
            
            self.logger.info(f"LLM Coordinator analyzing request from {user_email}")
            
            # Check if we need to start fresh
            if not self.current_agent:
                return self._llm_decide_initial_agent(shared, flow_type, body, subject)
            
            # Check if current agent is done
            if self.task_complete:
                return AgentDecision(
                    action=AgentAction.FINISH,
                    confidence=1.0,
                    reasoning="Task completed successfully",
                    parameters={}
                )
            
            # Let current agent continue or hand off
            return self._continue_or_handoff(shared)
            
        except Exception as e:
            self.logger.error(f"Error in LLM coordinator analysis: {e}")
            return AgentDecision(
                action=AgentAction.FINISH,
                confidence=0.0,
                reasoning=f"Error in analysis: {e}",
                parameters={}
            )
    
    def _llm_decide_initial_agent(self, shared: SharedState, flow_type: FlowType, body: str, subject: str) -> AgentDecision:
        """Use LLM to decide which agent should handle the initial request."""
        
        # All users get the same treatment since tokens are deprecated
        if flow_type == FlowType.USER:
            # Use LLM to analyze the request
            llm_decision = self._ask_llm_for_agent_selection(body, subject, shared)
            
            # Parse LLM response
            agent_name = llm_decision.get("agent")
            reasoning = llm_decision.get("reasoning", "LLM analysis")
            confidence = llm_decision.get("confidence", 0.8)
            action = llm_decision.get("action", "process_with_llm")
            
            # Validate agent exists
            if agent_name and agent_name in self.available_agents:
                self.current_agent = agent_name
                return AgentDecision(
                    action=AgentAction(action),
                    confidence=confidence,
                    reasoning=reasoning,
                    parameters={"agent": agent_name, **llm_decision.get("parameters", {})},
                    next_agent=agent_name
                )
            else:
                # Fallback to email agent
                self.current_agent = "EmailAgent"
                return AgentDecision(
                    action=AgentAction.PROCESS_WITH_LLM,
                    confidence=0.7,
                    reasoning="LLM suggested agent not available, using email agent",
                    parameters={"agent": "EmailAgent"},
                    next_agent="EmailAgent"
                )
        
        # Fallback for any other flow types
        self.current_agent = "EmailAgent"
        return AgentDecision(
            action=AgentAction.PROCESS_WITH_LLM,
            confidence=0.7,
            reasoning="Default to email agent",
            parameters={"agent": "EmailAgent"},
            next_agent="EmailAgent"
        )
    
    def _ask_llm_for_agent_selection(self, body: str, subject: str, shared: SharedState) -> Dict[str, Any]:
        """Ask LLM to analyze the request and suggest the best agent."""
        
        # Create context for LLM
        available_agents = list(self.available_agents.keys())
        user_email = shared.get("user", "")
        
        prompt = f"""
You are an intelligent coordinator for an email processing system. Analyze the user's request and decide which agent should handle it.

Available Agents:
- EmailAgent: General email processing, conversation management, basic responses
- ResearchAgent: Web search, investigation, research tasks, can hand off to content generation
- ContentAgent: Content generation (songs, images, documents), can work with research findings
- PaymentAgent: Bitcoin payment processing, payment requests

User Email: {user_email}
Subject: {subject}
Body: {body}

Please analyze this request and respond with a JSON object containing:
{{
    "agent": "agent_name",
    "action": "action_type",
    "reasoning": "explanation of why this agent is best",
    "confidence": 0.0-1.0,
    "parameters": {{"additional_params": "values"}}
}}

Consider:
1. Does the request require research/investigation?
2. Does the request ask for content generation?
3. Does the request mention payment or tokens?
4. Is this a general email that needs processing?

Respond only with the JSON object.
"""
        
        try:
            # Call LLM
            response = llm_service.call_llm([
                {"role": "system", "content": "You are a helpful coordinator that analyzes requests and suggests the best agent to handle them."},
                {"role": "user", "content": prompt}
            ])
            
            # Parse LLM response
            import json
            try:
                # Try to extract JSON from response
                response_text = response.get("content", "")
                
                # Look for JSON in the response
                start_idx = response_text.find('{')
                end_idx = response_text.rfind('}') + 1
                
                if start_idx != -1 and end_idx > start_idx:
                    json_str = response_text[start_idx:end_idx]
                    decision = json.loads(json_str)
                else:
                    # Fallback parsing
                    decision = self._parse_llm_response_fallback(response_text)
                
                self.logger.info(f"LLM decision: {decision}")
                return decision
                
            except json.JSONDecodeError as e:
                self.logger.warning(f"Failed to parse LLM JSON response: {e}")
                return self._parse_llm_response_fallback(response.get("content", ""))
                
        except Exception as e:
            self.logger.error(f"Error calling LLM for agent selection: {e}")
            return self._fallback_agent_selection(body)
    
    def _parse_llm_response_fallback(self, response_text: str) -> Dict[str, Any]:
        """Fallback parsing for LLM response."""
        response_lower = response_text.lower()
        
        # Simple keyword-based fallback
        if any(word in response_lower for word in ["research", "investigate", "find", "search"]):
            return {
                "agent": "ResearchAgent",
                "action": "investigate",
                "reasoning": "Request requires research/investigation",
                "confidence": 0.8,
                "parameters": {}
            }
        elif any(word in response_lower for word in ["generate", "create", "make", "song", "music", "image", "document"]):
            return {
                "agent": "ContentAgent",
                "action": "generate_content",
                "reasoning": "Request requires content generation",
                "confidence": 0.8,
                "parameters": {}
            }
        else:
            return {
                "agent": "EmailAgent",
                "action": "process_with_llm",
                "reasoning": "General email processing",
                "confidence": 0.7,
                "parameters": {}
            }
    
    def _fallback_agent_selection(self, body: str) -> Dict[str, Any]:
        """Fallback agent selection when LLM fails."""
        body_lower = body.lower()
        
        if any(word in body_lower for word in ["research", "investigate", "find", "search"]):
            return {
                "agent": "ResearchAgent",
                "action": "investigate",
                "reasoning": "Fallback: Request contains research keywords",
                "confidence": 0.7,
                "parameters": {}
            }
        elif any(word in body_lower for word in ["generate", "create", "make", "song", "music", "image"]):
            return {
                "agent": "ContentAgent",
                "action": "generate_content",
                "reasoning": "Fallback: Request contains content generation keywords",
                "confidence": 0.7,
                "parameters": {}
            }
        else:
            return {
                "agent": "EmailAgent",
                "action": "process_with_llm",
                "reasoning": "Fallback: General email processing",
                "confidence": 0.6,
                "parameters": {}
            }
    
    def _continue_or_handoff(self, shared: SharedState) -> AgentDecision:
        """Decide whether to continue with current agent or hand off."""
        
        if not self.current_agent or self.current_agent not in self.available_agents:
            return AgentDecision(
                action=AgentAction.FINISH,
                confidence=0.0,
                reasoning="No current agent available",
                parameters={}
            )
        
        current_agent = self.available_agents[self.current_agent]
        
        # Check if current agent wants to hand off
        agent_decision = current_agent.analyze(shared)
        
        # If agent wants to hand off to another agent
        if agent_decision.next_agent and agent_decision.next_agent in self.available_agents:
            self.current_agent = agent_decision.next_agent
            self.logger.info(f"Handing off from {current_agent.name} to {agent_decision.next_agent}")
            return agent_decision
        
        # If agent is done
        if agent_decision.action == AgentAction.FINISH:
            self.task_complete = True
            return agent_decision
        
        # Continue with current agent
        return agent_decision
    
    def execute(self, action: AgentAction, shared: SharedState, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the action by delegating to the appropriate agent."""
        
        if action == AgentAction.FINISH:
            return {"success": True, "message": "Task completed"}
        
        # Get the target agent
        target_agent_name = parameters.get("agent", self.current_agent)
        if not target_agent_name or target_agent_name not in self.available_agents:
            return {"success": False, "error": f"Agent not found: {target_agent_name}"}
        
        target_agent = self.available_agents[target_agent_name]
        
        # Execute the action
        try:
            result = target_agent.execute(action, shared, parameters)
            self.logger.info(f"Executed {action} with {target_agent_name}: {result}")
            return result
        except Exception as e:
            self.logger.error(f"Error executing {action} with {target_agent_name}: {e}")
            return {"success": False, "error": str(e)}
    
    def get_capabilities(self) -> List[str]:
        """Get LLM coordinator capabilities."""
        return [
            "llm_based_decision_making",
            "intelligent_agent_selection",
            "context_aware_routing",
            "agent_orchestration",
            "workflow_management"
        ]
    
    def reset(self):
        """Reset LLM coordinator state."""
        super().reset()
        self.current_agent = None
        self.task_complete = False
        self.logger.info("LLM Coordinator reset")
    
    def get_workflow_status(self) -> Dict[str, Any]:
        """Get current workflow status."""
        return {
            "current_agent": self.current_agent,
            "task_complete": self.task_complete,
            "available_agents": list(self.available_agents.keys()),
            "context": self.context,
            "history": [decision.action.value for decision in self.history]
        } 