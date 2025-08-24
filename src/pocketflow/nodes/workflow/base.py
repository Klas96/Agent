"""
Workflow node base classes for PocketFlow n8n-like workflow system.
This module provides workflow nodes that build on top of the original PocketFlow Node system.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field

from ...core.node import Node
from ...core.types import SharedState, NodeResult
from ...utils.logging import get_logger


@dataclass
class WorkflowNodeInput:
    """Input definition for a workflow node."""
    name: str
    type: str
    description: str
    required: bool = True
    default: Any = None


@dataclass
class WorkflowNodeOutput:
    """Output definition for a workflow node."""
    name: str
    type: str
    description: str


@dataclass
class WorkflowNodeMetadata:
    """Metadata for a workflow node."""
    name: str
    description: str
    category: str
    version: str = "1.0.0"
    author: str = "PocketFlow"
    inputs: List[WorkflowNodeInput] = field(default_factory=list)
    outputs: List[WorkflowNodeOutput] = field(default_factory=list)
    icon: Optional[str] = None
    color: Optional[str] = None


class WorkflowNode(Node):
    """
    Base class for workflow nodes that build on top of PocketFlow's Node system.
    
    Workflow nodes are designed to work with visual workflow editors and provide
    metadata for UI generation while maintaining compatibility with the original
    PocketFlow execution system.
    """
    
    def __init__(self, config: Dict[str, Any], name: Optional[str] = None):
        super().__init__(name)
        self.config = config
        self.logger = get_logger(f"WorkflowNode.{self.__class__.__name__}")
    
    def prep(self, shared: SharedState) -> Any:
        """Prepare data from shared state and config."""
        # Default implementation: return config and shared state
        return {"config": self.config, "shared": shared}
    
    def exec(self, prep_result: Any) -> Any:
        """Execute the workflow node logic."""
        return self.execute_workflow(prep_result["config"], prep_result["shared"])
    
    def post(self, shared: SharedState, prep_result: Any, exec_result: Any) -> str:
        """Post-process results and update shared state."""
        # Store workflow results in shared state
        workflow_key = f"workflow_{self.name}"
        shared[workflow_key] = {
            "config": self.config,
            "result": exec_result,
            "timestamp": self._get_timestamp()
        }
        
        # Set outputs based on metadata
        self._set_outputs(shared, exec_result)
        
        return "default"
    
    @abstractmethod
    def execute_workflow(self, config: Dict[str, Any], shared: SharedState) -> Dict[str, Any]:
        """Execute the workflow node logic."""
        pass
    
    @classmethod
    def get_metadata(cls) -> WorkflowNodeMetadata:
        """Get metadata for this workflow node."""
        return WorkflowNodeMetadata(
            name=cls.__name__,
            description="Base workflow node",
            category="workflow"
        )
    
    def validate_config(self) -> List[str]:
        """Validate the node configuration."""
        errors = []
        metadata = self.get_metadata()
        
        for input_def in metadata.inputs:
            if input_def.required and input_def.name not in self.config:
                errors.append(f"Required input '{input_def.name}' not found in config")
        
        return errors
    
    def get_input_value(self, name: str, default: Any = None) -> Any:
        """Get an input value from the config."""
        return self.config.get(name, default)
    
    def set_output(self, shared: SharedState, name: str, value: Any):
        """Set an output value in the shared state."""
        output_key = f"workflow_output_{self.name}_{name}"
        shared[output_key] = value
    
    def _set_outputs(self, shared: SharedState, result: Dict[str, Any]):
        """Set outputs based on the execution result."""
        if isinstance(result, dict):
            for key, value in result.items():
                self.set_output(shared, key, value)
    
    def _get_timestamp(self) -> float:
        """Get current timestamp."""
        import time
        return time.time()


class WorkflowTriggerNode(WorkflowNode):
    """Base class for workflow trigger nodes."""
    
    @classmethod
    def get_metadata(cls) -> WorkflowNodeMetadata:
        return WorkflowNodeMetadata(
            name=cls.__name__,
            description="Base workflow trigger node",
            category="trigger"
        )


class WorkflowActionNode(WorkflowNode):
    """Base class for workflow action nodes."""
    
    @classmethod
    def get_metadata(cls) -> WorkflowNodeMetadata:
        return WorkflowNodeMetadata(
            name=cls.__name__,
            description="Base workflow action node",
            category="action"
        )


class WorkflowConditionNode(WorkflowNode):
    """Base class for workflow condition nodes."""
    
    @classmethod
    def get_metadata(cls) -> WorkflowNodeMetadata:
        return WorkflowNodeMetadata(
            name=cls.__name__,
            description="Base workflow condition node",
            category="condition"
        )


class WorkflowTransformNode(WorkflowNode):
    """Base class for workflow transform nodes."""
    
    @classmethod
    def get_metadata(cls) -> WorkflowNodeMetadata:
        return WorkflowNodeMetadata(
            name=cls.__name__,
            description="Base workflow transform node",
            category="transform"
        ) 