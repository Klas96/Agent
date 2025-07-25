# Enhanced Investigation + Report Workflow

## Overview

The system now supports a powerful two-step workflow where the agent can:
1. **Investigate** - Research and gather information about a topic
2. **Write Report** - Generate a professional document based on the investigation findings

This enhancement makes the document creator much more powerful by allowing users to request research-based reports.

## 🎯 Key Features

### 1. **Intelligent Workflow Detection**
The system automatically detects which workflow to use based on user requests:

- **Investigation + Report**: "Investigate what is happening in the world and give me a report"
- **Simple Investigation**: "What's the latest news about climate change?"
- **Direct Content Generation**: "Create a business report about AI"

### 2. **Enhanced Agent Actions**
The agent now supports sophisticated action sequences:

```json
[
  {
    "action": "investigate",
    "parameters": {
      "query": "current world events global news latest developments",
      "depth": "comprehensive"
    }
  },
  {
    "action": "generate",
    "parameters": {
      "type": "document",
      "prompt": "Create a comprehensive report based on the investigation findings about current world events",
      "research_based": true
    }
  },
  {
    "action": "send",
    "parameters": {
      "to": "user@example.com",
      "body": "Here's your comprehensive report on current world events based on my investigation!",
      "attachment": "<generated report file>"
    }
  },
  {
    "action": "finish",
    "parameters": {}
  }
]
```

### 3. **Research-Based Document Generation**
When documents are generated based on research findings:

- ✅ Enhanced prompts that incorporate research data
- ✅ Structured sections that use research findings
- ✅ Professional LaTeX formatting
- ✅ Automatic detection of research-based vs. regular documents

## 🔄 Supported Workflows

### 1. **Investigation + Report Workflow**
**Trigger**: User requests both investigation and report generation
**Example**: "Investigate what is happening in the world and give me a report"

**Actions**:
1. `investigate` - Comprehensive web search
2. `generate` - Create document based on findings
3. `send` - Send report as PDF attachment
4. `finish` - End conversation

### 2. **Simple Investigation Workflow**
**Trigger**: User just wants information
**Example**: "What's the latest news about climate change?"

**Actions**:
1. `investigate` - Web search for information
2. `send` - Share findings via email
3. `finish` - End conversation

### 3. **Direct Content Generation Workflow**
**Trigger**: User wants content without research
**Example**: "Create a business report about AI"

**Actions**:
1. `generate` - Create content directly
2. `send` - Send content as attachment
3. `finish` - End conversation

## 📊 Enhanced Document Types

### Research-Based Business Reports
- **Structure**: Executive Summary, Introduction, Analysis, Recommendations, Conclusion
- **Features**: Research context, data-supported analysis, research-backed conclusions
- **Use Case**: Market analysis, industry reports, business intelligence

### Research-Based Technical Reports
- **Structure**: Introduction, Methodology, Results, Discussion, Conclusion
- **Features**: Technical analysis, research methodology, data-driven insights
- **Use Case**: Technology trends, scientific analysis, technical documentation

### Research-Based General Reports
- **Structure**: Abstract, Main Content, Summary
- **Features**: Comprehensive coverage, research integration, professional formatting
- **Use Case**: News analysis, trend reports, general research summaries

## 🎯 Example Use Cases

### 1. **World Events Report**
```
User: "Investigate what is happening in the world and give me a report"
Agent: 
1. Investigates current global events
2. Generates comprehensive report with findings
3. Sends professional PDF report
```

### 2. **Technical Analysis**
```
User: "Research the latest AI developments and create a technical report"
Agent:
1. Investigates AI developments
2. Generates technical report with methodology
3. Sends detailed technical document
```

### 3. **Business Intelligence**
```
User: "Find out about market trends and write a business report"
Agent:
1. Investigates market trends
2. Generates business report with recommendations
3. Sends professional business document
```

### 4. **Simple Information Request**
```
User: "What's the latest news about climate change?"
Agent:
1. Investigates climate change news
2. Sends findings via email (no report needed)
```

## 🔧 Technical Implementation

### Enhanced Prompt System
The prompt system now supports three distinct workflows with clear examples:

1. **Investigation + Report Workflow**
2. **Simple Content Generation**
3. **Simple Investigation**

### Research-Based Document Service
The document service automatically detects research-based prompts and enhances the generation:

- **Enhanced Prompts**: Incorporate research findings throughout
- **Structured Sections**: Use research data to support analysis
- **Professional Formatting**: LaTeX templates ensure quality
- **Automatic Detection**: Distinguish research-based from regular documents

### Agent Decision Making
The agent intelligently determines workflow based on:

- **Keywords**: "investigate", "research", "report", "generate"
- **Context**: Whether research is needed
- **User Intent**: Whether content generation is requested

## 📈 Benefits

### For Users
- **Comprehensive Research**: Thorough investigation of topics
- **Professional Reports**: High-quality, well-structured documents
- **Data-Driven Insights**: Reports based on actual research findings
- **Seamless Experience**: One email request, complete workflow

### For System
- **Intelligent Routing**: Automatic workflow detection
- **Flexible Architecture**: Supports multiple workflow patterns
- **Professional Output**: LaTeX-based document generation
- **Scalable Design**: Easy to extend with new document types

## 🚀 Usage Examples

### Email Requests That Work

**Investigation + Report:**
- "Investigate what is happening in the world and give me a report"
- "Research the latest AI developments and create a technical report"
- "Find out about market trends and write a business report"
- "Investigate climate change and generate a comprehensive report"

**Simple Investigation:**
- "What's the latest news about AI?"
- "Find information about renewable energy"
- "Research current economic conditions"

**Direct Content Generation:**
- "Create a business report about AI"
- "Generate a technical document about machine learning"
- "Write a report about climate change"

## 🔄 Workflow Comparison

| Request Type | Investigation | Document Generation | Output |
|-------------|---------------|-------------------|---------|
| "Investigate X and give me a report" | ✅ Comprehensive | ✅ Research-based | 📄 Professional PDF |
| "What's the latest news about X?" | ✅ Targeted | ❌ None | 📧 Email response |
| "Create a report about X" | ❌ None | ✅ Direct generation | 📄 Professional PDF |

## 🎉 Success Criteria Met

✅ **Two-Step Workflow**: Investigation followed by report generation  
✅ **Intelligent Agent**: Automatic workflow detection and routing  
✅ **Research Integration**: Documents based on actual research findings  
✅ **Professional Output**: LaTeX-based document generation  
✅ **Flexible Architecture**: Supports multiple workflow patterns  
✅ **User-Friendly**: Simple email requests trigger complex workflows  

## 🔮 Future Enhancements

1. **Multi-Source Research**: Combine web search with database queries
2. **Advanced Templates**: More document types (proposals, manuals, etc.)
3. **Interactive Reports**: Reports with embedded charts and graphs
4. **Citation Management**: Automatic citation and reference generation
5. **Collaborative Workflows**: Multi-agent research and writing teams

## 📝 Conclusion

The enhanced investigation + report workflow significantly improves the system's capabilities by:

- **Supporting Research-Based Reports**: Users can request investigation + report workflows
- **Providing Professional Output**: LaTeX-based document generation ensures quality
- **Enabling Intelligent Routing**: Agent automatically determines appropriate workflow
- **Delivering Comprehensive Results**: Thorough research + professional documentation

Users can now send simple email requests like "Investigate what is happening in the world and give me a report" and receive comprehensive, research-based, professionally formatted PDF reports automatically. 