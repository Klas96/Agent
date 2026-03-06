"""
Core flow abstractions for PocketFlow.

This module defines the Flow class and related abstractions.
"""

import time
import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Callable, Any
from .node import Node
from .types import SharedState, NodeResult, FlowType, FlowConfig
from ..utils.logging import get_logger


@dataclass
class FlowStep:
    """Represents a step in a flow."""
    name: str
    node: Node
    conditions: Dict[str, Callable] = None
    
    def __post_init__(self):
        if self.conditions is None:
            self.conditions = {}


class Flow:
    """
    A flow represents a sequence of nodes with routing logic.
    
    The flow engine executes nodes in sequence and routes between them
    based on the results of each node's execution.
    """
    
    def __init__(self, name: str, config: Optional[FlowConfig] = None):
        self.name = name
        self.config = config or FlowConfig(
            name=name,
            nodes=[],
            flow_type=FlowType.TOKENED_USER,
            requires_tokens=True,
            timeout=900  # Default 15 minutes timeout
        )
        self.steps: Dict[str, FlowStep] = {}
        self.routing: Dict[str, Dict[str, str]] = {}
        self.logger = get_logger(f"pocketflow.flow.{name}")
        self.start_step: Optional[str] = None
        self.end_steps: List[str] = []
        
    def add_step(self, name: str, node: Node, conditions: Optional[Dict[str, Callable]] = None) -> 'Flow':
        """Add a step to the flow."""
        self.steps[name] = FlowStep(name=name, node=node, conditions=conditions or {})
        return self
    
    def set_start(self, step_name: str) -> 'Flow':
        """Set the starting step of the flow."""
        if step_name not in self.steps:
            raise ValueError(f"Step '{step_name}' not found in flow")
        self.start_step = step_name
        return self
    
    def add_end_step(self, step_name: str) -> 'Flow':
        """Add an end step to the flow."""
        if step_name not in self.steps:
            raise ValueError(f"Step '{step_name}' not found in flow")
        self.end_steps.append(step_name)
        return self
    
    def add_routing(self, from_step: str, condition: str, to_step: str) -> 'Flow':
        """Add routing from one step to another based on a condition."""
        if from_step not in self.steps:
            raise ValueError(f"From step '{from_step}' not found in flow")
        if to_step not in self.steps:
            raise ValueError(f"To step '{to_step}' not found in flow")
        
        if from_step not in self.routing:
            self.routing[from_step] = {}
        self.routing[from_step][condition] = to_step
        return self
    
    def validate(self) -> bool:
        """Validate the flow configuration."""
        if not self.start_step:
            self.logger.error("No start step defined")
            return False
        
        if not self.end_steps:
            self.logger.error("No end steps defined")
            return False
        
        # Check for unreachable steps
        reachable = {self.start_step}
        to_check = [self.start_step]
        
        while to_check:
            current = to_check.pop(0)
            if current in self.routing:
                for next_step in self.routing[current].values():
                    if next_step not in reachable:
                        reachable.add(next_step)
                        to_check.append(next_step)
        
        unreachable = set(self.steps.keys()) - reachable
        if unreachable:
            self.logger.warning(f"Unreachable steps: {unreachable}")
        
        return True
    
    def run(self, shared: SharedState) -> NodeResult:
        """
        Execute the flow with the given shared state.
        
        Args:
            shared: The shared state to pass between nodes
            
        Returns:
            NodeResult containing the final result
        """
        if not self.validate():
            # Try to send guaranteed response even if validation fails
            return self._try_guaranteed_response(shared, "Flow validation failed")
        
        # Set flow type in shared state
        shared.flow_type = self.config.flow_type.value
        
        start_time = time.time()
        current_step = self.start_step
        step_count = 0
        last_error = None
        
        try:
            while current_step and step_count < 100:  # Prevent infinite loops
                step_count += 1
                
                # Check timeout (default to 900 seconds if not set)
                timeout = self.config.timeout if self.config.timeout is not None else 900
                if time.time() - start_time > timeout:
                    error_msg = f"Flow timeout after {timeout} seconds"
                    self.logger.error(error_msg)
                    return self._try_guaranteed_response(shared, error_msg)
                
                # Execute current step
                step = self.steps[current_step]
                self.logger.info(f"=== Executing step: {current_step} ===")
                result = step.node.run(shared)
                post_result = result.metadata.get("post_result", "default")
                self.logger.info(f"=== Step: {current_step}, post_result/route: {post_result} ===")
                
                if not result.success:
                    self.logger.error(f"Step {current_step} failed: {result.error}")
                    last_error = result.error
                    # Store error in shared state for guaranteed response node
                    shared.last_error = result.error
                    # Try to route to guaranteed response if available
                    if "guaranteed_response" in self.steps:
                        self.logger.info("Routing to guaranteed response node due to step failure")
                        current_step = "guaranteed_response"
                        continue
                    # Otherwise try guaranteed response and return
                    return self._try_guaranteed_response(shared, result.error)
                
                # Determine next step
                next_step = self._determine_next_step(current_step, result)
                self.logger.info(f"=== Step: {current_step}, next_step: {next_step} ===")
                
                if next_step in self.end_steps:
                    self.logger.info(f"Flow completed at end step: {next_step}")
                    # Check if response was sent before finishing
                    response_sent = getattr(shared, 'sender_have_gotten_response', False)
                    if not response_sent and "guaranteed_response" in self.steps:
                        self.logger.warning("Flow ending without response sent, routing to guaranteed response")
                        current_step = "guaranteed_response"
                        continue
                    return NodeResult(
                        success=True,
                        data=result.data,
                        metadata={"final_step": next_step, "total_steps": step_count}
                    )
                
                current_step = next_step
                
            error_msg = f"Flow exceeded maximum steps ({step_count})"
            self.logger.error(error_msg)
            return self._try_guaranteed_response(shared, error_msg)
            
        except Exception as e:
            self.logger.error(f"Flow execution error: {str(e)}", exc_info=True)
            shared.last_error = str(e)
            return self._try_guaranteed_response(shared, str(e))
    
    def _try_guaranteed_response(self, shared: SharedState, error: str) -> NodeResult:
        """
        Attempt to send a guaranteed response before returning error.
        
        This method tries to find and execute a guaranteed_response node
        to ensure the user receives a response even if the flow failed.
        """
        if "guaranteed_response" in self.steps:
            try:
                self.logger.info("Attempting to send guaranteed response")
                guaranteed_step = self.steps["guaranteed_response"]
                result = guaranteed_step.node.run(shared)
                
                if result.success:
                    self.logger.info("Guaranteed response sent successfully")
                    return NodeResult(
                        success=True,
                        data=result.data,
                        metadata={"guaranteed_response": True, "original_error": error}
                    )
                else:
                    self.logger.error(f"Guaranteed response also failed: {result.error}")
                    return NodeResult(
                        success=False,
                        error=f"Flow failed: {error}. Guaranteed response also failed: {result.error}"
                    )
            except Exception as e:
                self.logger.error(f"Exception while trying guaranteed response: {e}", exc_info=True)
                return NodeResult(
                    success=False,
                    error=f"Flow failed: {error}. Guaranteed response exception: {str(e)}"
                )
        else:
            self.logger.warning("No guaranteed_response node found, cannot send fallback response")
            return NodeResult(
                success=False,
                error=error
            )
    
    def _determine_next_step(self, current_step: str, result: NodeResult) -> Optional[str]:
        """Determine the next step based on the current step's result."""
        if current_step not in self.routing:
            return None
        
        routing_rules = self.routing[current_step]
        
        # Check for specific routing based on post_result
        post_result = result.metadata.get("post_result", "default")
        if post_result in routing_rules:
            return routing_rules[post_result]
        
        # Check for default routing
        if "default" in routing_rules:
            return routing_rules["default"]
        
        return None
    
    def get_execution_path(self) -> List[str]:
        """Get the execution path of the flow."""
        path = []
        current = self.start_step
        
        while current and current not in path:
            path.append(current)
            if current in self.routing:
                # Take the first available route
                routes = self.routing[current]
                if "default" in routes:
                    current = routes["default"]
                elif routes:
                    current = list(routes.values())[0]
                else:
                    current = None
            else:
                current = None
        
        return path


class FlowRouter:
    """
    Routes to different flows based on user token status and other conditions.
    """
    
    def __init__(self):
        self.flows: Dict[str, Flow] = {}
        self.logger = get_logger("pocketflow.router")
    
    def register_flow(self, flow: Flow):
        """Register a flow with the router."""
        self.flows[flow.name] = flow
        self.logger.info(f"Registered flow: {flow.name} (type: {flow.config.flow_type})")
    
    def select_flow(self, shared: SharedState) -> Optional[Flow]:
        """
        Select the appropriate flow based on user state.
        
        Args:
            shared: The shared state containing user information
            
        Returns:
            The selected flow or None if no suitable flow found
        """
        user_has_tokens = shared.get("user_has_tokens", False)
        tokens_remaining = shared.get("tokens_remaining", 0)
        
        self.logger.info(f"Selecting flow for user. Has tokens: {user_has_tokens}, Remaining: {tokens_remaining}")
        
        # All users get the same flow type
        flow_type = FlowType.USER
        
        # Find a flow that matches the requirements
        for flow in self.flows.values():
            if flow.config.flow_type == flow_type:
                return flow
        
        self.logger.warning(f"No suitable flow found for type: {flow_type}")
        return None
    
    def run_appropriate_flow(self, shared: SharedState) -> NodeResult:
        """
        Select and run the appropriate flow for the user.
        
        Args:
            shared: The shared state
            
        Returns:
            NodeResult from the executed flow
        """
        flow = self.select_flow(shared)
        if not flow:
            return NodeResult(
                success=False,
                error="No suitable flow found for user state"
            )
        
        self.logger.info(f"Executing flow: {flow.name}")
        return flow.run(shared)


class FlowBuilder:
    """Builder pattern for creating flows."""
    
    def __init__(self, name: str, flow_type: FlowType = FlowType.USER, requires_tokens: bool = False):
        self.flow = Flow(name, FlowConfig(
            name=name,
            nodes=[],
            flow_type=flow_type,
            requires_tokens=requires_tokens,
            timeout=900  # 15 minutes default timeout (to allow for slow LLM calls)
        ))
    
    def add_step(self, name: str, node: Node, conditions: Optional[Dict[str, Callable]] = None) -> 'FlowBuilder':
        """Add a step to the flow."""
        self.flow.add_step(name, node, conditions)
        return self
    
    def set_start(self, step_name: str) -> 'FlowBuilder':
        """Set the starting step."""
        self.flow.set_start(step_name)
        return self
    
    def add_end_step(self, step_name: str) -> 'FlowBuilder':
        """Add an end step."""
        self.flow.add_end_step(step_name)
        return self
    
    def add_routing(self, from_step: str, condition: str, to_step: str) -> 'FlowBuilder':
        """Add routing between steps."""
        self.flow.add_routing(from_step, condition, to_step)
        return self
    
    def build(self) -> Flow:
        """Build and return the flow."""
        if not self.flow.validate():
            raise ValueError("Flow validation failed")
        return self.flow


def create_flow(name: str, flow_type: FlowType = FlowType.USER, requires_tokens: bool = False) -> FlowBuilder:
    """Create a new flow builder."""
    return FlowBuilder(name, flow_type, requires_tokens) 