"""
Tests for the PocketFlow workflow engine and node system.
"""

import pytest
import json
from datetime import datetime
from unittest.mock import Mock, patch

from src.pocketflow.core.workflow import (
    WorkflowEngine, WorkflowDefinition, NodeConfig, Edge,
    ExecutionStatus, workflow_engine
)
from src.pocketflow.core.types import SharedState
from src.pocketflow.nodes import node_registry
from src.pocketflow.nodes.base import BaseNode, NodeMetadata, NodeInput, NodeOutput


class MockNode(BaseNode):
    """Mock node for testing."""
    
    def execute(self, shared: SharedState) -> dict:
        """Mock execution."""
        input_value = self.get_input_value("input_field", "default")
        self.set_output(shared, "output_field", f"processed_{input_value}")
        
        return {
            "success": True,
            "input_received": input_value,
            "output_generated": f"processed_{input_value}"
        }
    
    @classmethod
    def get_metadata(cls) -> NodeMetadata:
        """Get metadata for MockNode."""
        return NodeMetadata(
            name="MockNode",
            description="A mock node for testing",
            category="action",
            inputs=[
                NodeInput("input_field", "string", "Input field", False, "default")
            ],
            outputs=[
                NodeOutput("output_field", "string", "Output field")
            ]
        )


class MockTriggerNode(BaseNode):
    """Mock trigger node for testing."""
    
    def execute(self, shared: SharedState) -> dict:
        """Mock trigger execution."""
        trigger_data = self.get_input_value("trigger_data", {})
        shared["trigger_data"] = trigger_data
        
        return {
            "triggered": True,
            "trigger_data": trigger_data
        }
    
    @classmethod
    def get_metadata(cls) -> NodeMetadata:
        """Get metadata for MockTriggerNode."""
        return NodeMetadata(
            name="MockTriggerNode",
            description="A mock trigger node for testing",
            category="trigger",
            inputs=[
                NodeInput("trigger_data", "object", "Trigger data", False, {})
            ],
            outputs=[]
        )


class TestWorkflowEngine:
    """Test cases for the WorkflowEngine class."""
    
    def setup_method(self):
        """Set up test environment."""
        self.engine = WorkflowEngine()
        self.engine.register_node("MockNode", MockNode)
        self.engine.register_node("MockTriggerNode", MockTriggerNode)
    
    def test_create_workflow(self):
        """Test workflow creation."""
        workflow = self.engine.create_workflow("Test Workflow", "Test description")
        
        assert workflow.name == "Test Workflow"
        assert workflow.description == "Test description"
        assert workflow.id is not None
        assert len(workflow.nodes) == 0
        assert len(workflow.edges) == 0
    
    def test_add_node(self):
        """Test adding nodes to workflow."""
        workflow = self.engine.create_workflow("Test Workflow")
        
        node_id = self.engine.add_node(
            workflow=workflow,
            node_type="MockNode",
            name="Test Node",
            position={"x": 100, "y": 100},
            data={"input_field": "test_value"}
        )
        
        assert node_id is not None
        assert len(workflow.nodes) == 1
        assert workflow.nodes[0].id == node_id
        assert workflow.nodes[0].type == "MockNode"
        assert workflow.nodes[0].name == "Test Node"
        assert workflow.nodes[0].data["input_field"] == "test_value"
    
    def test_add_edge(self):
        """Test adding edges to workflow."""
        workflow = self.engine.create_workflow("Test Workflow")
        
        # Add nodes first
        node1_id = self.engine.add_node(workflow, "MockNode", "Node 1", {"x": 100, "y": 100})
        node2_id = self.engine.add_node(workflow, "MockNode", "Node 2", {"x": 200, "y": 100})
        
        # Add edge
        edge_id = self.engine.add_edge(
            workflow=workflow,
            source=node1_id,
            target=node2_id,
            source_handle="output_field",
            target_handle="input_field"
        )
        
        assert edge_id is not None
        assert len(workflow.edges) == 1
        assert workflow.edges[0].id == edge_id
        assert workflow.edges[0].source == node1_id
        assert workflow.edges[0].target == node2_id
    
    def test_validate_workflow_valid(self):
        """Test workflow validation with valid workflow."""
        workflow = self.engine.create_workflow("Test Workflow")
        
        # Add trigger node
        trigger_id = self.engine.add_node(workflow, "MockTriggerNode", "Trigger", {"x": 100, "y": 100})
        
        # Add action node
        action_id = self.engine.add_node(workflow, "MockNode", "Action", {"x": 200, "y": 100})
        
        # Add edge
        self.engine.add_edge(workflow, trigger_id, action_id)
        
        errors = self.engine.validate_workflow(workflow)
        assert len(errors) == 0
    
    def test_validate_workflow_no_nodes(self):
        """Test workflow validation with no nodes."""
        workflow = self.engine.create_workflow("Test Workflow")
        
        errors = self.engine.validate_workflow(workflow)
        assert len(errors) > 0
        assert "Workflow must have at least one node" in errors
    
    def test_validate_workflow_unknown_node_type(self):
        """Test workflow validation with unknown node type."""
        workflow = self.engine.create_workflow("Test Workflow")
        
        # Add node with unknown type
        self.engine.add_node(workflow, "UnknownNode", "Unknown", {"x": 100, "y": 100})
        
        errors = self.engine.validate_workflow(workflow)
        assert len(errors) > 0
        assert "Unknown node type: UnknownNode" in errors
    
    def test_validate_workflow_cycles(self):
        """Test workflow validation with cycles."""
        workflow = self.engine.create_workflow("Test Workflow")
        
        # Add nodes
        node1_id = self.engine.add_node(workflow, "MockNode", "Node 1", {"x": 100, "y": 100})
        node2_id = self.engine.add_node(workflow, "MockNode", "Node 2", {"x": 200, "y": 100})
        
        # Add edges creating a cycle
        self.engine.add_edge(workflow, node1_id, node2_id)
        self.engine.add_edge(workflow, node2_id, node1_id)
        
        errors = self.engine.validate_workflow(workflow)
        assert len(errors) > 0
        assert "Workflow contains cycles" in errors
    
    def test_execute_workflow_simple(self):
        """Test simple workflow execution."""
        workflow = self.engine.create_workflow("Test Workflow")
        
        # Add trigger node
        trigger_id = self.engine.add_node(
            workflow, "MockTriggerNode", "Trigger", {"x": 100, "y": 100},
            {"trigger_data": {"test": "value"}}
        )
        
        # Execute workflow
        result = self.engine.execute_workflow(workflow, {"initial": "data"})
        
        assert result.status == ExecutionStatus.COMPLETED
        assert result.workflow_id == workflow.id
        assert result.error is None
        assert len(result.node_results) == 1
        assert trigger_id in result.node_results
    
    def test_execute_workflow_with_action(self):
        """Test workflow execution with trigger and action nodes."""
        workflow = self.engine.create_workflow("Test Workflow")
        
        # Add trigger node
        trigger_id = self.engine.add_node(
            workflow, "MockTriggerNode", "Trigger", {"x": 100, "y": 100}
        )
        
        # Add action node
        action_id = self.engine.add_node(
            workflow, "MockNode", "Action", {"x": 200, "y": 100},
            {"input_field": "test_input"}
        )
        
        # Add edge
        self.engine.add_edge(workflow, trigger_id, action_id)
        
        # Execute workflow
        result = self.engine.execute_workflow(workflow)
        
        assert result.status == ExecutionStatus.COMPLETED
        assert len(result.node_results) == 2
        assert trigger_id in result.node_results
        assert action_id in result.node_results
        
        # Check action node result
        action_result = result.node_results[action_id]
        assert action_result["success"] is True
        assert action_result["input_received"] == "test_input"
        assert action_result["output_generated"] == "processed_test_input"
    
    def test_execute_workflow_invalid(self):
        """Test workflow execution with invalid workflow."""
        workflow = self.engine.create_workflow("Test Workflow")
        
        # Add node with unknown type (invalid)
        self.engine.add_node(workflow, "UnknownNode", "Unknown", {"x": 100, "y": 100})
        
        # Execute workflow
        result = self.engine.execute_workflow(workflow)
        
        assert result.status == ExecutionStatus.FAILED
        assert result.error is not None
        assert "Workflow validation failed" in result.error
    
    def test_export_workflow(self):
        """Test workflow export to JSON."""
        workflow = self.engine.create_workflow("Test Workflow", "Test description")
        
        # Add node
        node_id = self.engine.add_node(
            workflow, "MockNode", "Test Node", {"x": 100, "y": 100},
            {"input_field": "test_value"}
        )
        
        # Export workflow
        workflow_json = self.engine.export_workflow(workflow)
        workflow_dict = json.loads(workflow_json)
        
        assert workflow_dict["name"] == "Test Workflow"
        assert workflow_dict["description"] == "Test description"
        assert len(workflow_dict["nodes"]) == 1
        assert workflow_dict["nodes"][0]["id"] == node_id
        assert workflow_dict["nodes"][0]["type"] == "MockNode"
    
    def test_import_workflow(self):
        """Test workflow import from JSON."""
        workflow_json = '''
        {
            "id": "test-workflow",
            "name": "Test Workflow",
            "description": "Test description",
            "nodes": [
                {
                    "id": "node-1",
                    "type": "MockNode",
                    "name": "Test Node",
                    "position": {"x": 100, "y": 100},
                    "data": {"input_field": "test_value"}
                }
            ],
            "edges": [],
            "metadata": {},
            "createdAt": 1704067200,
            "updatedAt": 1704067200
        }
        '''
        
        workflow = self.engine.import_workflow(workflow_json)
        
        assert workflow.id == "test-workflow"
        assert workflow.name == "Test Workflow"
        assert workflow.description == "Test description"
        assert len(workflow.nodes) == 1
        assert workflow.nodes[0].id == "node-1"
        assert workflow.nodes[0].type == "MockNode"
    
    def test_get_execution_order(self):
        """Test getting execution order for nodes."""
        workflow = self.engine.create_workflow("Test Workflow")
        
        # Add nodes
        node1_id = self.engine.add_node(workflow, "MockNode", "Node 1", {"x": 100, "y": 100})
        node2_id = self.engine.add_node(workflow, "MockNode", "Node 2", {"x": 200, "y": 100})
        node3_id = self.engine.add_node(workflow, "MockNode", "Node 3", {"x": 300, "y": 100})
        
        # Add edges: node1 -> node2 -> node3
        self.engine.add_edge(workflow, node1_id, node2_id)
        self.engine.add_edge(workflow, node2_id, node3_id)
        
        execution_order = self.engine._get_execution_order(workflow)
        
        # Check that node1 comes before node2, and node2 comes before node3
        assert execution_order.index(node1_id) < execution_order.index(node2_id)
        assert execution_order.index(node2_id) < execution_order.index(node3_id)
    
    def test_get_execution_result(self):
        """Test getting execution result."""
        workflow = self.engine.create_workflow("Test Workflow")
        
        # Add trigger node
        self.engine.add_node(workflow, "MockTriggerNode", "Trigger", {"x": 100, "y": 100})
        
        # Execute workflow
        result = self.engine.execute_workflow(workflow)
        
        # Get execution result
        retrieved_result = self.engine.get_execution_result(result.execution_id)
        
        assert retrieved_result is not None
        assert retrieved_result.execution_id == result.execution_id
        assert retrieved_result.status == result.status
    
    def test_get_workflow_executions(self):
        """Test getting workflow executions."""
        workflow = self.engine.create_workflow("Test Workflow")
        
        # Add trigger node
        self.engine.add_node(workflow, "MockTriggerNode", "Trigger", {"x": 100, "y": 100})
        
        # Execute workflow multiple times
        result1 = self.engine.execute_workflow(workflow)
        result2 = self.engine.execute_workflow(workflow)
        
        # Get executions
        executions = self.engine.get_workflow_executions(workflow.id)
        
        assert len(executions) == 2
        execution_ids = [execution.execution_id for execution in executions]
        assert result1.execution_id in execution_ids
        assert result2.execution_id in execution_ids


class TestNodeRegistry:
    """Test cases for the NodeRegistry class."""
    
    def test_register_node(self):
        """Test node registration."""
        registry = node_registry
        
        # Check that MockNode is registered
        assert "MockNode" in registry.get_all_node_types()
        
        # Get node class
        node_class = registry.get_node_class("MockNode")
        assert node_class == MockNode
    
    def test_create_node(self):
        """Test node creation."""
        registry = node_registry
        
        config = {"input_field": "test_value"}
        node = registry.create_node("MockNode", config)
        
        assert isinstance(node, MockNode)
        assert node.config["input_field"] == "test_value"
    
    def test_get_node_metadata(self):
        """Test getting node metadata."""
        registry = node_registry
        
        metadata = registry.get_node_metadata("MockNode")
        
        assert metadata.name == "MockNode"
        assert metadata.category == "action"
        assert len(metadata.inputs) == 1
        assert len(metadata.outputs) == 1
    
    def test_get_all_node_metadata(self):
        """Test getting all node metadata."""
        registry = node_registry
        
        all_metadata = registry.get_all_node_metadata()
        
        assert "MockNode" in all_metadata
        assert "MockTriggerNode" in all_metadata
        assert all_metadata["MockNode"].name == "MockNode"
    
    def test_get_nodes_by_category(self):
        """Test getting nodes by category."""
        registry = node_registry
        
        action_nodes = registry.get_nodes_by_category("action")
        trigger_nodes = registry.get_nodes_by_category("trigger")
        
        assert "MockNode" in action_nodes
        assert "MockTriggerNode" in trigger_nodes


class TestMockNode:
    """Test cases for the MockNode class."""
    
    def test_mock_node_execution(self):
        """Test MockNode execution."""
        config = {"input_field": "test_input"}
        node = MockNode(config)
        
        shared = SharedState()
        result = node.execute(shared)
        
        assert result["success"] is True
        assert result["input_received"] == "test_input"
        assert result["output_generated"] == "processed_test_input"
        
        # Check outputs in shared state
        assert shared.get("outputs", {}).get("output_field") == "processed_test_input"
    
    def test_mock_node_default_input(self):
        """Test MockNode with default input."""
        config = {}
        node = MockNode(config)
        
        shared = SharedState()
        result = node.execute(shared)
        
        assert result["input_received"] == "default"
        assert result["output_generated"] == "processed_default"
    
    def test_mock_node_metadata(self):
        """Test MockNode metadata."""
        metadata = MockNode.get_metadata()
        
        assert metadata.name == "MockNode"
        assert metadata.description == "A mock node for testing"
        assert metadata.category == "action"
        assert len(metadata.inputs) == 1
        assert len(metadata.outputs) == 1
        
        # Check input metadata
        input_metadata = metadata.inputs[0]
        assert input_metadata.name == "input_field"
        assert input_metadata.type == "string"
        assert input_metadata.required is False
        assert input_metadata.default == "default"
        
        # Check output metadata
        output_metadata = metadata.outputs[0]
        assert output_metadata.name == "output_field"
        assert output_metadata.type == "string"


class TestMockTriggerNode:
    """Test cases for the MockTriggerNode class."""
    
    def test_mock_trigger_execution(self):
        """Test MockTriggerNode execution."""
        config = {"trigger_data": {"test": "value"}}
        node = MockTriggerNode(config)
        
        shared = SharedState()
        result = node.execute(shared)
        
        assert result["triggered"] is True
        assert result["trigger_data"] == {"test": "value"}
        assert shared["trigger_data"] == {"test": "value"}
    
    def test_mock_trigger_metadata(self):
        """Test MockTriggerNode metadata."""
        metadata = MockTriggerNode.get_metadata()
        
        assert metadata.name == "MockTriggerNode"
        assert metadata.category == "trigger"
        assert len(metadata.inputs) == 1
        assert len(metadata.outputs) == 0


if __name__ == "__main__":
    pytest.main([__file__]) 