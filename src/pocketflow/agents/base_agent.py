"""
Base agent class for PocketFlow.

Provides the foundation for all agentic behavior with dynamic decision making.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

from ..core.types import SharedState
from ..utils.logging import get_logger


class AgentAction(Enum):
    """Types of actions an agent can take."""
    FETCH_EMAIL = "fetch_email"
    SEND_EMAIL = "send_email"
    GET_CONTEXT = "get_context"
    PROCESS_WITH_LLM = "process_with_llm"
    INVESTIGATE = "investigate"
    GENERATE_CONTENT = "generate_content"
    REQUEST_PAYMENT = "request_payment"
    WAIT_FOR_INPUT = "wait_for_input"
    FINISH = "finish"


@dataclass
class AgentDecision:
    """Represents a decision made by an agent."""
    action: AgentAction
    confidence: float
    reasoning: str
    parameters: Dict[str, Any]
    next_agent: Optional[str] = None


class BaseAgent(ABC):
    """Base class for all agents in the system."""
    
    def __init__(self, name: str):
        self.name = name
        self.logger = get_logger(f"Agent.{name}")
        self.context: Dict[str, Any] = {}
        self.history: List[AgentDecision] = []
    
    @abstractmethod
    def analyze(self, shared: SharedState) -> AgentDecision:
        """
        Analyze the current state and decide what action to take.
        
        Args:
            shared: Current shared state
            
        Returns:
            AgentDecision with the chosen action and reasoning
        """
        pass
    
    @abstractmethod
    def execute(self, action: AgentAction, shared: SharedState, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a specific action.
        
        Args:
            action: Action to execute
            shared: Current shared state
            parameters: Action parameters
            
        Returns:
            Execution result
        """
        pass
    
    def can_handle(self, shared: SharedState) -> bool:
        """
        Check if this agent can handle the current situation.
        
        Args:
            shared: Current shared state
            
        Returns:
            True if this agent can handle the situation
        """
        return True
    
    def get_capabilities(self) -> List[str]:
        """Get list of capabilities this agent has."""
        return []
    
    def update_context(self, new_context: Dict[str, Any]):
        """Update agent's internal context."""
        self.context.update(new_context)
        self.logger.debug(f"Updated context: {new_context}")
    
    def add_to_history(self, decision: AgentDecision):
        """Add a decision to the agent's history."""
        self.history.append(decision)
        self.logger.debug(f"Added decision to history: {decision.action}")
    
    def get_history(self) -> List[AgentDecision]:
        """Get the agent's decision history."""
        return self.history.copy()
    
    def reset(self):
        """Reset agent state."""
        self.context.clear()
        self.history.clear()
        self.logger.debug("Agent state reset")
    
    def get_agent_info(self) -> Dict[str, Any]:
        """Get information about this agent."""
        return {
            "name": self.name,
            "capabilities": self.get_capabilities(),
            "context": self.context,
            "history_length": len(self.history)
        } 