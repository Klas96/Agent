"""
REST API for PocketFlow n8n-like workflow system.
This module provides a Flask API that builds on top of the original PocketFlow system.
"""

import json
import time
from typing import Dict, Any, List, Optional
from datetime import datetime
from flask import Flask, request, jsonify, abort
from flask_cors import CORS
from werkzeug.exceptions import HTTPException

from ..core.workflow_engine import workflow_engine, WorkflowDefinition, WorkflowExecutionResult
from ..nodes.workflow.registry import workflow_node_registry
from ..config.settings import get_settings
from ..utils.logging import get_logger


def create_workflow_app():
    """Create the Flask app for workflow API."""
    app = Flask(__name__)
    CORS(app)
    
    settings = get_settings()
    app.config['SECRET_KEY'] = settings.SECRET_KEY
    app.config['DEBUG'] = settings.DEBUG
    
    logger = get_logger("WorkflowAPI")
    
    # Error handlers
    @app.errorhandler(HTTPException)
    def handle_exception(e):
        """Handle HTTP exceptions."""
        response = {
            "error": e.description,
            "code": e.code
        }
        return jsonify(response), e.code
    
    @app.errorhandler(Exception)
    def handle_generic_exception(e):
        """Handle generic exceptions."""
        logger.error(f"Unhandled exception: {e}", exc_info=True)
        response = {
            "error": "Internal server error",
            "code": 500
        }
        return jsonify(response), 500
    
    # Health check endpoint
    @app.route('/api/health', methods=['GET'])
    def health_check():
        """Health check endpoint."""
        return jsonify({
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "service": "PocketFlow Workflow API"
        })
    
    # Workflow management endpoints
    @app.route('/api/workflows', methods=['GET'])
    def list_workflows():
        """List all workflows."""
        # For now, return empty list - in production, this would query a database
        return jsonify({
            "workflows": [],
            "total": 0
        })
    
    @app.route('/api/workflows', methods=['POST'])
    def create_workflow():
        """Create a new workflow."""
        try:
            data = request.get_json()
            if not data:
                abort(400, description="Request body is required")
            
            name = data.get("name")
            if not name:
                abort(400, description="Workflow name is required")
            
            description = data.get("description")
            
            # Create workflow
            workflow = workflow_engine.create_workflow(name, description)
            
            # Add nodes if provided
            if "nodes" in data:
                for node_data in data["nodes"]:
                    workflow_engine.add_node(
                        workflow,
                        node_data["type"],
                        node_data["name"],
                        node_data["position"],
                        node_data.get("data", {})
                    )
            
            # Add edges if provided
            if "edges" in data:
                for edge_data in data["edges"]:
                    workflow_engine.add_edge(
                        workflow,
                        edge_data["source"],
                        edge_data["target"],
                        edge_data.get("sourceHandle"),
                        edge_data.get("targetHandle"),
                        edge_data.get("condition")
                    )
            
            # Validate workflow
            errors = workflow_engine.validate_workflow(workflow)
            if errors:
                abort(400, description=f"Workflow validation failed: {', '.join(errors)}")
            
            # Export workflow to JSON
            workflow_json = workflow_engine.export_workflow(workflow)
            
            return jsonify({
                "workflow": json.loads(workflow_json),
                "message": "Workflow created successfully"
            }), 201
            
        except Exception as e:
            logger.error(f"Error creating workflow: {e}")
            abort(500, description=str(e))
    
    @app.route('/api/workflows/<workflow_id>', methods=['GET'])
    def get_workflow(workflow_id):
        """Get a specific workflow."""
        # For now, return 404 - in production, this would query a database
        abort(404, description="Workflow not found")
    
    @app.route('/api/workflows/<workflow_id>', methods=['PUT'])
    def update_workflow(workflow_id):
        """Update a workflow."""
        # For now, return 404 - in production, this would update a database
        abort(404, description="Workflow not found")
    
    @app.route('/api/workflows/<workflow_id>', methods=['DELETE'])
    def delete_workflow(workflow_id):
        """Delete a workflow."""
        # For now, return 404 - in production, this would delete from a database
        abort(404, description="Workflow not found")
    
    @app.route('/api/workflows/<workflow_id>/run', methods=['POST'])
    def run_workflow(workflow_id):
        """Run a workflow."""
        try:
            data = request.get_json() or {}
            initial_data = data.get("initial_data", {})
            
            # For now, create a simple workflow for testing
            # In production, this would load the workflow from a database
            workflow = workflow_engine.create_workflow("Test Workflow")
            
            # Add a manual trigger node
            trigger_id = workflow_engine.add_node(
                workflow,
                "ManualTriggerNode",
                "Manual Trigger",
                {"x": 100, "y": 100},
                {"trigger_data": initial_data}
            )
            
            # Execute the workflow
            result = workflow_engine.execute_workflow(workflow, initial_data)
            
            return jsonify({
                "execution_id": result.execution_id,
                "status": result.status,
                "start_time": result.start_time,
                "end_time": result.end_time,
                "error": result.error,
                "node_results": result.node_results
            })
            
        except Exception as e:
            logger.error(f"Error running workflow: {e}")
            abort(500, description=str(e))
    
    @app.route('/api/workflows/<workflow_id>/logs', methods=['GET'])
    def get_workflow_logs(workflow_id):
        """Get logs for a workflow."""
        # For now, return empty logs - in production, this would query a database
        return jsonify({
            "logs": [],
            "workflow_id": workflow_id
        })
    
    # Execution management endpoints
    @app.route('/api/executions/<execution_id>', methods=['GET'])
    def get_execution_result(execution_id):
        """Get the result of a workflow execution."""
        result = workflow_engine.get_execution_result(execution_id)
        if not result:
            abort(404, description="Execution not found")
        
        return jsonify({
            "execution_id": result.execution_id,
            "workflow_id": result.workflow_id,
            "status": result.status,
            "start_time": result.start_time,
            "end_time": result.end_time,
            "error": result.error,
            "node_results": result.node_results,
            "logs": result.logs,
            "initial_data": result.initial_data
        })
    
    # Node management endpoints
    @app.route('/api/nodes', methods=['GET'])
    def list_nodes():
        """List all available node types."""
        try:
            node_types = workflow_node_registry.get_all_node_types()
            node_metadata = workflow_node_registry.get_all_node_metadata()
            
            nodes = []
            for node_type in node_types:
                metadata = node_metadata[node_type]
                nodes.append({
                    "type": node_type,
                    "name": metadata.name,
                    "description": metadata.description,
                    "category": metadata.category,
                    "version": metadata.version,
                    "author": metadata.author,
                    "icon": metadata.icon,
                    "color": metadata.color,
                    "inputs": [
                        {
                            "name": inp.name,
                            "type": inp.type,
                            "description": inp.description,
                            "required": inp.required,
                            "default": inp.default
                        }
                        for inp in metadata.inputs
                    ],
                    "outputs": [
                        {
                            "name": out.name,
                            "type": out.type,
                            "description": out.description
                        }
                        for out in metadata.outputs
                    ]
                })
            
            return jsonify({
                "nodes": nodes,
                "total": len(nodes)
            })
            
        except Exception as e:
            logger.error(f"Error listing nodes: {e}")
            abort(500, description=str(e))
    
    @app.route('/api/nodes/<node_type>', methods=['GET'])
    def get_node_details(node_type):
        """Get details for a specific node type."""
        try:
            metadata = workflow_node_registry.get_node_metadata(node_type)
            
            return jsonify({
                "type": node_type,
                "name": metadata.name,
                "description": metadata.description,
                "category": metadata.category,
                "version": metadata.version,
                "author": metadata.author,
                "icon": metadata.icon,
                "color": metadata.color,
                "inputs": [
                    {
                        "name": inp.name,
                        "type": inp.type,
                        "description": inp.description,
                        "required": inp.required,
                        "default": inp.default
                    }
                    for inp in metadata.inputs
                ],
                "outputs": [
                    {
                        "name": out.name,
                        "type": out.type,
                        "description": out.description
                    }
                    for out in metadata.outputs
                ]
            })
            
        except ValueError:
            abort(404, description=f"Node type '{node_type}' not found")
        except Exception as e:
            logger.error(f"Error getting node details: {e}")
            abort(500, description=str(e))
    
    @app.route('/api/nodes/categories', methods=['GET'])
    def get_node_categories():
        """Get all node categories."""
        try:
            categories = {}
            node_metadata = workflow_node_registry.get_all_node_metadata()
            
            for node_type, metadata in node_metadata.items():
                category = metadata.category
                if category not in categories:
                    categories[category] = []
                categories[category].append(node_type)
            
            return jsonify({
                "categories": categories
            })
            
        except Exception as e:
            logger.error(f"Error getting node categories: {e}")
            abort(500, description=str(e))
    
    # Configuration endpoint
    @app.route('/api/config', methods=['GET'])
    def get_config():
        """Get API configuration."""
        return jsonify({
            "version": "1.0.0",
            "service": "PocketFlow Workflow API",
            "features": {
                "workflows": True,
                "nodes": True,
                "executions": True,
                "logs": True
            },
            "node_categories": [
                "trigger",
                "action", 
                "condition",
                "transform"
            ]
        })
    
    return app


# Create the app instance
workflow_app = create_workflow_app() 