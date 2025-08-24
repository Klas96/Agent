# PocketFlow Custom Node Development

This document describes how to create custom nodes for the PocketFlow n8n-like workflow automation platform.

## Overview

Custom nodes allow you to extend the workflow system with your own functionality. Each node is a Python class that inherits from one of the base node classes and implements the required methods.

## Node Base Classes

### BaseNode

The base class for all nodes. Provides common functionality and abstract methods.

```python
from abc import ABC, abstractmethod
from typing import Dict, Any
from ..core.types import SharedState

class BaseNode(ABC):
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = get_logger(f"Node.{self.__class__.__name__}")
    
    @abstractmethod
    def execute(self, shared: SharedState) -> Dict[str, Any]:
        """Execute the node logic."""
        pass
    
    @classmethod
    def get_metadata(cls) -> NodeMetadata:
        """Get metadata for this node type."""
        pass
```

### TriggerNode

Base class for trigger nodes that start workflows.

```python
class TriggerNode(BaseNode):
    """Base class for trigger nodes."""
    pass
```

### ActionNode

Base class for action nodes that perform tasks.

```python
class ActionNode(BaseNode):
    """Base class for action nodes."""
    pass
```

### ConditionNode

Base class for condition nodes that route workflow execution.

```python
class ConditionNode(BaseNode):
    """Base class for condition nodes."""
    pass
```

### TransformNode

Base class for transform nodes that modify data.

```python
class TransformNode(BaseNode):
    """Base class for transform nodes."""
    pass
```

## Creating a Custom Node

### Step 1: Define the Node Class

Create a new Python file in `src/pocketflow/nodes/custom/`:

```python
# src/pocketflow/nodes/custom/my_custom_node.py

from typing import Dict, Any
from ..base import ActionNode, NodeInput, NodeOutput, NodeMetadata
from ...core.types import SharedState
from ...utils.logging import get_logger


class MyCustomNode(ActionNode):
    """
    A custom node that performs a specific task.
    """
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        # Initialize any services or dependencies here
    
    def execute(self, shared: SharedState) -> Dict[str, Any]:
        """
        Execute the node logic.
        
        Args:
            shared: Shared state that can be read from and written to
            
        Returns:
            Dictionary containing the execution result and any outputs
        """
        try:
            # Get input values from configuration
            input_value = self.get_input_value("input_field", "")
            
            # Perform the node's logic
            result = self._process_data(input_value)
            
            # Set outputs in shared state
            self.set_output(shared, "processed_data", result)
            self.set_output(shared, "status", "completed")
            
            return {
                "success": True,
                "processed_data": result,
                "message": "Data processed successfully"
            }
            
        except Exception as e:
            self.logger.error(f"Error in MyCustomNode: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _process_data(self, data: str) -> str:
        """Process the input data."""
        # Implement your custom logic here
        return f"Processed: {data.upper()}"
    
    @classmethod
    def get_metadata(cls) -> NodeMetadata:
        """Get metadata for this node type."""
        return NodeMetadata(
            name="MyCustomNode",
            description="A custom node that processes data",
            category="action",
            version="1.0.0",
            author="Your Name",
            inputs=[
                NodeInput("input_field", "string", "Input data to process", True),
                NodeInput("optional_field", "number", "Optional parameter", False, 10)
            ],
            outputs=[
                NodeOutput("processed_data", "string", "Processed data result"),
                NodeOutput("status", "string", "Processing status")
            ],
            icon="custom",
            color="#FF5722"
        )
```

### Step 2: Register the Node

Add your node to the node registry in `src/pocketflow/nodes/__init__.py`:

```python
# In src/pocketflow/nodes/__init__.py

from .custom.my_custom_node import MyCustomNode

class NodeRegistry:
    def _register_default_nodes(self):
        """Register all default node types."""
        # ... existing registrations ...
        
        # Register custom nodes
        self.register_node("MyCustomNode", MyCustomNode)
```

### Step 3: Test Your Node

Create a test for your custom node:

```python
# tests/test_custom_nodes.py

import pytest
from src.pocketflow.nodes.custom.my_custom_node import MyCustomNode
from src.pocketflow.core.types import SharedState


def test_my_custom_node():
    """Test the MyCustomNode functionality."""
    # Create node with configuration
    config = {
        "input_field": "test data",
        "optional_field": 5
    }
    node = MyCustomNode(config)
    
    # Create shared state
    shared = SharedState()
    
    # Execute node
    result = node.execute(shared)
    
    # Assert results
    assert result["success"] is True
    assert result["processed_data"] == "Processed: TEST DATA"
    assert shared.get("outputs", {}).get("processed_data") == "Processed: TEST DATA"
    assert shared.get("outputs", {}).get("status") == "completed"


def test_my_custom_node_metadata():
    """Test the MyCustomNode metadata."""
    metadata = MyCustomNode.get_metadata()
    
    assert metadata.name == "MyCustomNode"
    assert metadata.category == "action"
    assert len(metadata.inputs) == 2
    assert len(metadata.outputs) == 2
```

## Node Categories

### Trigger Nodes

Trigger nodes start workflows and typically monitor external events:

```python
class MyTriggerNode(TriggerNode):
    def execute(self, shared: SharedState) -> Dict[str, Any]:
        # Check for trigger condition
        if self._should_trigger():
            # Set trigger data in shared state
            shared["trigger_data"] = self._get_trigger_data()
            return {"triggered": True, "data": self._get_trigger_data()}
        else:
            return {"triggered": False}
```

### Action Nodes

Action nodes perform specific tasks:

```python
class MyActionNode(ActionNode):
    def execute(self, shared: SharedState) -> Dict[str, Any]:
        # Get input from shared state or configuration
        input_data = self.get_input_value("input_data")
        
        # Perform action
        result = self._perform_action(input_data)
        
        # Set outputs
        self.set_output(shared, "result", result)
        
        return {"success": True, "result": result}
```

### Condition Nodes

Condition nodes evaluate conditions and route execution:

```python
class MyConditionNode(ConditionNode):
    def execute(self, shared: SharedState) -> Dict[str, Any]:
        # Evaluate condition
        condition_result = self._evaluate_condition()
        
        # Set condition result
        self.set_output(shared, "condition_result", condition_result)
        
        return {
            "success": True,
            "condition_result": condition_result,
            "route": "true" if condition_result else "false"
        }
```

### Transform Nodes

Transform nodes modify data without performing external actions:

```python
class MyTransformNode(TransformNode):
    def execute(self, shared: SharedState) -> Dict[str, Any]:
        # Get input data
        input_data = self.get_input_value("input_data")
        
        # Transform data
        transformed_data = self._transform_data(input_data)
        
        # Set output
        self.set_output(shared, "transformed_data", transformed_data)
        
        return {"success": True, "transformed_data": transformed_data}
```

## Node Configuration

### Input Parameters

Define input parameters using `NodeInput`:

```python
NodeInput(
    name="parameter_name",      # Parameter name
    type="string",             # Parameter type (string, number, boolean, object, array)
    description="Description",  # Parameter description
    required=True,             # Whether parameter is required
    default="default_value"    # Default value (optional)
)
```

### Output Parameters

Define output parameters using `NodeOutput`:

```python
NodeOutput(
    name="output_name",        # Output name
    type="string",             # Output type
    description="Description"  # Output description
)
```

### Node Metadata

Define node metadata using `NodeMetadata`:

```python
NodeMetadata(
    name="NodeName",           # Node class name
    description="Description", # Node description
    category="action",         # Node category (trigger, action, condition, transform)
    version="1.0.0",          # Node version
    author="Author Name",      # Node author
    inputs=[...],             # List of NodeInput objects
    outputs=[...],            # List of NodeOutput objects
    icon="icon_name",         # Icon name for UI
    color="#FF5722"           # Color for UI
)
```

## Best Practices

### 1. Error Handling

Always handle errors gracefully:

```python
def execute(self, shared: SharedState) -> Dict[str, Any]:
    try:
        # Node logic here
        return {"success": True, "result": result}
    except Exception as e:
        self.logger.error(f"Error in {self.__class__.__name__}: {e}")
        return {"success": False, "error": str(e)}
```

### 2. Input Validation

Validate inputs before processing:

```python
def execute(self, shared: SharedState) -> Dict[str, Any]:
    # Validate required inputs
    required_input = self.get_input_value("required_field")
    if not required_input:
        return {"success": False, "error": "Required field is missing"}
    
    # Process with validated input
    result = self._process(required_input)
    return {"success": True, "result": result}
```

### 3. Logging

Use the built-in logger for debugging:

```python
def execute(self, shared: SharedState) -> Dict[str, Any]:
    self.logger.info(f"Starting {self.__class__.__name__} execution")
    
    # Node logic here
    
    self.logger.info(f"Completed {self.__class__.__name__} execution")
    return {"success": True}
```

### 4. Shared State Management

Use shared state for data passing between nodes:

```python
def execute(self, shared: SharedState) -> Dict[str, Any]:
    # Read from shared state
    previous_result = shared.get("previous_node_output")
    
    # Process data
    result = self._process(previous_result)
    
    # Write to shared state
    self.set_output(shared, "my_output", result)
    
    return {"success": True, "result": result}
```

### 5. Configuration Management

Use the configuration system for node parameters:

```python
def execute(self, shared: SharedState) -> Dict[str, Any]:
    # Get configuration values with defaults
    timeout = self.get_input_value("timeout", 30)
    retries = self.get_input_value("retries", 3)
    
    # Use configuration in node logic
    result = self._process_with_config(timeout, retries)
    
    return {"success": True, "result": result}
```

## Example: Custom Email Filter Node

Here's a complete example of a custom node that filters emails:

```python
# src/pocketflow/nodes/custom/email_filter_node.py

from typing import Dict, Any
from ..base import ConditionNode, NodeInput, NodeOutput, NodeMetadata
from ...core.types import SharedState
from ...utils.logging import get_logger


class EmailFilterNode(ConditionNode):
    """
    Filters emails based on criteria like sender, subject, or content.
    """
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
    
    def execute(self, shared: SharedState) -> Dict[str, Any]:
        """Filter email based on configured criteria."""
        try:
            # Get email data from shared state
            email_data = shared.get("email", {})
            if not email_data:
                return {"success": False, "error": "No email data found"}
            
            # Get filter criteria from configuration
            filter_field = self.get_input_value("filter_field", "subject")
            filter_operator = self.get_input_value("filter_operator", "contains")
            filter_value = self.get_input_value("filter_value", "")
            
            # Apply filter
            passes_filter = self._apply_filter(
                email_data.get(filter_field, ""),
                filter_operator,
                filter_value
            )
            
            # Set outputs
            self.set_output(shared, "filter_result", passes_filter)
            self.set_output(shared, "filtered_email", email_data if passes_filter else None)
            
            return {
                "success": True,
                "filter_result": passes_filter,
                "message": f"Email {'passed' if passes_filter else 'failed'} filter"
            }
            
        except Exception as e:
            self.logger.error(f"Error in EmailFilterNode: {e}")
            return {"success": False, "error": str(e)}
    
    def _apply_filter(self, field_value: str, operator: str, filter_value: str) -> bool:
        """Apply the specified filter."""
        if operator == "contains":
            return filter_value.lower() in field_value.lower()
        elif operator == "equals":
            return field_value.lower() == filter_value.lower()
        elif operator == "starts_with":
            return field_value.lower().startswith(filter_value.lower())
        elif operator == "ends_with":
            return field_value.lower().endswith(filter_value.lower())
        elif operator == "regex":
            import re
            return bool(re.search(filter_value, field_value, re.IGNORECASE))
        else:
            return False
    
    @classmethod
    def get_metadata(cls) -> NodeMetadata:
        """Get metadata for EmailFilterNode."""
        return NodeMetadata(
            name="EmailFilterNode",
            description="Filters emails based on configurable criteria",
            category="condition",
            version="1.0.0",
            author="PocketFlow",
            inputs=[
                NodeInput("filter_field", "string", "Email field to filter on", False, "subject"),
                NodeInput("filter_operator", "string", "Filter operator", False, "contains"),
                NodeInput("filter_value", "string", "Value to filter for", True)
            ],
            outputs=[
                NodeOutput("filter_result", "boolean", "Whether email passed the filter"),
                NodeOutput("filtered_email", "object", "Email data if passed filter")
            ],
            icon="filter",
            color="#FF9800"
        )
```

## Testing Custom Nodes

Create comprehensive tests for your custom nodes:

```python
# tests/test_email_filter_node.py

import pytest
from src.pocketflow.nodes.custom.email_filter_node import EmailFilterNode
from src.pocketflow.core.types import SharedState


def test_email_filter_contains():
    """Test email filter with contains operator."""
    config = {
        "filter_field": "subject",
        "filter_operator": "contains",
        "filter_value": "urgent"
    }
    node = EmailFilterNode(config)
    
    shared = SharedState()
    shared["email"] = {
        "subject": "Urgent meeting tomorrow",
        "from": "boss@company.com",
        "body": "Please attend the urgent meeting"
    }
    
    result = node.execute(shared)
    
    assert result["success"] is True
    assert result["filter_result"] is True
    assert shared["outputs"]["filter_result"] is True


def test_email_filter_equals():
    """Test email filter with equals operator."""
    config = {
        "filter_field": "from",
        "filter_operator": "equals",
        "filter_value": "boss@company.com"
    }
    node = EmailFilterNode(config)
    
    shared = SharedState()
    shared["email"] = {
        "subject": "Meeting",
        "from": "boss@company.com",
        "body": "Meeting details"
    }
    
    result = node.execute(shared)
    
    assert result["success"] is True
    assert result["filter_result"] is True


def test_email_filter_no_email_data():
    """Test email filter with no email data."""
    config = {
        "filter_field": "subject",
        "filter_operator": "contains",
        "filter_value": "urgent"
    }
    node = EmailFilterNode(config)
    
    shared = SharedState()
    
    result = node.execute(shared)
    
    assert result["success"] is False
    assert "No email data found" in result["error"]
```

## Deployment

After creating your custom node:

1. **Add to node registry**: Update `src/pocketflow/nodes/__init__.py`
2. **Write tests**: Create comprehensive tests
3. **Update documentation**: Document your node's functionality
4. **Test in workflow**: Create a test workflow using your node
5. **Deploy**: Deploy with the rest of the PocketFlow system

## Node Icons and Colors

Use consistent icons and colors for your nodes:

- **Icons**: Use standard icon names (email, search, create, etc.)
- **Colors**: Use hex color codes that match the node category
  - Trigger nodes: Green (#4CAF50)
  - Action nodes: Blue (#2196F3)
  - Condition nodes: Orange (#FF9800)
  - Transform nodes: Purple (#9C27B0)

This ensures a consistent and professional appearance in the workflow editor. 