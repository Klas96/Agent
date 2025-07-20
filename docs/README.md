# PocketFlow Documentation

## Overview

PocketFlow is a modular email processing and content generation system that provides:

- **Modular Architecture**: Clean separation of concerns with reusable components
- **Service Layer**: External integrations for email, LLM, content generation, Bitcoin, and web search
- **Dynamic Flow Selection**: Intelligent flow routing based on user type and content
- **Token-Based Management**: Different flows for users with and without tokens
- **Type Safety**: Comprehensive type hints and Pydantic models
- **Performance Monitoring**: Built-in performance tracking and metrics

## Architecture

### Core Components

```
PocketFlow/
├── core/           # Core types and flow engine
├── nodes/          # Modular node implementations
├── services/       # External service integrations
├── flows/          # Production-ready flow definitions
├── config/         # Configuration management
└── utils/          # Utilities and helpers
```

### Key Concepts

1. **Flows**: High-level workflows that orchestrate nodes
2. **Nodes**: Individual processing units with specific responsibilities
3. **Services**: External integrations (email, LLM, content, etc.)
4. **Shared State**: Data passed between nodes in a flow
5. **Flow Types**: Different user states (tokened, tokenless, payment pending)

## Quick Start

### Basic Usage

```python
from pocketflow import SharedState, FlowType, run_auto_select

# Create shared state with email context
shared = SharedState(
    user="user@example.com",
    flow_type=FlowType.TOKENED_USER,
    email={
        "id": "email_1",
        "from": "user@example.com",
        "to": "assistant@example.com",
        "subject": "Generate a song",
        "body": "Please generate a 2-minute song in the style of Daft Punk.",
        "thread_id": "thread_1"
    }
)

# Run with auto-selection
result = run_auto_select(shared)

if result["success"]:
    print("Flow completed successfully!")
else:
    print(f"Flow failed: {result['error']}")
```

### Manual Flow Selection

```python
from pocketflow import run_flow

# Run specific flow
result = run_flow("content_generation", shared)
```

## Flows

### Available Flows

1. **Email Processor Flow** (`email_processor`)
   - Complete email processing pipeline
   - Handles all types of requests
   - Full conversation management

2. **Tokenless User Flow** (`tokenless_user`)
   - For users without tokens
   - Redirects to payment requests
   - Restricted functionality

3. **Content Generation Flow** (`content_generation`)
   - Specialized for content creation
   - Optimized for audio, image, document generation
   - Content type detection

4. **Investigation Flow** (`investigation`)
   - Specialized for web search and research
   - Result summarization
   - Information gathering

5. **Payment Processing Flow** (`payment_processing`)
   - Bitcoin payment handling
   - Address management
   - Payment tracking

### Flow Selection Logic

The system automatically selects flows based on:

- **User Type**: Tokened vs tokenless users
- **Content Keywords**: "generate", "create", "research", "investigate"
- **Flow Type**: Email processing, payment, investigation
- **Request Context**: Email body analysis

## Nodes

### Email Nodes

- **FetchEmailNode**: Fetches and processes unread emails
- **SendEmailNode**: Sends emails with threading and attachments
- **ConversationContextNode**: Manages conversation history

### Agent Nodes

- **AgentNode**: LLM interactions and action extraction
- **PopAgentActionNode**: Action queue management

### Content Nodes

- **ContentCreatorNode**: Determines content subtypes
- **ContentParamNode**: Prepares generation parameters
- **GenerateContentNode**: Generates content using services

### Investigation Nodes

- **InvestigateTopicNode**: Web search and investigation

### Bitcoin Nodes

- **PurchaseTokensWithBitcoinNode**: Bitcoin payment requests

## Services

### Email Service

```python
from pocketflow.services import email_service

# Fetch unread emails
emails = email_service.fetch_unread_emails()

# Send email
success = email_service.send_email(email_request)
```

### LLM Service

```python
from pocketflow.services import llm_service

# Call LLM
response = llm_service.call_llm(messages)

# Extract actions
actions = llm_service.extract_actions(response)
```

### Content Service

```python
from pocketflow.services import content_service

# Generate content
file_path = content_service.generate_content(content_request)
```

### Bitcoin Service

```python
from pocketflow.services import bitcoin_service

# Get or create address
address = bitcoin_service.get_or_create_address(user_email)

# Create payment request
payment_info = bitcoin_service.create_payment_request(payment_request)
```

### Web Search Service

```python
from pocketflow.services import websearch_service

# Search web
results = websearch_service.search(investigation_request)

# Summarize results
summary = websearch_service.summarize_results(results)
```

## Configuration

### Environment Configuration

```yaml
# config/development.yaml
email:
  imap_host: "imap.gmail.com"
  smtp_host: "smtp.gmail.com"
  username: "your-email@gmail.com"
  password: "your-password"

llm:
  openai_api_key: "your-openai-key"
  google_api_key: "your-google-key"

bitcoin:
  wallet_path: "/path/to/wallet"
  network: "testnet"
```

### Flow Configuration

```yaml
# config/flows.yaml
flows:
  email_processor:
    type: "TOKENED_USER"
    requires_tokens: true
    steps:
      - fetch_email
      - conversation_context
      - agent
      - pop_action
      - content_creator
      - content_params
      - generate_content
      - investigate
      - send_email
```

## Performance Monitoring

### Built-in Monitoring

```python
from pocketflow.utils.performance import performance_monitor

# Get performance metrics
metrics = performance_monitor.get_metrics("email_processor")
print(f"Success rate: {metrics['summary']['success_rate']:.2%}")
```

### Performance Decorators

```python
from pocketflow.utils.performance import monitor_performance, monitor_flow_performance

@monitor_performance("my_function")
def my_function():
    # Function implementation
    pass

@monitor_flow_performance("email_processor")
def run_email_processor(shared):
    # Flow implementation
    pass
```

## Error Handling

### Custom Exceptions

```python
from pocketflow.utils.errors import (
    PocketFlowError,
    EmailError,
    LLMError,
    ContentGenerationError,
    BitcoinError,
    WebSearchError
)

try:
    result = run_flow("email_processor", shared)
except EmailError as e:
    print(f"Email error: {e}")
except LLMError as e:
    print(f"LLM error: {e}")
```

### Error Recovery

The system includes automatic error recovery:

- Retry logic for transient failures
- Fallback mechanisms for service failures
- Graceful degradation for partial failures
- Comprehensive error logging

## Testing

### Unit Tests

```python
# tests/unit/test_email_processor.py
import pytest
from pocketflow.flows import EmailProcessorFlow

def test_email_processor_flow():
    flow = EmailProcessorFlow()
    shared = SharedState(user="test@example.com")
    result = flow.run(shared)
    assert result["success"] == True
```

### Integration Tests

```python
# tests/integration/test_full_pipeline.py
def test_full_pipeline():
    shared = create_test_shared_state()
    result = run_auto_select(shared)
    assert result["success"] == True
    assert "attachment" in result["final_state"]
```

## Migration Guide

### From Old System

1. **Update Imports**:
   ```python
   # Old
   from nodes import FetchEmailNode
   
   # New
   from pocketflow.nodes import FetchEmailNode
   ```

2. **Update Flow Creation**:
   ```python
   # Old
   flow = create_flow("my_flow")
   
   # New
   flow = create_flow("my_flow", FlowType.TOKENED_USER)
   ```

3. **Update Configuration**:
   ```python
   # Old
   config = load_config()
   
   # New
   config = get_config()
   ```

### Breaking Changes

- Node interfaces have changed to use services
- Flow routing is now configuration-driven
- Error handling uses custom exceptions
- Type hints are required for all functions

## Best Practices

### Flow Design

1. **Keep flows focused**: Each flow should have a specific purpose
2. **Use appropriate flow types**: Match flow type to user state
3. **Handle errors gracefully**: Include error recovery mechanisms
4. **Monitor performance**: Use performance decorators for critical paths

### Node Development

1. **Use services**: Don't implement external integrations directly
2. **Handle errors**: Catch and re-raise with appropriate exceptions
3. **Add type hints**: All functions should have complete type annotations
4. **Log appropriately**: Use structured logging with context

### Service Integration

1. **Implement interfaces**: All services should implement the base interface
2. **Handle timeouts**: Include timeout handling for external calls
3. **Add retry logic**: Implement exponential backoff for transient failures
4. **Validate inputs**: Use Pydantic models for request validation

## Troubleshooting

### Common Issues

1. **Flow Selection Issues**:
   - Check user flow type in shared state
   - Verify email content for keyword detection
   - Review flow routing configuration

2. **Service Connection Issues**:
   - Verify service configuration
   - Check network connectivity
   - Review authentication credentials

3. **Performance Issues**:
   - Monitor performance metrics
   - Check for bottlenecks in flow execution
   - Review service response times

### Debug Mode

```python
from pocketflow.utils.logging import setup_logging

# Enable debug logging
setup_logging(level="DEBUG", log_format="detailed")
```

## API Reference

### Core Types

- `SharedState`: Data container for flow execution
- `FlowType`: Enum for different flow types
- `EmailData`: Email message structure
- `ContentGenerationRequest`: Content generation parameters
- `PaymentRequest`: Bitcoin payment parameters

### Core Classes

- `Flow`: Base flow class
- `FlowBuilder`: Flow construction helper
- `Node`: Base node class
- `SimpleNode`: Simplified node implementation

### Utility Functions

- `create_flow()`: Create a new flow builder
- `run_flow()`: Run a specific flow
- `run_auto_select()`: Auto-select and run appropriate flow
- `get_available_flows()`: Get information about all flows
- `get_flow_info()`: Get information about a specific flow

## Contributing

### Development Setup

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Set up configuration files
4. Run tests: `pytest tests/`

### Code Style

- Use type hints for all functions
- Follow PEP 8 style guidelines
- Add docstrings for all public functions
- Include unit tests for new features

### Pull Request Process

1. Create feature branch
2. Add tests for new functionality
3. Update documentation
4. Submit pull request with description

## License

This project is licensed under the MIT License - see the LICENSE file for details. 