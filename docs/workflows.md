# PocketFlow Workflow API Documentation

This document describes the REST API for the PocketFlow n8n-like workflow automation platform.

## Overview

The PocketFlow workflow system provides a REST API for creating, managing, and executing node-based workflows. The API is designed to integrate with a visual dashboard's Workflows tab, providing JSON responses suitable for a graph-based UI.

## Base URL

```
http://localhost:5000/api
```

## Authentication

Currently, the API uses token-based access control. Include your token in the request headers:

```
Authorization: Bearer YOUR_TOKEN
```

## Endpoints

### Health Check

#### GET /api/health

Check the health status of the API.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T12:00:00",
  "version": "1.0.0"
}
```

### Workflows

#### GET /api/workflows

List all workflows.

**Query Parameters:**
- `owner` (optional): Filter by workflow owner

**Response:**
```json
{
  "workflows": [
    {
      "id": "workflow-123",
      "name": "Email Processing",
      "description": "Process incoming emails",
      "owner": "user@example.com",
      "created_at": 1704067200,
      "updated_at": 1704067200,
      "is_active": true
    }
  ],
  "total": 1
}
```

#### POST /api/workflows

Create a new workflow.

**Request Body:**
```json
{
  "name": "My Workflow",
  "description": "A sample workflow",
  "nodes": [
    {
      "id": "node-1",
      "type": "EmailReceivedTrigger",
      "name": "Email Trigger",
      "position": {"x": 100, "y": 100},
      "data": {
        "host": "smtp.example.com",
        "port": 587
      }
    }
  ],
  "edges": [
    {
      "id": "edge-1",
      "source": "node-1",
      "target": "node-2",
      "sourceHandle": "email_data",
      "targetHandle": "input"
    }
  ]
}
```

**Response:**
```json
{
  "workflow": {
    "id": "workflow-123",
    "name": "My Workflow",
    "description": "A sample workflow",
    "nodes": [...],
    "edges": [...],
    "metadata": {},
    "createdAt": 1704067200,
    "updatedAt": 1704067200
  },
  "message": "Workflow created successfully"
}
```

#### GET /api/workflows/{id}

Get a specific workflow by ID.

**Response:**
```json
{
  "id": "workflow-123",
  "name": "My Workflow",
  "description": "A sample workflow",
  "nodes": [...],
  "edges": [...],
  "metadata": {},
  "createdAt": 1704067200,
  "updatedAt": 1704067200
}
```

#### PUT /api/workflows/{id}

Update a workflow.

**Request Body:** Same as POST /api/workflows

**Response:**
```json
{
  "workflow": {...},
  "message": "Workflow updated successfully"
}
```

#### DELETE /api/workflows/{id}

Delete a workflow (soft delete).

**Response:**
```json
{
  "message": "Workflow deleted successfully"
}
```

#### POST /api/workflows/{id}/run

Execute a workflow.

**Request Body:**
```json
{
  "initial_data": {
    "custom_field": "value"
  }
}
```

**Response:**
```json
{
  "execution_id": "exec-123",
  "status": "completed",
  "start_time": 1704067200,
  "end_time": 1704067210,
  "node_results": {
    "node-1": {
      "success": true,
      "email_data": {...}
    }
  },
  "error": null,
  "logs": [
    "INFO: Workflow started",
    "INFO: Node node-1 executed successfully"
  ]
}
```

#### GET /api/workflows/{id}/logs

Get execution logs for a workflow.

**Query Parameters:**
- `limit` (optional): Maximum number of logs to return (default: 100)

**Response:**
```json
{
  "workflow_id": "workflow-123",
  "logs": [
    {
      "id": 1,
      "execution_id": "exec-123",
      "timestamp": 1704067200,
      "level": "INFO",
      "message": "Workflow started",
      "data": null
    }
  ],
  "total": 1
}
```

### Executions

#### GET /api/executions/{execution_id}

Get the result of a specific execution.

**Response:**
```json
{
  "execution_id": "exec-123",
  "workflow_id": "workflow-123",
  "status": "completed",
  "start_time": 1704067200,
  "end_time": 1704067210,
  "node_results": {...},
  "error": null,
  "logs": [...]
}
```

### Nodes

#### GET /api/nodes

List all available node types.

**Response:**
```json
{
  "nodes": [
    {
      "type": "EmailReceivedTrigger",
      "name": "EmailReceivedTrigger",
      "description": "Triggers when a new email is received",
      "category": "trigger",
      "version": "1.0.0",
      "author": "PocketFlow",
      "icon": "email",
      "color": "#4CAF50",
      "inputs": [
        {
          "name": "host",
          "type": "string",
          "description": "SMTP host",
          "required": false,
          "default": null
        }
      ],
      "outputs": [
        {
          "name": "email_data",
          "type": "object",
          "description": "Complete email data"
        }
      ]
    }
  ],
  "total": 1
}
```

#### GET /api/nodes/{node_type}

Get details for a specific node type.

**Response:**
```json
{
  "type": "EmailReceivedTrigger",
  "name": "EmailReceivedTrigger",
  "description": "Triggers when a new email is received",
  "category": "trigger",
  "version": "1.0.0",
  "author": "PocketFlow",
  "icon": "email",
  "color": "#4CAF50",
  "inputs": [...],
  "outputs": [...]
}
```

#### GET /api/nodes/categories

Get all node categories.

**Response:**
```json
{
  "categories": {
    "trigger": {
      "name": "Trigger",
      "node_types": ["EmailReceivedTrigger", "ScheduledTrigger", "ManualTrigger"],
      "count": 3
    },
    "action": {
      "name": "Action",
      "node_types": ["SendEmailAction", "GenerateContentAction"],
      "count": 2
    }
  },
  "total_categories": 4
}
```

### Configuration

#### GET /api/config

Get application configuration.

**Response:**
```json
{
  "environment": "development",
  "debug": true,
  "log_level": "INFO",
  "flow_timeout": 300,
  "max_retries": 3,
  "content_output_dir": "/opt/pocketflow/data/generated",
  "max_content_duration": 300
}
```

## Error Handling

All endpoints return appropriate HTTP status codes:

- `200`: Success
- `201`: Created
- `400`: Bad Request
- `404`: Not Found
- `500`: Internal Server Error

Error responses include a description:

```json
{
  "error": "Workflow validation failed: Unknown node type: InvalidNode",
  "code": 400
}
```

## Workflow JSON Format

Workflows are defined using a JSON format compatible with graph-based UIs:

```json
{
  "id": "workflow-id",
  "name": "Workflow Name",
  "description": "Workflow description",
  "nodes": [
    {
      "id": "node-id",
      "type": "NodeType",
      "name": "Node Name",
      "position": {"x": 100, "y": 100},
      "data": {
        "param1": "value1",
        "param2": "value2"
      }
    }
  ],
  "edges": [
    {
      "id": "edge-id",
      "source": "source-node-id",
      "target": "target-node-id",
      "sourceHandle": "output-handle",
      "targetHandle": "input-handle",
      "condition": "condition-expression"
    }
  ],
  "metadata": {
    "version": "1.0.0",
    "author": "User",
    "category": "category",
    "tags": ["tag1", "tag2"]
  },
  "createdAt": 1704067200,
  "updatedAt": 1704067200
}
```

## Node Types

### Trigger Nodes

- **EmailReceivedTrigger**: Monitors for new emails
- **ScheduledTrigger**: Runs on a schedule
- **ManualTrigger**: Manual execution trigger

### Action Nodes

- **SendEmailAction**: Sends email responses
- **GenerateContentAction**: Generates audio/image content
- **GenerateLatexAction**: Generates LaTeX documents
- **WebSearchAction**: Performs web searches
- **HttpRequestAction**: Makes HTTP requests

### Condition Nodes

- **IfElseNode**: Evaluates conditions and routes execution

### Transform Nodes

- **TransformNode**: Manipulates data
- **DelayNode**: Adds delays to execution
- **LogNode**: Logs data to execution logs

## Examples

### Creating a Simple Email Workflow

```bash
curl -X POST http://localhost:5000/api/workflows \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Email Reply Workflow",
    "description": "Automatically reply to emails",
    "nodes": [
      {
        "id": "trigger",
        "type": "EmailReceivedTrigger",
        "name": "Email Trigger",
        "position": {"x": 100, "y": 100},
        "data": {}
      },
      {
        "id": "reply",
        "type": "SendEmailAction",
        "name": "Send Reply",
        "position": {"x": 300, "y": 100},
        "data": {
          "subject": "Re: {{email_data.subject}}",
          "body": "Thank you for your email. I will get back to you soon."
        }
      }
    ],
    "edges": [
      {
        "id": "edge1",
        "source": "trigger",
        "target": "reply"
      }
    ]
  }'
```

### Running a Workflow

```bash
curl -X POST http://localhost:5000/api/workflows/workflow-123/run \
  -H "Content-Type: application/json" \
  -d '{
    "initial_data": {
      "custom_field": "test value"
    }
  }'
```

## Integration with Visual Dashboard

The API is designed to work with visual workflow editors like React Flow. The workflow JSON format includes:

- **Nodes**: Array of node objects with position and configuration
- **Edges**: Array of connection objects between nodes
- **Position**: x,y coordinates for visual placement
- **Handles**: Input/output connection points for nodes

This format allows the dashboard to:
1. Display nodes in their correct positions
2. Show connections between nodes
3. Allow drag-and-drop editing
4. Save and load workflow configurations 