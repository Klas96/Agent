"""
Workflow engine for PocketFlow n8n-like workflow system.
This module provides a workflow engine that builds on top of the original PocketFlow Flow system.
"""

import json
import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from datetime import datetime

from .flow import Flow, FlowBuilder, FlowConfig
from .types import SharedState, FlowType, NodeResult
from ..nodes.workflow.registry import WorkflowNodeRegistry
from ..utils.logging import get_logger


@dataclass
class WorkflowDefinition:
    """Definition of a visual workflow."""
    id: str
    name: str
    description: Optional[str] = None
    nodes: List[Dict[str, Any]] = field(default_factory=list)
    edges: List[Dict[str, Any]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)


@dataclass
class WorkflowExecutionResult:
    """Result of a workflow execution."""
    execution_id: str
    workflow_id: str
    status: str  # "success", "failed", "running"
    start_time: float
    end_time: Optional[float] = None
    node_results: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None
    logs: List[str] = field(default_factory=list)
    initial_data: Dict[str, Any] = field(default_factory=dict)


class WorkflowEngine:
    """
    Workflow engine that converts visual workflows to PocketFlow flows.
    
    This engine takes n8n-like workflow definitions and converts them to
    the original PocketFlow Flow system for execution.
    """
    
    def __init__(self):
        self.logger = get_logger("WorkflowEngine")
        self.workflow_registry = WorkflowNodeRegistry()
        self.execution_history: Dict[str, WorkflowExecutionResult] = {}
    
    def create_workflow(self, name: str, description: Optional[str] = None) -> WorkflowDefinition:
        """Create a new workflow definition."""
        workflow_id = str(uuid.uuid4())
        return WorkflowDefinition(
            id=workflow_id,
            name=name,
            description=description
        )
    
    def add_node(self, workflow: WorkflowDefinition, node_type: str, name: str,
                 position: Dict[str, int], data: Dict[str, Any] = None) -> str:
        """Add a node to the workflow."""
        node_id = str(uuid.uuid4())
        node_data = {
            "id": node_id,
            "type": node_type,
            "name": name,
            "position": position,
            "data": data or {}
        }
        workflow.nodes.append(node_data)
        workflow.updated_at = time.time()
        return node_id
    
    def add_edge(self, workflow: WorkflowDefinition, source: str, target: str,
                 source_handle: Optional[str] = None, target_handle: Optional[str] = None,
                 condition: Optional[str] = None) -> str:
        """Add an edge between nodes."""
        edge_id = str(uuid.uuid4())
        edge_data = {
            "id": edge_id,
            "source": source,
            "target": target,
            "sourceHandle": source_handle,
            "targetHandle": target_handle,
            "condition": condition
        }
        workflow.edges.append(edge_data)
        workflow.updated_at = time.time()
        return edge_id
    
    def validate_workflow(self, workflow: WorkflowDefinition) -> List[str]:
        """Validate a workflow definition."""
        errors = []
        
        if not workflow.nodes:
            errors.append("Workflow must have at least one node")
            return errors
        
        # Check for cycles
        if self._has_cycles(workflow):
            errors.append("Workflow contains cycles")
        
        # Check for unreachable nodes
        unreachable = self._find_unreachable_nodes(workflow)
        if unreachable:
            errors.append(f"Unreachable nodes: {unreachable}")
        
        # Validate node types
        for node in workflow.nodes:
            node_type = node.get("type")
            if not node_type:
                errors.append(f"Node {node.get('id')} missing type")
                continue
            
            try:
                self.workflow_registry.get_node_class(node_type)
            except ValueError:
                errors.append(f"Unknown node type: {node_type}")
        
        return errors
    
    def _has_cycles(self, workflow: WorkflowDefinition) -> bool:
        """Check if the workflow has cycles."""
        # Simple cycle detection using DFS
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
                if edge["source"] == node_id:
                    if dfs(edge["target"]):
                        return True
            
            rec_stack.remove(node_id)
            return False
        
        # Check all nodes
        for node in workflow.nodes:
            if node["id"] not in visited:
                if dfs(node["id"]):
                    return True
        
        return False
    
    def _find_unreachable_nodes(self, workflow: WorkflowDefinition) -> List[str]:
        """Find nodes that are not reachable from any trigger node."""
        # Find trigger nodes (nodes with no incoming edges)
        trigger_nodes = set()
        target_nodes = set()
        
        for edge in workflow.edges:
            target_nodes.add(edge["target"])
        
        for node in workflow.nodes:
            if node["id"] not in target_nodes:
                trigger_nodes.add(node["id"])
        
        if not trigger_nodes:
            return [node["id"] for node in workflow.nodes]
        
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
                if edge["source"] == current:
                    to_visit.append(edge["target"])
        
        # Return unreachable nodes
        all_nodes = {node["id"] for node in workflow.nodes}
        return list(all_nodes - reachable)
    
    def execute_workflow(self, workflow: WorkflowDefinition, initial_data: Dict[str, Any] = None) -> WorkflowExecutionResult:
        """Execute a workflow by converting it to a PocketFlow flow."""
        execution_id = str(uuid.uuid4())
        start_time = time.time()
        
        result = WorkflowExecutionResult(
            execution_id=execution_id,
            workflow_id=workflow.id,
            status="running",
            start_time=start_time,
            initial_data=initial_data or {}
        )
        
        try:
            # Validate workflow
            errors = self.validate_workflow(workflow)
            if errors:
                result.status = "failed"
                result.error = f"Workflow validation failed: {', '.join(errors)}"
                return result
            
            # Convert workflow to PocketFlow flow
            flow = self._convert_to_pocketflow_flow(workflow)
            
            # Create shared state
            shared = SharedState()
            if initial_data:
                shared.update(initial_data)
            
            # Execute the flow
            flow_result = flow.run(shared)
            
            # Record results
            result.end_time = time.time()
            if flow_result.success:
                result.status = "success"
                result.node_results = {
                    "final_result": flow_result.data,
                    "metadata": flow_result.metadata
                }
            else:
                result.status = "failed"
                result.error = flow_result.error
            
            # Store execution result
            self.execution_history[execution_id] = result
            
            return result
            
        except Exception as e:
            result.status = "failed"
            result.error = str(e)
            result.end_time = time.time()
            self.execution_history[execution_id] = result
            return result
    
    def _convert_to_pocketflow_flow(self, workflow: WorkflowDefinition) -> Flow:
        """Convert a workflow definition to a PocketFlow flow."""
        # Create flow builder
        flow_builder = FlowBuilder(
            name=workflow.name,
            flow_type=FlowType.USER,
            requires_tokens=False
        )
        
        # Create node instances
        node_instances = {}
        for node_data in workflow.nodes:
            node_id = node_data["id"]
            node_type = node_data["type"]
            node_name = node_data["name"]
            node_config = node_data.get("data", {})
            
            # Create workflow node
            workflow_node = self.workflow_registry.create_node(
                node_type, node_config, node_name
            )
            
            node_instances[node_id] = workflow_node
        
        # Add nodes to flow
        for node_id, node in node_instances.items():
            flow_builder.add_step(node_id, node)
        
        # Set start node (first trigger node or first node)
        start_node = None
        for node_data in workflow.nodes:
            if node_data["type"].endswith("Trigger"):
                start_node = node_data["id"]
                break
        
        if not start_node and workflow.nodes:
            start_node = workflow.nodes[0]["id"]
        
        if start_node:
            flow_builder.set_start(start_node)
        
        # Add routing based on edges
        for edge in workflow.edges:
            source = edge["source"]
            target = edge["target"]
            condition = edge.get("condition", "default")
            
            flow_builder.add_routing(source, condition, target)
        
        # Add end steps (nodes with no outgoing edges)
        target_nodes = {edge["target"] for edge in workflow.edges}
        for node_data in workflow.nodes:
            if node_data["id"] not in target_nodes:
                flow_builder.add_end_step(node_data["id"])
        
        return flow_builder.build()
    
    def get_execution_result(self, execution_id: str) -> Optional[WorkflowExecutionResult]:
        """Get the result of a workflow execution."""
        return self.execution_history.get(execution_id)
    
    def get_workflow_executions(self, workflow_id: str) -> List[WorkflowExecutionResult]:
        """Get all executions of a workflow."""
        return [
            result for result in self.execution_history.values()
            if result.workflow_id == workflow_id
        ]
    
    def export_workflow(self, workflow: WorkflowDefinition) -> str:
        """Export a workflow to JSON."""
        workflow_dict = {
            "id": workflow.id,
            "name": workflow.name,
            "description": workflow.description,
            "nodes": workflow.nodes,
            "edges": workflow.edges,
            "metadata": workflow.metadata,
            "createdAt": workflow.created_at,
            "updatedAt": workflow.updated_at
        }
        return json.dumps(workflow_dict, indent=2)
    
    def import_workflow(self, workflow_json: str) -> WorkflowDefinition:
        """Import a workflow from JSON."""
        workflow_dict = json.loads(workflow_json)
        
        return WorkflowDefinition(
            id=workflow_dict["id"],
            name=workflow_dict["name"],
            description=workflow_dict.get("description"),
            nodes=workflow_dict.get("nodes", []),
            edges=workflow_dict.get("edges", []),
            metadata=workflow_dict.get("metadata", {}),
            created_at=workflow_dict.get("createdAt", time.time()),
            updated_at=workflow_dict.get("updatedAt", time.time())
        )


# Global workflow engine instance
workflow_engine = WorkflowEngine() 