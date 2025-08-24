# PocketFlow Workflow - ASCII Visualization

## Left-to-Right Workflow Flow

```
┌─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                                                 VISUAL DASHBOARD                                                              │
│                                                                                                                                               │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐          │
│  │   TRIGGER   │───▶│    AGENT    │───▶│   ACTION    │───▶│ TRANSFORM   │───▶│   ACTION    │───▶│   LOG       │───▶│   RESULT    │          │
│  │             │    │             │    │             │    │             │    │             │    │             │    │             │          │
│  │EmailFetching│    │DecisionAgent│    │ContentCreator│   │TransformNode│    │MessageSending│   │PostProcessing│   │ Final       │          │
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
│  │   CREATE    │───▶│  VALIDATE   │───▶│   STORE     │───▶│   EXECUTE   │───▶│   MONITOR   │───▶│   LOG       │───▶│   RETURN    │          │
│  │ Workflow    │    │ Workflow    │    │ Workflow    │    │ Workflow    │    │ Progress    │    │ Results     │    │ Results     │          │
│  └─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘          │
│                                                                                                                                               │
└─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
                                        │
                                        ▼ Convert
┌─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                                              WORKFLOW ENGINE                                                                  │
│                                                                                                                                               │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐          │
│  │   PARSE     │───▶│  CONVERT    │───▶│   CREATE    │───▶│   VALIDATE  │───▶│   EXECUTE   │───▶│   MONITOR   │───▶│   RETURN    │          │
│  │ JSON        │    │ to Flow     │    │ Flow        │    │ Flow        │    │ Flow        │    │ Execution   │    │ Results     │          │
│  └─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘          │
│                                                                                                                                               │
└─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
                                        │
                                        ▼ Execute
┌─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                                           ORIGINAL POCKETFLOW                                                                 │
│                                                                                                                                               │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐          │
│  │   TRIGGER   │───▶│  PROCESS    │───▶│   ACTION    │───▶│ TRANSFORM   │───▶│   ACTION    │───▶│   LOG       │───▶│   RESULT    │          │
│  │             │    │             │    │             │    │             │    │             │    │             │    │             │          │
│  │FetchEmail   │    │Analyze      │    │WebSearch    │    │Transform    │    │GenerateLatex│    │LogResult    │    │FinalOutput  │          │
│  └─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘          │
│                                                                                                                                               │
└─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
                                        │
                                        ▼ Services
┌─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                                                   SERVICES                                                                    │
│                                                                                                                                               │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐          │
│  │   EMAIL     │    │   CONTENT   │    │   WEB       │    │   LLM       │    │   DATABASE  │    │   LOGGING   │    │   OUTPUT    │          │
│  │ Service     │    │ Generation  │    │ Search      │    │ Service     │    │ Service     │    │ Service     │    │ Service     │          │
│  └─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘          │
│                                                                                                                                               │
└─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

## Agent Workflow Example

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   EMAIL     │───▶│  DECISION   │───▶│  CONTENT    │───▶│  MESSAGE    │───▶│  POST       │───▶│   RESULT    │
│ FETCHING    │    │   AGENT     │    │  CREATOR    │    │  SENDING    │    │ PROCESSING  │    │             │
│             │    │             │    │             │    │             │    │             │    │             │
│ New Email   │    │ Analyze     │    │ Generate    │    │ Send Reply  │    │ Log &       │    │ Workflow    │
│ Received    │    │ & Decide    │    │ Content     │    │ to User     │    │ Cleanup     │    │ Complete    │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
```

## Investigation Workflow Example

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   EMAIL     │───▶│  DECISION   │───▶│INVESTIGATION│───▶│  MESSAGE    │───▶│  POST       │
│ FETCHING    │    │   AGENT     │    │             │    │  SENDING    │    │ PROCESSING  │
│             │    │             │    │             │    │             │    │             │
│ New Email   │    │ Analyze     │    │ Research    │    │ Send Report │    │ Log &       │
│ Received    │    │ & Decide    │    │ Topic       │    │ to User     │    │ Cleanup     │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
```

## Simple Email Processing Workflow

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   EMAIL     │───▶│  DECISION   │───▶│  MESSAGE    │───▶│  POST       │
│ FETCHING    │    │   AGENT     │    │  SENDING    │    │ PROCESSING  │
│             │    │             │    │             │    │             │
│ New Email   │    │ Simple      │    │ Send Reply  │    │ Log &       │
│ Received    │    │ Reply       │    │ to User     │    │ Cleanup     │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
```

## Content Generation Workflow

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   MANUAL    │───▶│  DECISION   │───▶│  CONTENT    │───▶│  MESSAGE    │───▶│  POST       │
│  TRIGGER    │    │   AGENT     │    │  CREATOR    │    │  SENDING    │    │ PROCESSING  │
│             │    │             │    │             │    │             │    │             │
│ User Input  │    │ Analyze     │    │ Create Doc  │    │ Send Doc    │    │ Log &       │
│             │    │ Request     │    │             │    │ to User     │    │ Cleanup     │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
```

## Data Flow Example

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   INPUT     │───▶│  PROCESS    │───▶│ TRANSFORM   │───▶│   OUTPUT    │
│             │    │             │    │             │    │             │
│ Email Data  │    │ Decision    │    │ Content     │    │ Response    │
│             │    │ Analysis    │    │ Generation  │    │ Sent        │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
```

## Agent Node Categories Flow

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│  TRIGGER    │───▶│    AGENT    │───▶│   ACTION    │───▶│ TRANSFORM   │
│             │    │             │    │             │    │             │
│EmailFetching│    │DecisionAgent│    │ContentCreator│   │PostProcessing│
│ Scheduled   │    │             │    │Investigation│   │             │
│ Manual      │    │             │    │MessageSending│   │             │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
```

## API Flow

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   HEALTH    │    │ WORKFLOWS   │    │   CREATE    │    │   EXECUTE   │
│             │    │             │    │             │    │             │
│ GET /health │    │GET /workflows│   │POST /workflows│  │POST /run    │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
```

## Key Points

1. **Left to Right**: All workflows flow naturally from left to right
2. **Layered**: Each layer builds on the previous one
3. **Visual**: The visual editor mirrors the actual execution
4. **Compatible**: Works with both traditional and visual workflows
5. **Extensible**: Easy to add new nodes and capabilities

## Agent Node Types

- **EmailFetchingNode**: Fetches new emails and triggers workflow execution
- **DecisionAgentNode**: AI agent that analyzes emails and makes routing decisions
- **ContentCreatorNode**: Creates various types of content (text, LaTeX, audio, images)
- **InvestigationNode**: Performs research and investigation on topics
- **MessageSendingNode**: Sends emails and other messages
- **PostProcessingNode**: Handles final processing, logging, and cleanup 