"""
Core node abstractions for PocketFlow.

This module defines the base Node class and related abstractions.
"""

import logging
from abc import ABC, abstractmethod
from typing import Any, Optional, Dict
from .types import SharedState, NodeResult
from ..utils.logging import get_logger
from ..utils.errors import NodeError


class Node(ABC):
    """
    Base class for all nodes in PocketFlow.
    
    Each node follows a three-phase execution pattern:
    1. prep: Prepare data from shared state
    2. exec: Execute the main logic
    3. post: Post-process results and update shared state
    """
    
    def __init__(self, name: Optional[str] = None):
        self.name = name or self.__class__.__name__
        self.logger = get_logger(f"node.{self.name}")
    
    def run(self, shared: SharedState) -> NodeResult:
        """
        Execute the node with the given shared state.
        
        Args:
            shared: The shared state passed between nodes
            
        Returns:
            NodeResult containing the execution result
        """
        try:
            self.logger.debug(f"Starting node {self.name}")
            
            # Preparation phase
            prep_result = self.prep(shared)
            if prep_result is None:
                return NodeResult(
                    success=False,
                    error="Node preparation returned None"
                )
            
            # Execution phase
            exec_result = self.exec(prep_result)
            if exec_result is None:
                return NodeResult(
                    success=False,
                    error="Node execution returned None"
                )
            
            # Post-processing phase
            post_result = self.post(shared, prep_result, exec_result)
            
            return NodeResult(
                success=True,
                data=exec_result,
                metadata={"post_result": post_result}
            )
            
        except Exception as e:
            self.logger.error(f"Error in node {self.name}: {str(e)}", exc_info=True)
            # Try fallback if available
            try:
                fallback_result = self.exec_fallback(prep_result, e)
                if fallback_result is not None:
                    return NodeResult(
                        success=True,
                        data=fallback_result,
                        metadata={"fallback": True, "original_error": str(e)}
                    )
            except Exception as fallback_error:
                self.logger.error(f"Fallback also failed for node {self.name}: {str(fallback_error)}")
            
            return NodeResult(
                success=False,
                error=str(e)
            )
    
    def exec_fallback(self, prep_result: Any, exc: Exception) -> Optional[Any]:
        """
        Fallback method called when exec() fails.
        
        Args:
            prep_result: Result from the prep phase
            exc: The exception that caused the failure
            
        Returns:
            Fallback result or None if no fallback is available
        """
        # Default implementation: re-raise the exception
        raise exc
    
    @abstractmethod
    def prep(self, shared: SharedState) -> Any:
        """
        Prepare data for execution.
        
        Args:
            shared: The shared state
            
        Returns:
            Prepared data for execution
        """
        pass
    
    @abstractmethod
    def exec(self, prep_result: Any) -> Any:
        """
        Execute the main logic of the node.
        
        Args:
            prep_result: Result from the prep phase
            
        Returns:
            Execution result
        """
        pass
    
    @abstractmethod
    def post(self, shared: SharedState, prep_result: Any, exec_result: Any) -> str:
        """
        Post-process results and update shared state.
        
        Args:
            shared: The shared state to update
            prep_result: Result from the prep phase
            exec_result: Result from the exec phase
            
        Returns:
            Routing decision (string identifier)
        """
        pass


class SimpleNode(Node):
    """
    A simplified node that combines prep, exec, and post into a single method.
    
    Useful for simple nodes that don't need complex state management.
    """
    
    def prep(self, shared: SharedState) -> SharedState:
        """Return the shared state as-is for simple nodes."""
        return shared
    
    def exec(self, shared: SharedState) -> Any:
        """Execute the main logic."""
        return self.process(shared)
    
    def post(self, shared: SharedState, prep_result: SharedState, exec_result: Any) -> str:
        """Update shared state and return routing decision."""
        if exec_result is not None and isinstance(exec_result, dict):
            # Update shared state attributes based on exec_result
            for key, value in exec_result.items():
                if key != "route" and hasattr(shared, key):
                    setattr(shared, key, value)
            
            # Return the route if specified, otherwise default
            return exec_result.get("route", "default")
        return "default"
    
    @abstractmethod
    def process(self, shared: SharedState) -> Optional[Dict[str, Any]]:
        """
        Process the shared state and return updates.
        
        Args:
            shared: The shared state
            
        Returns:
            Dictionary of updates to apply to shared state, or None
        """
        pass


class ConditionalNode(Node):
    """
    A node that can route to different paths based on conditions.
    """
    
    def __init__(self, name: Optional[str] = None, conditions: Optional[Dict[str, callable]] = None):
        super().__init__(name)
        self.conditions = conditions or {}
    
    def add_condition(self, route: str, condition: callable):
        """Add a routing condition."""
        self.conditions[route] = condition
    
    def post(self, shared: SharedState, prep_result: Any, exec_result: Any) -> str:
        """Route based on conditions."""
        for route, condition in self.conditions.items():
            if condition(shared, prep_result, exec_result):
                return route
        return "default"


class ErrorHandlingNode(Node):
    """
    A node wrapper that provides consistent error handling.
    """
    
    def __init__(self, node: Node, max_retries: int = 3):
        super().__init__(f"ErrorHandling_{node.name}")
        self.node = node
        self.max_retries = max_retries
    
    def prep(self, shared: SharedState) -> Any:
        return self.node.prep(shared)
    
    def exec(self, prep_result: Any) -> Any:
        for attempt in range(self.max_retries):
            try:
                return self.node.exec(prep_result)
            except Exception as e:
                if attempt == self.max_retries - 1:
                    raise
                self.logger.warning(f"Attempt {attempt + 1} failed, retrying: {e}")
    
    def post(self, shared: SharedState, prep_result: Any, exec_result: Any) -> str:
        return self.node.post(shared, prep_result, exec_result) 