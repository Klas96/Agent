"""
Registry for all available workflow node types.
This registry manages the discovery and instantiation of workflow nodes.
"""

from typing import Dict, List, Type
from .base import WorkflowNode, WorkflowNodeMetadata
from .triggers import EmailFetchingNode, ScheduledTriggerNode, ManualTriggerNode
from .agents import (
    DecisionAgentNode, ContentCreatorNode, InvestigationNode, 
    MessageSendingNode, PostProcessingNode
)
from .actions import (
    SendEmailWorkflowNode, GenerateContentWorkflowNode, 
    GenerateLatexWorkflowNode, WebSearchWorkflowNode, HttpRequestWorkflowNode
)
from .conditions import IfElseWorkflowNode, TransformWorkflowNode, DelayWorkflowNode, LogWorkflowNode


class WorkflowNodeRegistry:
    """Registry for all available workflow node types."""
    
    def __init__(self):
        self._nodes: Dict[str, Type[WorkflowNode]] = {}
        self._register_default_nodes()
    
    def _register_default_nodes(self):
        """Register all default node types."""
        
        # Trigger nodes
        self.register_node("EmailFetchingNode", EmailFetchingNode)
        self.register_node("ScheduledTriggerNode", ScheduledTriggerNode)
        self.register_node("ManualTriggerNode", ManualTriggerNode)
        
        # Agent nodes (new)
        self.register_node("DecisionAgentNode", DecisionAgentNode)
        self.register_node("ContentCreatorNode", ContentCreatorNode)
        self.register_node("InvestigationNode", InvestigationNode)
        self.register_node("MessageSendingNode", MessageSendingNode)
        self.register_node("PostProcessingNode", PostProcessingNode)
        
        # Action nodes
        self.register_node("SendEmailWorkflowNode", SendEmailWorkflowNode)
        self.register_node("GenerateContentWorkflowNode", GenerateContentWorkflowNode)
        self.register_node("GenerateLatexWorkflowNode", GenerateLatexWorkflowNode)
        self.register_node("WebSearchWorkflowNode", WebSearchWorkflowNode)
        self.register_node("HttpRequestWorkflowNode", HttpRequestWorkflowNode)
        
        # Condition and transform nodes
        self.register_node("IfElseWorkflowNode", IfElseWorkflowNode)
        self.register_node("TransformWorkflowNode", TransformWorkflowNode)
        self.register_node("DelayWorkflowNode", DelayWorkflowNode)
        self.register_node("LogWorkflowNode", LogWorkflowNode)
    
    def register_node(self, node_type: str, node_class: Type[WorkflowNode]):
        """Register a new node type."""
        self._nodes[node_type] = node_class
    
    def get_node_class(self, node_type: str) -> Type[WorkflowNode]:
        """Get a node class by type."""
        if node_type not in self._nodes:
            raise ValueError(f"Unknown node type: {node_type}")
        return self._nodes[node_type]
    
    def create_node(self, node_type: str, config: Dict, name: str = None) -> WorkflowNode:
        """Create a node instance."""
        node_class = self.get_node_class(node_type)
        return node_class(config, name)
    
    def get_all_node_types(self) -> List[str]:
        """Get all registered node types."""
        return list(self._nodes.keys())
    
    def get_node_metadata(self, node_type: str) -> WorkflowNodeMetadata:
        """Get metadata for a specific node type."""
        node_class = self.get_node_class(node_type)
        return node_class.get_metadata()
    
    def get_all_node_metadata(self) -> Dict[str, WorkflowNodeMetadata]:
        """Get metadata for all node types."""
        return {
            node_type: self.get_node_metadata(node_type)
            for node_type in self._nodes.keys()
        }
    
    def get_nodes_by_category(self, category: str) -> List[str]:
        """Get all node types in a specific category."""
        category_nodes = []
        for node_type in self._nodes.keys():
            metadata = self.get_node_metadata(node_type)
            if metadata.category == category:
                category_nodes.append(node_type)
        return category_nodes
    
    def create_pocketflow_node(self, node_type: str, config: Dict, name: str = None):
        """Create a workflow node that can be used in the original PocketFlow system."""
        return self.create_node(node_type, config, name)


# Create global registry instance
workflow_node_registry = WorkflowNodeRegistry() 