# PocketFlow Workflow Visualization

This directory contains visualizations that show how PocketFlow workflows flow from left to right, demonstrating the n8n-like system built on top of the original PocketFlow framework.

## 📊 Visualization Files

### 1. `workflow_visualization.md`
**Comprehensive visualization** showing the complete left-to-right workflow architecture:
- Visual Dashboard layer
- Workflow API layer  
- Workflow Engine layer
- Original PocketFlow layer
- Services layer

### 2. `ascii_workflow.md`
**ASCII art examples** showing simple workflow patterns:
- Email processing workflow
- Content generation workflow
- Data flow examples
- Node categories flow
- API flow

### 3. `show_workflow_visualization.py`
**Interactive script** to display the visualization in the terminal:
```bash
python3 show_workflow_visualization.py
```

## 🎯 Key Concepts Visualized

### Left-to-Right Flow
All workflows follow a natural left-to-right progression:

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   TRIGGER   │───▶│  CONDITION  │───▶│   ACTION    │───▶│   RESULT    │
│             │    │             │    │             │    │             │
│ EmailTrigger│    │ IfElseNode  │    │WebSearch    │    │ Final Output│
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
```

### Layered Architecture
Each layer builds on the previous one:

```
Visual Dashboard
       │
       ▼ HTTP API
Workflow API  
       │
       ▼ Convert
Workflow Engine
       │
       ▼ Execute
Original PocketFlow
       │
       ▼ Services
Services
```

### Node Categories
Different types of nodes serve different purposes:

- **TRIGGER**: Start workflows (Email, Scheduled, Manual)
- **CONDITION**: Make decisions (If/Else, Switch, Compare)  
- **ACTION**: Perform tasks (Web Search, Send Email, Generate Content)
- **TRANSFORM**: Modify data (Filter, Map, Format)

## 🚀 Quick Start

1. **View the visualization**:
   ```bash
   python3 show_workflow_visualization.py
   ```

2. **Read the detailed documentation**:
   - `workflow_visualization.md` - Complete architecture overview
   - `ascii_workflow.md` - Simple examples and patterns

3. **Understand the flow**:
   - Visual Dashboard → User creates workflow visually
   - Workflow API → Receives workflow via REST API
   - Workflow Engine → Converts visual workflow to PocketFlow flow
   - Original PocketFlow → Executes using proven flow system
   - Services → Perform actual work (email, content, etc.)

## 💡 Benefits Visualized

- ✅ **Backward Compatibility**: All existing PocketFlow functionality preserved
- ✅ **Visual Workflows**: Modern n8n-like interface for complex workflows
- ✅ **Hybrid Usage**: Use traditional flows or visual workflows as needed
- ✅ **Extensible**: Easy to add new nodes and capabilities
- ✅ **Robust**: Built on proven PocketFlow foundation

## 🔗 Related Documentation

- [Main Documentation](../index.md) - Overview of PocketFlow
- [API Documentation](workflows.md) - REST API reference
- [Custom Node Guide](nodes.md) - How to create custom nodes
- [Sample Workflows](../data/workflows/) - Example workflow definitions

---

**PocketFlow** - Transform your workflows with AI-powered automation, now with visual workflow capabilities! 🚀 