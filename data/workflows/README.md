# PocketFlow Workflows

This directory contains sample workflows and workflow templates for the PocketFlow n8n-like automation platform.

## Sample Workflows

### Email to LaTeX Report Workflow

**File**: `sample_workflow.json`

A comprehensive workflow that demonstrates the full capabilities of the PocketFlow system:

1. **EmailReceivedTrigger**: Monitors for new emails
2. **LogNode**: Logs email receipt for debugging
3. **IfElseNode**: Checks if the email contains a report request
4. **WebSearchAction**: Performs web search for relevant information
5. **GenerateLatexAction**: Generates a LaTeX report using templates
6. **SendEmailAction**: Sends the generated report via email
7. **LogNode**: Logs completion status

**Features**:
- Conditional processing based on email content
- Web research integration
- LaTeX document generation
- Automated email responses
- Comprehensive logging

**Use Case**: Automatically generate and send reports when users email requests for specific information.

## Workflow Structure

Each workflow JSON file contains:

```json
{
  "id": "unique-workflow-id",
  "name": "Workflow Name",
  "description": "Workflow description",
  "nodes": [
    {
      "id": "node-id",
      "type": "NodeType",
      "name": "Node Name",
      "position": {"x": 100, "y": 100},
      "data": {
        "parameter1": "value1",
        "parameter2": "value2"
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
    "author": "Author Name",
    "category": "category",
    "tags": ["tag1", "tag2"]
  },
  "createdAt": 1704067200,
  "updatedAt": 1704067200
}
```

## Using Sample Workflows

### Import a Workflow

```bash
# Import the sample workflow
curl -X POST http://localhost:5000/api/workflows \
  -H "Content-Type: application/json" \
  -d @sample_workflow.json
```

### Run a Workflow

```bash
# Execute the workflow
curl -X POST http://localhost:5000/api/workflows/workflow-id/run \
  -H "Content-Type: application/json" \
  -d '{
    "initial_data": {
      "custom_field": "test value"
    }
  }'
```

### Export a Workflow

```bash
# Export a workflow to JSON
curl -X GET http://localhost:5000/api/workflows/workflow-id \
  -H "Content-Type: application/json" > my_workflow.json
```

## Creating Custom Workflows

### 1. Plan Your Workflow

- Identify the trigger (what starts the workflow)
- Define the actions (what the workflow should do)
- Plan the data flow between nodes
- Consider error handling and logging

### 2. Choose Your Nodes

**Trigger Nodes**:
- `EmailReceivedTrigger`: Start on email receipt
- `ScheduledTrigger`: Start on schedule
- `ManualTrigger`: Manual execution

**Action Nodes**:
- `SendEmailAction`: Send emails
- `GenerateContentAction`: Create content
- `GenerateLatexAction`: Generate documents
- `WebSearchAction`: Search the web
- `HttpRequestAction`: Make API calls

**Condition Nodes**:
- `IfElseNode`: Conditional branching

**Transform Nodes**:
- `TransformNode`: Data manipulation
- `DelayNode`: Add delays
- `LogNode`: Logging and debugging

### 3. Configure Nodes

Each node has specific configuration parameters:

```json
{
  "type": "SendEmailAction",
  "name": "Send Reply",
  "data": {
    "to_email": "{{email_data.from}}",
    "subject": "Re: {{email_data.subject}}",
    "body": "Thank you for your email."
  }
}
```

### 4. Connect Nodes

Use edges to define the flow between nodes:

```json
{
  "source": "trigger-node-id",
  "target": "action-node-id",
  "sourceHandle": "email_data",
  "targetHandle": "input_data"
}
```

### 5. Test Your Workflow

1. Create the workflow via API
2. Run it with test data
3. Check the execution logs
4. Verify the results
5. Iterate and improve

## Workflow Best Practices

### 1. Error Handling

- Use `LogNode` to capture important information
- Add conditional logic for error cases
- Provide fallback actions for failed operations

### 2. Data Flow

- Use descriptive node names
- Document data transformations
- Validate data at each step

### 3. Performance

- Minimize unnecessary API calls
- Use appropriate delays for rate limiting
- Cache frequently used data

### 4. Security

- Validate all inputs
- Use environment variables for sensitive data
- Implement proper authentication

### 5. Monitoring

- Add logging at key points
- Monitor execution times
- Track success/failure rates

## Workflow Templates

### Email Processing Template

```json
{
  "name": "Email Processing Template",
  "nodes": [
    {
      "type": "EmailReceivedTrigger",
      "name": "Email Trigger"
    },
    {
      "type": "LogNode",
      "name": "Log Email"
    },
    {
      "type": "IfElseNode",
      "name": "Check Content"
    },
    {
      "type": "SendEmailAction",
      "name": "Send Response"
    }
  ]
}
```

### Content Generation Template

```json
{
  "name": "Content Generation Template",
  "nodes": [
    {
      "type": "ManualTrigger",
      "name": "Start"
    },
    {
      "type": "GenerateContentAction",
      "name": "Generate Content"
    },
    {
      "type": "GenerateLatexAction",
      "name": "Generate Report"
    },
    {
      "type": "SendEmailAction",
      "name": "Send Report"
    }
  ]
}
```

## Troubleshooting

### Common Issues

1. **Workflow Validation Errors**
   - Check that all node types are registered
   - Verify that edges connect valid nodes
   - Ensure no cycles in the workflow

2. **Execution Failures**
   - Check node configuration
   - Verify input data format
   - Review execution logs

3. **Data Flow Issues**
   - Confirm edge connections
   - Check node output formats
   - Validate shared state usage

### Debugging Tips

1. **Use LogNode** to track data flow
2. **Test nodes individually** before combining
3. **Check API responses** for error details
4. **Review execution logs** for timing issues
5. **Validate JSON format** before importing

## Contributing

To add new sample workflows:

1. Create a new JSON file with descriptive name
2. Include comprehensive documentation
3. Test the workflow thoroughly
4. Update this README with workflow details
5. Submit a pull request

## Resources

- **API Documentation**: [docs/workflows.md](../../docs/workflows.md)
- **Node Development**: [docs/nodes.md](../../docs/nodes.md)
- **Main Documentation**: [docs/index.md](../../docs/index.md)
- **API Server**: `http://localhost:5000/api` 