"""
Workflow engine for PocketFlow n8n-like automation platform.

This module provides the core workflow execution engine that supports
node-based workflows with triggers, actions, and conditional logic.
"""

import json
import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable
from enum import Enum
from pathlib import Path

from .types import SharedState
from ..utils.logging import get_logger


class NodeType(Enum):
    """Types of nodes in the workflow system."""
    TRIGGER = "trigger"
    ACTION = "action"
    CONDITION = "condition"
    TRANSFORM = "transform"


class ExecutionStatus(Enum):
    """Workflow execution status."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class NodeConfig:
    """Configuration for a workflow node."""
    id: str
    type: str
    name: str
    position: Dict[str, int] = field(default_factory=dict)  # x, y coordinates
    data: Dict[str, Any] = field(default_factory=dict)  # Node-specific configuration
    inputs: List[str] = field(default_factory=list)
    outputs: List[str] = field(default_factory=list)


@dataclass
class Edge:
    """Connection between nodes in a workflow."""
    id: str
    source: str  # Source node ID
    target: str  # Target node ID
    source_handle: Optional[str] = None  # Source output handle
    target_handle: Optional[str] = None  # Target input handle
    condition: Optional[str] = None  # Conditional logic for the edge


@dataclass
class WorkflowDefinition:
    """Complete workflow definition."""
    id: str
    name: str
    description: Optional[str] = None
    nodes: List[NodeConfig] = field(default_factory=list)
    edges: List[Edge] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)


@dataclass
class ExecutionResult:
    """Result of a workflow execution."""
    execution_id: str
    workflow_id: str
    status: ExecutionStatus
    start_time: float
    end_time: Optional[float] = None
    node_results: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None
    logs: List[str] = field(default_factory=list)


class WorkflowEngine:
    """
    Core workflow execution engine.
    
    Supports node-based workflows with triggers, actions, and conditional logic.
    """
    
    def __init__(self):
        self.logger = get_logger("WorkflowEngine")
        self.node_registry: Dict[str, Callable] = {}
        self.execution_history: Dict[str, ExecutionResult] = {}
        
    def register_node(self, node_type: str, node_class: Callable):
        """Register a node type with the workflow engine."""
        self.node_registry[node_type] = node_class
        self.logger.info(f"Registered node type: {node_type}")
    
    def create_workflow(self, name: str, description: Optional[str] = None) -> WorkflowDefinition:
        """Create a new workflow definition."""
        workflow = WorkflowDefinition(
            id=str(uuid.uuid4()),
            name=name,
            description=description
        )
        return workflow
    
    def add_node(self, workflow: WorkflowDefinition, node_type: str, name: str, 
                 position: Dict[str, int], data: Dict[str, Any] = None) -> str:
        """Add a node to a workflow."""
        node_id = str(uuid.uuid4())
        node = NodeConfig(
            id=node_id,
            type=node_type,
            name=name,
            position=position,
            data=data or {}
        )
        workflow.nodes.append(node)
        workflow.updated_at = time.time()
        return node_id
    
    def add_edge(self, workflow: WorkflowDefinition, source: str, target: str,
                 source_handle: Optional[str] = None, target_handle: Optional[str] = None,
                 condition: Optional[str] = None) -> str:
        """Add an edge between nodes in a workflow."""
        edge_id = str(uuid.uuid4())
        edge = Edge(
            id=edge_id,
            source=source,
            target=target,
            source_handle=source_handle,
            target_handle=target_handle,
            condition=condition
        )
        workflow.edges.append(edge)
        workflow.updated_at = time.time()
        return edge_id
    
    def validate_workflow(self, workflow: WorkflowDefinition) -> List[str]:
        """Validate a workflow definition and return any errors."""
        errors = []
        
        # Check if workflow has nodes
        if not workflow.nodes:
            errors.append("Workflow must have at least one node")
        
        # Check if all node types are registered
        for node in workflow.nodes:
            if node.type not in self.node_registry:
                errors.append(f"Unknown node type: {node.type}")
        
        # Check for cycles in the graph
        if self._has_cycles(workflow):
            errors.append("Workflow contains cycles")
        
        # Check for unreachable nodes
        unreachable = self._find_unreachable_nodes(workflow)
        if unreachable:
            errors.append(f"Unreachable nodes: {', '.join(unreachable)}")
        
        return errors
    
    def _has_cycles(self, workflow: WorkflowDefinition) -> bool:
        """Check if the workflow graph has cycles."""
        visited = set()
        rec_stack = set()
        
        def dfs(node_id: str) -> bool:
            if node_id in rec_stack:
                return True
            if node_id in visited:
                return False
            
            visited.add(node_id)
            rec_stack.add(node_id)
            
            # Find all edges from this node
            for edge in workflow.edges:
                if edge.source == node_id:
                    if dfs(edge.target):
                        return True
            
            rec_stack.remove(node_id)
            return False
        
        # Check each node
        for node in workflow.nodes:
            if node.id not in visited:
                if dfs(node.id):
                    return True
        
        return False
    
    def _find_unreachable_nodes(self, workflow: WorkflowDefinition) -> List[str]:
        """Find nodes that are not reachable from any trigger node."""
        # Find trigger nodes (nodes with no incoming edges)
        trigger_nodes = set()
        for node in workflow.nodes:
            if node.type.endswith("Trigger"):
                trigger_nodes.add(node.id)
        
        # If no trigger nodes, all nodes are unreachable
        if not trigger_nodes:
            return [node.id for node in workflow.nodes]
        
        # Find all reachable nodes from trigger nodes
        reachable = set()
        to_visit = list(trigger_nodes)
        
        while to_visit:
            current = to_visit.pop(0)
            if current in reachable:
                continue
            
            reachable.add(current)
            
            # Add all nodes that this node connects to
            for edge in workflow.edges:
                if edge.source == current:
                    to_visit.append(edge.target)
        
        # Return unreachable nodes
        all_nodes = {node.id for node in workflow.nodes}
        return list(all_nodes - reachable)
    
    def execute_workflow(self, workflow: WorkflowDefinition, initial_data: Dict[str, Any] = None) -> ExecutionResult:
        """Execute a workflow and return the execution result."""
        execution_id = str(uuid.uuid4())
        start_time = time.time()
        
        result = ExecutionResult(
            execution_id=execution_id,
            workflow_id=workflow.id,
            status=ExecutionStatus.RUNNING,
            start_time=start_time
        )
        
        self.execution_history[execution_id] = result
        
        try:
            self.logger.info(f"Starting workflow execution: {workflow.name} (ID: {execution_id})")
            
            # Validate workflow before execution
            errors = self.validate_workflow(workflow)
            if errors:
                raise ValueError(f"Workflow validation failed: {'; '.join(errors)}")
            
            # Initialize shared state
            shared = SharedState()
            if initial_data:
                shared.update(initial_data)
            
            # Find trigger nodes
            trigger_nodes = [node for node in workflow.nodes if node.type.endswith("Trigger")]
            if not trigger_nodes:
                raise ValueError("No trigger nodes found in workflow")
            
            # Execute trigger nodes first
            for trigger_node in trigger_nodes:
                node_result = self._execute_node(trigger_node, shared, result)
                result.node_results[trigger_node.id] = node_result
            
            # Execute remaining nodes in topological order
            execution_order = self._get_execution_order(workflow)
            
            for node_id in execution_order:
                if node_id in [node.id for node in trigger_nodes]:
                    continue  # Already executed
                
                node = next(n for n in workflow.nodes if n.id == node_id)
                node_result = self._execute_node(node, shared, result)
                result.node_results[node_id] = node_result
                
                # Check if execution should stop
                if node_result.get("stop_execution", False):
                    break
            
            result.status = ExecutionStatus.COMPLETED
            result.end_time = time.time()
            
            self.logger.info(f"Workflow execution completed: {workflow.name} (ID: {execution_id})")
            
        except Exception as e:
            result.status = ExecutionStatus.FAILED
            result.error = str(e)
            result.end_time = time.time()
            self.logger.error(f"Workflow execution failed: {workflow.name} (ID: {execution_id}): {e}")
        
        return result
    
    def _execute_node(self, node: NodeConfig, shared: SharedState, result: ExecutionResult) -> Dict[str, Any]:
        """Execute a single node."""
        try:
            self.logger.info(f"Executing node: {node.name} (Type: {node.type})")
            
            if node.type not in self.node_registry:
                raise ValueError(f"Unknown node type: {node.type}")
            
            node_class = self.node_registry[node.type]
            node_instance = node_class(node.data)
            
            # Execute the node
            node_result = node_instance.execute(shared)
            
            self.logger.info(f"Node execution completed: {node.name}")
            return node_result
            
        except Exception as e:
            self.logger.error(f"Node execution failed: {node.name}: {e}")
            result.logs.append(f"ERROR: {node.name} - {e}")
            raise
    
    def _get_execution_order(self, workflow: WorkflowDefinition) -> List[str]:
        """Get the topological order of nodes for execution."""
        # Build adjacency list
        graph = {node.id: [] for node in workflow.nodes}
        in_degree = {node.id: 0 for node in workflow.nodes}
        
        for edge in workflow.edges:
            graph[edge.source].append(edge.target)
            in_degree[edge.target] += 1
        
        # Topological sort
        queue = [node_id for node_id, degree in in_degree.items() if degree == 0]
        order = []
        
        while queue:
            current = queue.pop(0)
            order.append(current)
            
            for neighbor in graph[current]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)
        
        return order
    
    def get_execution_result(self, execution_id: str) -> Optional[ExecutionResult]:
        """Get the result of a specific execution."""
        return self.execution_history.get(execution_id)
    
    def get_workflow_executions(self, workflow_id: str) -> List[ExecutionResult]:
        """Get all executions for a specific workflow."""
        return [result for result in self.execution_history.values() if result.workflow_id == workflow_id]
    
    def export_workflow(self, workflow: WorkflowDefinition) -> str:
        """Export workflow to JSON string."""
        workflow_dict = {
            "id": workflow.id,
            "name": workflow.name,
            "description": workflow.description,
            "nodes": [
                {
                    "id": node.id,
                    "type": node.type,
                    "name": node.name,
                    "position": node.position,
                    "data": node.data
                }
                for node in workflow.nodes
            ],
            "edges": [
                {
                    "id": edge.id,
                    "source": edge.source,
                    "target": edge.target,
                    "sourceHandle": edge.source_handle,
                    "targetHandle": edge.target_handle,
                    "condition": edge.condition
                }
                for edge in workflow.edges
            ],
            "metadata": workflow.metadata,
            "createdAt": workflow.created_at,
            "updatedAt": workflow.updated_at
        }
        return json.dumps(workflow_dict, indent=2)
    
    def import_workflow(self, workflow_json: str) -> WorkflowDefinition:
        """Import workflow from JSON string."""
        workflow_dict = json.loads(workflow_json)
        
        workflow = WorkflowDefinition(
            id=workflow_dict.get("id", str(uuid.uuid4())),
            name=workflow_dict["name"],
            description=workflow_dict.get("description")
        )
        
        # Import nodes
        for node_dict in workflow_dict.get("nodes", []):
            node = NodeConfig(
                id=node_dict["id"],
                type=node_dict["type"],
                name=node_dict["name"],
                position=node_dict.get("position", {}),
                data=node_dict.get("data", {})
            )
            workflow.nodes.append(node)
        
        # Import edges
        for edge_dict in workflow_dict.get("edges", []):
            edge = Edge(
                id=edge_dict["id"],
                source=edge_dict["source"],
                target=edge_dict["target"],
                source_handle=edge_dict.get("sourceHandle"),
                target_handle=edge_dict.get("targetHandle"),
                condition=edge_dict.get("condition")
            )
            workflow.edges.append(edge)
        
        workflow.metadata = workflow_dict.get("metadata", {})
        workflow.created_at = workflow_dict.get("createdAt", time.time())
        workflow.updated_at = workflow_dict.get("updatedAt", time.time())
        
        return workflow


# Global workflow engine instance
workflow_engine = WorkflowEngine() 