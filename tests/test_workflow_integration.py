"""
Tests for PocketFlow workflow integration.
This module tests that the n8n-like workflow system integrates properly with the original PocketFlow framework.
"""

import pytest
import json
from unittest.mock import Mock, patch

from src.pocketflow.core.workflow_engine import workflow_engine, WorkflowDefinition
from src.pocketflow.core.types import SharedState
from src.pocketflow.nodes.workflow.registry import workflow_node_registry
from src.pocketflow.nodes.workflow.triggers import ManualTriggerNode


class TestWorkflowIntegration:
    """Test that workflow system integrates with original PocketFlow."""
    
    def setup_method(self):
        """Set up test environment."""
        # Clear any existing workflows
        workflow_engine.execution_history.clear()
    
    def test_workflow_engine_creates_pocketflow_flow(self):
        """Test that workflow engine creates valid PocketFlow flows."""
        # Create a simple workflow
        workflow = workflow_engine.create_workflow("Test Workflow")
        
        # Add a manual trigger node
        trigger_id = workflow_engine.add_node(
            workflow,
            "ManualTriggerNode",
            "Manual Trigger",
            {"x": 100, "y": 100},
            {"trigger_data": {"test": "data"}}
        )
        
        # Validate workflow
        errors = workflow_engine.validate_workflow(workflow)
        assert not errors, f"Workflow validation failed: {errors}"
        
        # Convert to PocketFlow flow
        flow = workflow_engine._convert_to_pocketflow_flow(workflow)
        
        # Verify it's a valid PocketFlow flow
        assert flow.name == "Test Workflow"
        assert flow.start_step == trigger_id
        assert len(flow.steps) == 1
        assert trigger_id in flow.steps
    
    def test_workflow_node_inherits_from_pocketflow_node(self):
        """Test that workflow nodes inherit from original PocketFlow Node."""
        # Create a workflow node
        config = {"trigger_data": {"test": "data"}}
        node = ManualTriggerNode(config, "Test Trigger")
        
        # Verify it's a valid PocketFlow Node
        assert hasattr(node, 'run')
        assert hasattr(node, 'prep')
        assert hasattr(node, 'exec')
        assert hasattr(node, 'post')
        
        # Verify it has workflow-specific methods
        assert hasattr(node, 'execute_workflow')
        assert hasattr(node, 'get_metadata')
    
    def test_workflow_execution_uses_pocketflow_flow(self):
        """Test that workflow execution uses the original PocketFlow flow system."""
        # Create a simple workflow
        workflow = workflow_engine.create_workflow("Test Workflow")
        
        # Add a manual trigger node
        trigger_id = workflow_engine.add_node(
            workflow,
            "ManualTriggerNode",
            "Manual Trigger",
            {"x": 100, "y": 100},
            {"trigger_data": {"test": "data"}}
        )
        
        # Execute the workflow
        result = workflow_engine.execute_workflow(workflow, {"initial": "data"})
        
        # Verify execution was successful
        assert result.status == "success"
        assert result.workflow_id == workflow.id
        assert result.execution_id is not None
        
        # Verify the result contains PocketFlow flow results
        assert "final_result" in result.node_results
        assert "metadata" in result.node_results
    
    def test_workflow_node_registry_integrates_with_pocketflow(self):
        """Test that workflow node registry works with PocketFlow nodes."""
        # Get all available node types
        node_types = workflow_node_registry.get_all_node_types()
        
        # Verify we have some nodes
        assert len(node_types) > 0
        
        # Verify we can create nodes
        for node_type in node_types:
            try:
                node = workflow_node_registry.create_node(
                    node_type, 
                    {"test": "config"}, 
                    f"Test {node_type}"
                )
                
                # Verify it's a valid PocketFlow Node
                assert hasattr(node, 'run')
                assert hasattr(node, 'prep')
                assert hasattr(node, 'exec')
                assert hasattr(node, 'post')
                
            except Exception as e:
                pytest.fail(f"Failed to create node {node_type}: {e}")
    
    def test_workflow_export_import_compatibility(self):
        """Test that workflow export/import works with JSON format."""
        # Create a workflow
        workflow = workflow_engine.create_workflow("Test Workflow", "Test Description")
        
        # Add a node
        workflow_engine.add_node(
            workflow,
            "ManualTriggerNode",
            "Manual Trigger",
            {"x": 100, "y": 100},
            {"trigger_data": {"test": "data"}}
        )
        
        # Export to JSON
        workflow_json = workflow_engine.export_workflow(workflow)
        workflow_dict = json.loads(workflow_json)
        
        # Verify JSON structure
        assert "id" in workflow_dict
        assert "name" in workflow_dict
        assert "description" in workflow_dict
        assert "nodes" in workflow_dict
        assert "edges" in workflow_dict
        assert "metadata" in workflow_dict
        
        # Import from JSON
        imported_workflow = workflow_engine.import_workflow(workflow_json)
        
        # Verify imported workflow matches original
        assert imported_workflow.id == workflow.id
        assert imported_workflow.name == workflow.name
        assert imported_workflow.description == workflow.description
        assert len(imported_workflow.nodes) == len(workflow.nodes)
    
    def test_workflow_with_original_pocketflow_services(self):
        """Test that workflow nodes can use original PocketFlow services."""
        # Create a workflow node that uses email service
        config = {
            "host": "test.example.com",
            "port": 587,
            "username": "test@example.com",
            "password": "password",
            "use_tls": True
        }
        
        # This should work without errors (even if email service is mocked)
        node = ManualTriggerNode(config, "Email Trigger")
        
        # Verify node has access to PocketFlow services
        assert hasattr(node, 'settings')
        assert hasattr(node, 'logger')
        
        # Verify node can be executed (even if it fails due to missing email service)
        shared = SharedState()
        try:
            result = node.run(shared)
            # Should either succeed or fail gracefully
            assert result is not None
        except Exception as e:
            # Expected if email service is not available
            assert "email" in str(e).lower() or "connection" in str(e).lower()


class TestWorkflowNodeCompatibility:
    """Test compatibility between workflow nodes and original PocketFlow nodes."""
    
    def test_workflow_node_can_be_used_in_pocketflow_flow(self):
        """Test that workflow nodes can be used in original PocketFlow flows."""
        from src.pocketflow.core.flow import FlowBuilder, FlowType
        
        # Create a PocketFlow flow
        flow_builder = FlowBuilder("Test Flow", FlowType.USER, requires_tokens=False)
        
        # Add a workflow node to the flow
        workflow_node = ManualTriggerNode(
            {"trigger_data": {"test": "data"}}, 
            "Workflow Trigger"
        )
        
        flow_builder.add_step("trigger", workflow_node)
        flow_builder.set_start("trigger")
        flow_builder.add_end_step("trigger")
        
        # Build the flow
        flow = flow_builder.build()
        
        # Verify the flow is valid
        assert flow.validate()
        assert flow.start_step == "trigger"
        assert "trigger" in flow.steps
        
        # Execute the flow
        shared = SharedState()
        result = flow.run(shared)
        
        # Verify execution was successful
        assert result.success
        assert result.data is not None
    
    def test_workflow_node_metadata_compatibility(self):
        """Test that workflow node metadata is compatible with visual editors."""
        # Get metadata for a workflow node
        metadata = ManualTriggerNode.get_metadata()
        
        # Verify metadata structure
        assert hasattr(metadata, 'name')
        assert hasattr(metadata, 'description')
        assert hasattr(metadata, 'category')
        assert hasattr(metadata, 'inputs')
        assert hasattr(metadata, 'outputs')
        assert hasattr(metadata, 'icon')
        assert hasattr(metadata, 'color')
        
        # Verify inputs and outputs are properly structured
        for input_def in metadata.inputs:
            assert hasattr(input_def, 'name')
            assert hasattr(input_def, 'type')
            assert hasattr(input_def, 'description')
            assert hasattr(input_def, 'required')
        
        for output_def in metadata.outputs:
            assert hasattr(output_def, 'name')
            assert hasattr(output_def, 'type')
            assert hasattr(output_def, 'description') 