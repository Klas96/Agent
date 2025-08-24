---
layout: default
title: "PocketFlow"
nav_order: 1
---

# PocketFlow

A modular email processing and content generation system with **n8n-like workflow automation capabilities**.

PocketFlow combines the power of the original PocketFlow framework with modern visual workflow automation, allowing you to create complex workflows through both traditional flows and a visual editor interface.

## 🎯 Quick Visualization

See the left-to-right workflow flow in action:

```bash
python3 show_workflow_visualization.py
```

This shows how workflows flow from **Visual Dashboard** → **Workflow API** → **Workflow Engine** → **Original PocketFlow** → **Services**.

## Key Features

### 🔧 Core Architecture
- **Original PocketFlow Framework**: Maintains all existing email processing, content generation, and research capabilities
- **n8n-like Workflow System**: Visual workflow editor compatible with React Flow and similar tools
- **Hybrid Approach**: Use traditional flows or visual workflows - both work seamlessly together
- **REST API**: Complete HTTP API for workflow management and execution

### 📧 Email Processing
- **Email Triggers**: Monitor for new emails and trigger workflows automatically
- **Email Actions**: Send emails with dynamic content and attachments
- **Conversation Context**: Maintain conversation history and context
- **Token-based Access**: Secure email processing with user authentication

### 🎨 Content Generation
- **Audio Generation**: Create audio content from text using AI
- **Image Generation**: Generate images from descriptions
- **LaTeX Documents**: Create professional documents using templates
- **Dynamic Content**: Generate content based on workflow data

### 🔍 Research & Investigation
- **Web Search**: Search the web for information
- **Topic Investigation**: Deep dive into specific topics
- **Data Analysis**: Process and analyze research results
- **Content Synthesis**: Combine multiple sources into coherent content

### 🔄 Workflow Control
- **Visual Editor**: Drag-and-drop workflow creation
- **Conditional Logic**: If-else branching and decision making
- **Data Transformation**: Transform and manipulate data between nodes
- **Error Handling**: Robust error handling and retry mechanisms

### 🌐 API & Integration
- **REST API**: Complete HTTP API for all operations
- **Visual Dashboard**: Compatible with React Flow and similar editors
- **JSON Workflows**: Standard JSON format for workflow definitions
- **Extensible**: Easy to add custom nodes and functionality

## Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/your-org/pocketflow.git
cd pocketflow

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your configuration
```

### Running the Workflow API

```bash
# Start the workflow API server
python run_workflow_api.py

# The API will be available at http://localhost:5000
```

### View Workflow Visualization

```bash
# See the left-to-right workflow flow
python3 show_workflow_visualization.py
```

### Basic Usage

#### Using Traditional PocketFlow Flows

```python
from pocketflow import create_flow, run_flow
from pocketflow.nodes.email import FetchEmailNode, SendEmailNode

# Create a traditional flow
flow = create_flow("Email Processing")
flow.add_step("fetch", FetchEmailNode())
flow.add_step("send", SendEmailNode())
flow.set_start("fetch")
flow.add_routing("fetch", "default", "send")
flow.add_end_step("send")

# Run the flow
shared = {"email_config": {...}}
result = run_flow("Email Processing", shared)
```

#### Using Visual Workflows

```python
# Create a workflow via API
import requests

workflow_data = {
    "name": "Email to LaTeX Report",
    "description": "Process emails and generate LaTeX reports",
    "nodes": [
        {
            "type": "EmailTriggerNode",
            "name": "Email Trigger",
            "position": {"x": 100, "y": 100},
            "data": {"host": "smtp.example.com"}
        },
        {
            "type": "GenerateLatexWorkflowNode", 
            "name": "Generate Report",
            "position": {"x": 300, "y": 100},
            "data": {"template": "report"}
        }
    ],
    "edges": [
        {
            "source": "node-1",
            "target": "node-2"
        }
    ]
}

response = requests.post("http://localhost:5000/api/workflows", json=workflow_data)
workflow = response.json()["workflow"]

# Run the workflow
run_response = requests.post(f"http://localhost:5000/api/workflows/{workflow['id']}/run")
result = run_response.json()
```

## Node Types

### Trigger Nodes
- **EmailTriggerNode**: Triggers when new emails are received
- **ScheduledTriggerNode**: Triggers on a schedule
- **ManualTriggerNode**: Manual trigger for testing

### Action Nodes
- **SendEmailWorkflowNode**: Send emails using PocketFlow email service
- **GenerateContentWorkflowNode**: Generate audio/image content
- **GenerateLatexWorkflowNode**: Create LaTeX documents
- **WebSearchWorkflowNode**: Search the web for information
- **HttpRequestWorkflowNode**: Make HTTP requests

### Control Nodes
- **IfElseWorkflowNode**: Conditional branching
- **TransformWorkflowNode**: Data transformation
- **DelayWorkflowNode**: Add delays to workflows
- **LogWorkflowNode**: Log data and messages

## API Documentation

### Base URL
```
http://localhost:5000/api
```

### Authentication
All endpoints use token-based authentication (inherited from original PocketFlow).

### Key Endpoints

#### Workflows
- `GET /api/workflows` - List all workflows
- `POST /api/workflows` - Create a new workflow
- `GET /api/workflows/{id}` - Get workflow details
- `PUT /api/workflows/{id}` - Update workflow
- `DELETE /api/workflows/{id}` - Delete workflow
- `POST /api/workflows/{id}/run` - Execute workflow

#### Nodes
- `GET /api/nodes` - List all available node types
- `GET /api/nodes/{type}` - Get node details
- `GET /api/nodes/categories` - Get nodes by category

#### Executions
- `GET /api/executions/{id}` - Get execution result

For complete API documentation, see [API Reference](workflows.md).

## Custom Node Development

Create custom nodes by extending the `WorkflowNode` class:

```python
from pocketflow.nodes.workflow.base import WorkflowActionNode, WorkflowNodeInput, WorkflowNodeOutput

class CustomActionNode(WorkflowActionNode):
    def execute_workflow(self, config, shared):
        # Your custom logic here
        return {"result": "success"}
    
    @classmethod
    def get_metadata(cls):
        return WorkflowNodeMetadata(
            name="CustomActionNode",
            description="A custom action node",
            category="action",
            inputs=[
                WorkflowNodeInput("input_field", "string", "Input description")
            ],
            outputs=[
                WorkflowNodeOutput("output_field", "string", "Output description")
            ]
        )
```

For detailed custom node development, see [Custom Node Guide](nodes.md).

## Configuration

PocketFlow uses the same configuration system as the original framework:

### Environment Variables
```bash
# Email Configuration
EMAIL_HOST=smtp.example.com
EMAIL_PORT=587
EMAIL_USERNAME=user@example.com
EMAIL_PASSWORD=password
EMAIL_USE_TLS=true

# API Configuration
SECRET_KEY=your-secret-key
DEBUG=false
HOST=0.0.0.0
PORT=5000
```

### Database
PocketFlow uses SQLite for storing workflows and execution history:
- Workflow definitions
- Execution results
- Logs and metadata

## Examples

### Email Processing Workflow
A workflow that monitors emails and generates LaTeX reports:

```json
{
  "name": "Email to LaTeX Report",
  "nodes": [
    {
      "type": "EmailTriggerNode",
      "name": "Email Trigger",
      "data": {"host": "smtp.example.com"}
    },
    {
      "type": "IfElseWorkflowNode",
      "name": "Check if Report Request",
      "data": {"condition": "contains", "value1": "{{email_body}}", "value2": "report"}
    },
    {
      "type": "WebSearchWorkflowNode",
      "name": "Search Information",
      "data": {"query": "{{email_subject}}"}
    },
    {
      "type": "GenerateLatexWorkflowNode",
      "name": "Generate Report",
      "data": {"template": "report", "content": "{{search_results}}"}
    }
  ],
  "edges": [
    {"source": "Email Trigger", "target": "Check if Report Request"},
    {"source": "Check if Report Request", "target": "Search Information", "condition": "true"},
    {"source": "Search Information", "target": "Generate Report"}
  ]
}
```

## Testing

Run the test suite to verify everything works:

```bash
# Run all tests
python -m pytest tests/

# Run specific test categories
python -m pytest tests/test_workflow_integration.py
python -m pytest tests/test_workflow_engine.py
```

## Architecture

### Core Components

```
┌─────────────────────────────────────────────────────────────┐
│                    Visual Dashboard                         │
│                 (React Flow / n8n-like)                     │
└─────────────────────┬───────────────────────────────────────┘
                      │ HTTP API
┌─────────────────────▼───────────────────────────────────────┐
│                    Workflow API                             │
│              (Flask REST API)                               │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│                  Workflow Engine                            │
│         (Converts visual workflows to PocketFlow flows)     │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│                Original PocketFlow                          │
│              (Flow, Node, Services)                         │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│                    Services                                 │
│         (Email, Content, Web Search, etc.)                  │
└─────────────────────────────────────────────────────────────┘
```

### Data Flow

1. **Visual Editor**: User creates workflow in visual interface
2. **Workflow API**: Receives workflow definition via REST API
3. **Workflow Engine**: Converts visual workflow to PocketFlow flow
4. **PocketFlow Flow**: Executes using original flow system
5. **Services**: Perform actual work (email, content generation, etc.)
6. **Results**: Returned through the same path

### Key Benefits

- **Backward Compatibility**: All existing PocketFlow functionality preserved
- **Visual Workflows**: Modern n8n-like interface for complex workflows
- **Hybrid Usage**: Use traditional flows or visual workflows as needed
- **Extensible**: Easy to add new nodes and capabilities
- **Robust**: Built on proven PocketFlow foundation

## Deployment

### Development
```bash
python run_workflow_api.py
```

### Production
```bash
# Use a production WSGI server
gunicorn -w 4 -b 0.0.0.0:5000 pocketflow.web.workflow_api:workflow_app
```

### Docker
```dockerfile
FROM python:3.9
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
EXPOSE 5000
CMD ["python", "run_workflow_api.py"]
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License

MIT License - see LICENSE file for details.

## Support

- **Documentation**: [API Reference](workflows.md), [Custom Nodes](nodes.md)
- **Visualization**: [Workflow Flow](workflow_visualization.md), [ASCII Examples](ascii_workflow.md)
- **Examples**: [Sample Workflows](data/workflows/)
- **Issues**: GitHub Issues
- **Discussions**: GitHub Discussions
