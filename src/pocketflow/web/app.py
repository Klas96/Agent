"""
Flask REST API for PocketFlow n8n-like workflow automation platform.

This module provides the REST API endpoints for managing workflows and nodes.
"""

import json
import time
from typing import Dict, Any, List, Optional
from datetime import datetime

from flask import Flask, request, jsonify, abort
from flask_cors import CORS
from werkzeug.exceptions import HTTPException

from ..core.workflow import workflow_engine, WorkflowDefinition, ExecutionResult
from ..nodes import node_registry
from ..services.database_service import DatabaseService
from ..config.settings import get_settings
from ..utils.logging import get_logger


def create_app():
    """Create and configure the Flask application."""
    app = Flask(__name__)
    
    # Configure CORS
    CORS(app)
    
    # Configure settings
    settings = get_settings()
    app.config['SECRET_KEY'] = settings.SECRET_KEY
    app.config['DEBUG'] = settings.DEBUG
    
    # Initialize services
    db_service = DatabaseService()
    logger = get_logger("WebApp")
    
    # Register nodes with workflow engine
    for node_type in node_registry.get_all_node_types():
        node_class = node_registry.get_node_class(node_type)
        workflow_engine.register_node(node_type, node_class)
    
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
        logger.error(f"Unhandled exception: {e}")
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
            "version": "1.0.0"
        })
    
    # Workflow endpoints
    @app.route('/api/workflows', methods=['GET'])
    def list_workflows():
        """List all workflows."""
        try:
            # Get workflows from database (placeholder implementation)
            workflows = []
            
            # For now, return empty list - will be implemented with database
            return jsonify({
                "workflows": workflows,
                "total": len(workflows)
            })
        except Exception as e:
            logger.error(f"Error listing workflows: {e}")
            abort(500, description="Failed to list workflows")
    
    @app.route('/api/workflows', methods=['POST'])
    def create_workflow():
        """Create a new workflow."""
        try:
            data = request.get_json()
            if not data:
                abort(400, description="No data provided")
            
            name = data.get('name')
            description = data.get('description')
            
            if not name:
                abort(400, description="Workflow name is required")
            
            # Create workflow
            workflow = workflow_engine.create_workflow(name, description)
            
            # Add nodes if provided
            if 'nodes' in data:
                for node_data in data['nodes']:
                    workflow_engine.add_node(
                        workflow=workflow,
                        node_type=node_data['type'],
                        name=node_data['name'],
                        position=node_data.get('position', {}),
                        data=node_data.get('data', {})
                    )
            
            # Add edges if provided
            if 'edges' in data:
                for edge_data in data['edges']:
                    workflow_engine.add_edge(
                        workflow=workflow,
                        source=edge_data['source'],
                        target=edge_data['target'],
                        source_handle=edge_data.get('sourceHandle'),
                        target_handle=edge_data.get('targetHandle'),
                        condition=edge_data.get('condition')
                    )
            
            # Validate workflow
            errors = workflow_engine.validate_workflow(workflow)
            if errors:
                abort(400, description=f"Workflow validation failed: {'; '.join(errors)}")
            
            # Store workflow (placeholder - will be implemented with database)
            workflow_json = workflow_engine.export_workflow(workflow)
            
            return jsonify({
                "workflow": json.loads(workflow_json),
                "message": "Workflow created successfully"
            }), 201
            
        except Exception as e:
            logger.error(f"Error creating workflow: {e}")
            abort(500, description="Failed to create workflow")
    
    @app.route('/api/workflows/<workflow_id>', methods=['GET'])
    def get_workflow(workflow_id):
        """Get a specific workflow."""
        try:
            # Get workflow from database (placeholder implementation)
            # For now, return 404 - will be implemented with database
            abort(404, description="Workflow not found")
            
        except Exception as e:
            logger.error(f"Error getting workflow: {e}")
            abort(500, description="Failed to get workflow")
    
    @app.route('/api/workflows/<workflow_id>', methods=['PUT'])
    def update_workflow(workflow_id):
        """Update a workflow."""
        try:
            data = request.get_json()
            if not data:
                abort(400, description="No data provided")
            
            # Update workflow (placeholder implementation)
            # For now, return 404 - will be implemented with database
            abort(404, description="Workflow not found")
            
        except Exception as e:
            logger.error(f"Error updating workflow: {e}")
            abort(500, description="Failed to update workflow")
    
    @app.route('/api/workflows/<workflow_id>', methods=['DELETE'])
    def delete_workflow(workflow_id):
        """Delete a workflow."""
        try:
            # Delete workflow (placeholder implementation)
            # For now, return 404 - will be implemented with database
            abort(404, description="Workflow not found")
            
        except Exception as e:
            logger.error(f"Error deleting workflow: {e}")
            abort(500, description="Failed to delete workflow")
    
    @app.route('/api/workflows/<workflow_id>/run', methods=['POST'])
    def run_workflow(workflow_id):
        """Execute a workflow."""
        try:
            data = request.get_json() or {}
            initial_data = data.get('initial_data', {})
            
            # Get workflow (placeholder implementation)
            # For now, create a sample workflow for testing
            workflow = workflow_engine.create_workflow("Sample Workflow")
            
            # Add a manual trigger node
            trigger_id = workflow_engine.add_node(
                workflow=workflow,
                node_type="ManualTrigger",
                name="Manual Trigger",
                position={"x": 100, "y": 100},
                data={"trigger_data": initial_data}
            )
            
            # Execute workflow
            result = workflow_engine.execute_workflow(workflow, initial_data)
            
            return jsonify({
                "execution_id": result.execution_id,
                "status": result.status.value,
                "start_time": result.start_time,
                "end_time": result.end_time,
                "node_results": result.node_results,
                "error": result.error,
                "logs": result.logs
            })
            
        except Exception as e:
            logger.error(f"Error running workflow: {e}")
            abort(500, description="Failed to run workflow")
    
    @app.route('/api/workflows/<workflow_id>/logs', methods=['GET'])
    def get_workflow_logs(workflow_id):
        """Get execution logs for a workflow."""
        try:
            # Get logs from database (placeholder implementation)
            logs = []
            
            return jsonify({
                "workflow_id": workflow_id,
                "logs": logs,
                "total": len(logs)
            })
            
        except Exception as e:
            logger.error(f"Error getting workflow logs: {e}")
            abort(500, description="Failed to get workflow logs")
    
    @app.route('/api/executions/<execution_id>', methods=['GET'])
    def get_execution_result(execution_id):
        """Get the result of a specific execution."""
        try:
            result = workflow_engine.get_execution_result(execution_id)
            if not result:
                abort(404, description="Execution not found")
            
            return jsonify({
                "execution_id": result.execution_id,
                "workflow_id": result.workflow_id,
                "status": result.status.value,
                "start_time": result.start_time,
                "end_time": result.end_time,
                "node_results": result.node_results,
                "error": result.error,
                "logs": result.logs
            })
            
        except Exception as e:
            logger.error(f"Error getting execution result: {e}")
            abort(500, description="Failed to get execution result")
    
    # Node endpoints
    @app.route('/api/nodes', methods=['GET'])
    def list_nodes():
        """List all available node types."""
        try:
            node_types = node_registry.get_all_node_types()
            node_metadata = node_registry.get_all_node_metadata()
            
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
                            "name": input_def.name,
                            "type": input_def.type,
                            "description": input_def.description,
                            "required": input_def.required,
                            "default": input_def.default
                        }
                        for input_def in metadata.inputs
                    ],
                    "outputs": [
                        {
                            "name": output_def.name,
                            "type": output_def.type,
                            "description": output_def.description
                        }
                        for output_def in metadata.outputs
                    ]
                })
            
            return jsonify({
                "nodes": nodes,
                "total": len(nodes)
            })
            
        except Exception as e:
            logger.error(f"Error listing nodes: {e}")
            abort(500, description="Failed to list nodes")
    
    @app.route('/api/nodes/<node_type>', methods=['GET'])
    def get_node_details(node_type):
        """Get details for a specific node type."""
        try:
            metadata = node_registry.get_node_metadata(node_type)
            
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
                        "name": input_def.name,
                        "type": input_def.type,
                        "description": input_def.description,
                        "required": input_def.required,
                        "default": input_def.default
                    }
                    for input_def in metadata.inputs
                ],
                "outputs": [
                    {
                        "name": output_def.name,
                        "type": output_def.type,
                        "description": output_def.description
                    }
                    for output_def in metadata.outputs
                ]
            })
            
        except ValueError:
            abort(404, description="Node type not found")
        except Exception as e:
            logger.error(f"Error getting node details: {e}")
            abort(500, description="Failed to get node details")
    
    @app.route('/api/nodes/categories', methods=['GET'])
    def get_node_categories():
        """Get all node categories."""
        try:
            categories = ["trigger", "action", "condition", "transform"]
            
            category_data = {}
            for category in categories:
                node_types = node_registry.get_nodes_by_category(category)
                category_data[category] = {
                    "name": category.title(),
                    "node_types": node_types,
                    "count": len(node_types)
                }
            
            return jsonify({
                "categories": category_data,
                "total_categories": len(categories)
            })
            
        except Exception as e:
            logger.error(f"Error getting node categories: {e}")
            abort(500, description="Failed to get node categories")
    
    # Configuration endpoints
    @app.route('/api/config', methods=['GET'])
    def get_config():
        """Get application configuration."""
        try:
            settings = get_settings()
            
            # Return safe configuration (no sensitive data)
            config = {
                "environment": settings.ENVIRONMENT,
                "debug": settings.DEBUG,
                "log_level": settings.LOG_LEVEL,
                "flow_timeout": settings.FLOW_TIMEOUT,
                "max_retries": settings.MAX_RETRIES,
                "content_output_dir": settings.CONTENT_OUTPUT_DIR,
                "max_content_duration": settings.MAX_CONTENT_DURATION
            }
            
            return jsonify(config)
            
        except Exception as e:
            logger.error(f"Error getting config: {e}")
            abort(500, description="Failed to get configuration")
    
    return app


# Create the application instance
app = create_app()


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000) 