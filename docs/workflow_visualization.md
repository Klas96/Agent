# PocketFlow Workflow Visualization

## Left-to-Right Workflow Architecture

This document provides a visual representation of how PocketFlow workflows flow from left to right, showing both traditional flows and the new n8n-like visual workflow system.

## 1. Traditional PocketFlow Flow (Left to Right)

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Trigger   │───▶│   Process   │───▶│   Action    │───▶│    Result   │
│             │    │             │    │             │    │             │
│ FetchEmail  │    │ Analyze     │    │ SendEmail   │    │ Email Sent  │
│             │    │ Content     │    │             │    │             │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
```

### Traditional Flow Example

```python
# Traditional PocketFlow Flow (Left to Right)
flow = create_flow("Email Processing")
flow.add_step("fetch", FetchEmailNode())      # ← Left: Trigger
flow.add_step("analyze", AnalyzeNode())       # ← Middle: Process  
flow.add_step("send", SendEmailNode())        # ← Right: Action
flow.set_start("fetch")
flow.add_routing("fetch", "default", "analyze")
flow.add_routing("analyze", "default", "send")
flow.add_end_step("send")
```

## 2. n8n-like Visual Workflow (Left to Right)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        Visual Workflow Editor                                │
│                                                                             │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐  │
│  │   Trigger   │───▶│  Condition  │───▶│   Action    │───▶│   Log       │  │
│  │             │    │             │    │             │    │             │  │
│  │EmailTrigger │    │ IfElseNode  │    │GenerateLatex│    │ LogNode     │  │
│  │             │    │             │    │             │    │             │  │
│  └─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Visual Workflow JSON Example

```json
{
  "name": "Email to LaTeX Report",
  "nodes": [
    {
      "id": "trigger-1",
      "type": "EmailTriggerNode",
      "name": "Email Trigger",
      "position": {"x": 100, "y": 100},    // ← Left position
      "data": {"host": "smtp.example.com"}
    },
    {
      "id": "condition-1", 
      "type": "IfElseWorkflowNode",
      "name": "Check if Report Request",
      "position": {"x": 300, "y": 100},    // ← Middle position
      "data": {"condition": "contains", "value1": "{{email_body}}", "value2": "report"}
    },
    {
      "id": "action-1",
      "type": "GenerateLatexWorkflowNode",
      "name": "Generate Report", 
      "position": {"x": 500, "y": 100},    // ← Right position
      "data": {"template": "report"}
    },
    {
      "id": "log-1",
      "type": "LogWorkflowNode",
      "name": "Log Result",
      "position": {"x": 700, "y": 100},    // ← Far right position
      "data": {"message": "Report generated successfully"}
    }
  ],
  "edges": [
    {"source": "trigger-1", "target": "condition-1"},
    {"source": "condition-1", "target": "action-1", "condition": "true"},
    {"source": "action-1", "target": "log-1"}
  ]
}
```

## 3. Complete System Architecture (Left to Right)

```
┌─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                                                 VISUAL DASHBOARD                                                              │
│                                                                                                                                               │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐          │
│  │   Trigger   │───▶│  Condition  │───▶│   Action    │───▶│ Transform   │───▶│   Action    │───▶│   Log       │───▶│   Result    │          │
│  │             │    │             │    │             │    │             │    │             │    │             │    │             │          │
│  │EmailTrigger │    │ IfElseNode  │    │WebSearch    │    │TransformNode│    │GenerateLatex│    │ LogNode     │    │ Final       │          │
│  │             │    │             │    │             │    │             │    │             │    │             │    │ Output      │          │
│  └─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘          │
│                                                                                                                                               │
└─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
                                        │
                                        ▼ HTTP API
┌─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                                                 WORKFLOW API                                                                   │
│                                                                                                                                               │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐          │
│  │   Create    │───▶│  Validate   │───▶│   Store     │───▶│   Execute   │───▶│   Monitor   │───▶│   Log       │───▶│   Return    │          │
│  │ Workflow    │    │ Workflow    │    │ Workflow    │    │ Workflow    │    │ Progress    │    │ Results     │    │ Results     │          │
│  │             │    │             │    │             │    │             │    │             │    │             │    │             │          │
│  └─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘          │
│                                                                                                                                               │
└─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
                                        │
                                        ▼ Convert
┌─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                                              WORKFLOW ENGINE                                                                  │
│                                                                                                                                               │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐          │
│  │   Parse     │───▶│  Convert    │───▶│   Create    │───▶│   Validate  │───▶│   Execute   │───▶│   Monitor   │───▶│   Return    │          │
│  │ JSON        │    │ to Flow     │    │ Flow        │    │ Flow        │    │ Flow        │    │ Execution   │    │ Results     │          │
│  │             │    │             │    │             │    │             │    │             │    │             │    │             │          │
│  └─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘          │
│                                                                                                                                               │
└─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
                                        │
                                        ▼ Execute
┌─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                                           ORIGINAL POCKETFLOW                                                                 │
│                                                                                                                                               │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐          │
│  │   Trigger   │───▶│  Process    │───▶│   Action    │───▶│ Transform   │───▶│   Action    │───▶│   Log       │───▶│   Result    │          │
│  │             │    │             │    │             │    │             │    │             │    │             │    │             │          │
│  │FetchEmail   │    │Analyze      │    │WebSearch    │    │Transform    │    │GenerateLatex│    │LogResult    │    │FinalOutput  │          │
│  │             │    │             │    │             │    │             │    │             │    │             │    │             │          │
│  └─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘          │
│                                                                                                                                               │
└─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
                                        │
                                        ▼ Services
┌─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                                                   SERVICES                                                                    │
│                                                                                                                                               │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐          │
│  │   Email     │    │   Content   │    │   Web       │    │   LLM       │    │   Database  │    │   Logging   │    │   Output    │          │
│  │ Service     │    │ Generation  │    │ Search      │    │ Service     │    │ Service     │    │ Service     │    │ Service     │          │
│  │             │    │             │    │             │    │             │    │             │    │             │    │             │          │
│  └─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘          │
│                                                                                                                                               │
└─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

## 4. Data Flow Visualization (Left to Right)

```
┌─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                                                 DATA FLOW                                                                     │
│                                                                                                                                               │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐          │
│  │   Input     │───▶│  Process    │───▶│   Transform │───▶│   Validate  │───▶│   Generate  │───▶│   Store     │───▶│   Output    │          │
│  │             │    │             │    │             │    │             │    │             │    │             │    │             │          │
│  │Email Data   │    │Extract Info │    │Format Data  │    │Check Rules  │    │Create Doc   │    │Save Result  │    │Send Email   │          │
│  │             │    │             │    │             │    │             │    │             │    │             │    │             │          │
│  └─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘          │
│                                                                                                                                               │
└─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

## 5. Node Categories (Left to Right)

```
┌─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                                              NODE CATEGORIES                                                                 │
│                                                                                                                                               │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐          │
│  │  TRIGGER    │───▶│  CONDITION  │───▶│   ACTION    │───▶│ TRANSFORM   │───▶│   ACTION    │───▶│  CONDITION  │───▶│   ACTION    │          │
│  │             │    │             │    │             │    │             │    │             │    │             │    │             │          │
│  │EmailTrigger │    │ IfElseNode  │    │WebSearch    │    │TransformNode│    │GenerateLatex│    │ Validate    │    │ SendEmail   │          │
│  │Scheduled    │    │ Switch      │    │HttpRequest  │    │ Filter      │    │GenerateContent│  │ Check       │    │ LogResult   │          │
│  │Manual       │    │ Compare     │    │SendEmail    │    │ Map         │    │GenerateLatex│    │ Format      │    │ StoreData   │          │
│  └─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘          │
│                                                                                                                                               │
└─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

## 6. Execution Flow (Left to Right)

```
┌─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                                              EXECUTION FLOW                                                                  │
│                                                                                                                                               │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐          │
│  │   Start     │───▶│  Trigger    │───▶│  Condition  │───▶│   Action    │───▶│ Transform   │───▶│   Action    │───▶│    End      │          │
│  │             │    │             │    │             │    │             │    │             │    │             │    │             │          │
│  │Manual/Email │    │Check Email  │    │If Report    │    │Search Web   │    │Format Data  │    │Generate Doc │    │Send Result  │          │
│  │Scheduled    │    │Received     │    │Requested    │    │for Info     │    │for Template │    │from Data    │    │via Email    │          │
│  └─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘          │
│                                                                                                                                               │
└─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

## 7. API Endpoints (Left to Right)

```
┌─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                                              API ENDPOINTS                                                                   │
│                                                                                                                                               │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐          │
│  │   Health    │    │  Workflows  │    │   Create    │    │   Execute   │    │   Monitor   │    │   Results   │    │   Logs      │          │
│  │             │    │             │    │             │    │             │    │             │    │             │    │             │          │
│  │GET /health  │    │GET /workflows│   │POST /workflows│  │POST /run    │    │GET /status  │    │GET /results │    │GET /logs    │          │
│  │             │    │             │    │             │    │             │    │             │    │             │    │             │          │
│  └─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘          │
│                                                                                                                                               │
└─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

## 8. Development Workflow (Left to Right)

```
┌─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                                            DEVELOPMENT FLOW                                                                  │
│                                                                                                                                               │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐          │
│  │   Design    │───▶│  Develop    │───▶│   Test      │───▶│  Deploy     │───▶│   Monitor   │───▶│   Debug     │───▶│   Update    │          │
│  │             │    │             │    │             │    │             │    │             │    │             │    │             │          │
│  │Plan Workflow│    │Code Nodes   │    │Unit Tests   │    │API Server   │    │Logs & Metrics│   │Fix Issues   │    │New Features │          │
│  │             │    │             │    │Integration  │    │Database     │    │Performance  │    │Error Handling│   │Optimization │          │
│  └─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘          │
│                                                                                                                                               │
└─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

## Key Insights

1. **Left-to-Right Flow**: All workflows follow a natural left-to-right progression
2. **Layered Architecture**: Each layer builds on the previous one
3. **Data Transformation**: Data flows through nodes, being transformed at each step
4. **Visual Representation**: The visual editor mirrors the actual execution flow
5. **API Integration**: REST API provides programmatic access to the workflow system
6. **Backward Compatibility**: Original PocketFlow flows work alongside new visual workflows

This visualization shows how PocketFlow maintains its core functionality while adding powerful visual workflow capabilities that flow naturally from left to right. 