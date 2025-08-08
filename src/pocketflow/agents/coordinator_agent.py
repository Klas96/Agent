"""
Coordinator agent for PocketFlow.

This agent orchestrates other agents and makes high-level decisions about
which agents should handle different parts of a request.
"""

from typing import Dict, Any, List, Optional
from ..agents.base_agent import BaseAgent, AgentAction, AgentDecision
from ..core.types import SharedState, FlowType
from ..utils.logging import get_logger


class CoordinatorAgent(BaseAgent):
    """Main coordinator agent that orchestrates other agents."""
    
    def __init__(self):
        super().__init__("Coordinator")
        self.available_agents: Dict[str, BaseAgent] = {}
        self.current_agent: Optional[str] = None
        self.task_complete = False
    
    def register_agent(self, agent: BaseAgent):
        """Register an agent with the coordinator."""
        self.available_agents[agent.name] = agent
        self.logger.info(f"Registered agent: {agent.name}")
    
    def analyze(self, shared: SharedState) -> AgentDecision:
        """Analyze the situation and decide which agent should handle it."""
        try:
            # Get user context
            user_email = shared.get("user")
            flow_type = shared.get("flow_type", FlowType.TOKENED_USER)
            email = shared.get("email", {})
            body = email.get("body", "").lower()
            
            self.logger.info(f"Coordinator analyzing request from {user_email}")
            
            # Check if we need to start fresh
            if not self.current_agent:
                return self._decide_initial_agent(shared, flow_type, body)
            
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
            self.logger.error(f"Error in coordinator analysis: {e}")
            return AgentDecision(
                action=AgentAction.FINISH,
                confidence=0.0,
                reasoning=f"Error in analysis: {e}",
                parameters={}
            )
    
    def _decide_initial_agent(self, shared: SharedState, flow_type: FlowType, body: str) -> AgentDecision:
        """Decide which agent should handle the initial request."""
        
        # All users get the same treatment since tokens are deprecated
        if flow_type == FlowType.USER:
            # Check for investigation needs
            investigation_keywords = ["research", "investigate", "find", "search", "what is", "how to", "latest", "current"]
            if any(keyword in body for keyword in investigation_keywords):
                self.current_agent = "ResearchAgent"
                return AgentDecision(
                    action=AgentAction.INVESTIGATE,
                    confidence=0.9,
                    reasoning="Request requires investigation",
                    parameters={"agent": "ResearchAgent", "topic": body},
                    next_agent="ResearchAgent"
                )
            
            # Check for content generation
            content_keywords = ["generate", "create", "make", "song", "music", "image", "document", "write"]
            if any(keyword in body for keyword in content_keywords):
                self.current_agent = "ContentAgent"
                return AgentDecision(
                    action=AgentAction.GENERATE_CONTENT,
                    confidence=0.9,
                    reasoning="Request requires content generation",
                    parameters={"agent": "ContentAgent", "content_type": "auto_detect"},
                    next_agent="ContentAgent"
                )
            
            # Default to email agent for general processing
            self.current_agent = "EmailAgent"
            return AgentDecision(
                action=AgentAction.PROCESS_WITH_LLM,
                confidence=0.8,
                reasoning="General email processing",
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
        """Get coordinator capabilities."""
        return [
            "agent_orchestration",
            "task_delegation",
            "workflow_management",
            "agent_selection",
            "context_management"
        ]
    
    def reset(self):
        """Reset coordinator state."""
        super().reset()
        self.current_agent = None
        self.task_complete = False
        self.logger.info("Coordinator reset")
    
    def get_workflow_status(self) -> Dict[str, Any]:
        """Get current workflow status."""
        return {
            "current_agent": self.current_agent,
            "task_complete": self.task_complete,
            "available_agents": list(self.available_agents.keys()),
            "context": self.context,
            "history": [decision.action.value for decision in self.history]
        } 