#!/usr/bin/env python3
"""
Script to display PocketFlow workflow visualization in the terminal.
This shows the left-to-right workflow flow from visual dashboard to services.
"""

import os
import sys
from pathlib import Path

def print_header(title):
    """Print a formatted header."""
    print("\n" + "="*80)
    print(f" {title}")
    print("="*80)

def print_workflow_visualization():
    """Print the main workflow visualization."""
    print_header("POCKETFLOW WORKFLOW VISUALIZATION - LEFT TO RIGHT")
    
    print("""
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
""")

def print_agent_workflows():
    """Print agent workflow examples."""
    print_header("AGENT WORKFLOW EXAMPLES")
    
    print("""
🤖 COMPLETE AGENT WORKFLOW:
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   EMAIL     │───▶│  DECISION   │───▶│  CONTENT    │───▶│  MESSAGE    │───▶│  POST       │───▶│   RESULT    │
│ FETCHING    │    │   AGENT     │    │  CREATOR    │    │  SENDING    │    │ PROCESSING  │    │             │
│             │    │             │    │             │    │             │    │             │    │             │
│ New Email   │    │ Analyze     │    │ Generate    │    │ Send Reply  │    │ Log &       │    │ Workflow    │
│ Received    │    │ & Decide    │    │ Content     │    │ to User     │    │ Cleanup     │    │ Complete    │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘

🔍 INVESTIGATION WORKFLOW:
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   EMAIL     │───▶│  DECISION   │───▶│INVESTIGATION│───▶│  MESSAGE    │───▶│  POST       │
│ FETCHING    │    │   AGENT     │    │             │    │  SENDING    │    │ PROCESSING  │
│             │    │             │    │             │    │             │    │             │
│ New Email   │    │ Analyze     │    │ Research    │    │ Send Report │    │ Log &       │
│ Received    │    │ & Decide    │    │ Topic       │    │ to User     │    │ Cleanup     │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘

📧 SIMPLE EMAIL PROCESSING:
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   EMAIL     │───▶│  DECISION   │───▶│  MESSAGE    │───▶│  POST       │
│ FETCHING    │    │   AGENT     │    │  SENDING    │    │ PROCESSING  │
│             │    │             │    │             │    │             │
│ New Email   │    │ Simple      │    │ Send Reply  │    │ Log &       │
│ Received    │    │ Reply       │    │ to User     │    │ Cleanup     │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘

🎨 CONTENT GENERATION:
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   MANUAL    │───▶│  DECISION   │───▶│  CONTENT    │───▶│  MESSAGE    │───▶│  POST       │
│  TRIGGER    │    │   AGENT     │    │  CREATOR    │    │  SENDING    │    │ PROCESSING  │
│             │    │             │    │             │    │             │    │             │
│ User Input  │    │ Analyze     │    │ Create Doc  │    │ Send Doc    │    │ Log &       │
│             │    │ Request     │    │             │    │ to User     │    │ Cleanup     │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
""")

def print_node_categories():
    """Print node categories flow."""
    print_header("AGENT NODE CATEGORIES")
    
    print("""
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│  TRIGGER    │───▶│    AGENT    │───▶│   ACTION    │───▶│ TRANSFORM   │
│             │    │             │    │             │    │             │
│EmailFetching│    │DecisionAgent│    │ContentCreator│   │PostProcessing│
│ Scheduled   │    │             │    │Investigation│   │             │
│ Manual      │    │             │    │MessageSending│   │             │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘

🤖 AGENT NODE TYPES:
• EmailFetchingNode: Fetches new emails and triggers workflow execution
• DecisionAgentNode: AI agent that analyzes emails and makes routing decisions
• ContentCreatorNode: Creates various types of content (text, LaTeX, audio, images)
• InvestigationNode: Performs research and investigation on topics
• MessageSendingNode: Sends emails and other messages
• PostProcessingNode: Handles final processing, logging, and cleanup
""")

def print_api_flow():
    """Print API flow."""
    print_header("API FLOW")
    
    print("""
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   HEALTH    │    │ WORKFLOWS   │    │   CREATE    │    │   EXECUTE   │
│             │    │             │    │             │    │             │
│ GET /health │    │GET /workflows│   │POST /workflows│  │POST /run    │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘

🔗 API ENDPOINTS:
• GET  /api/health - Check API status
• GET  /api/workflows - List all workflows
• POST /api/workflows - Create new workflow
• GET  /api/workflows/{id} - Get workflow details
• PUT  /api/workflows/{id} - Update workflow
• DELETE /api/workflows/{id} - Delete workflow
• POST /api/workflows/{id}/run - Execute workflow
• GET  /api/nodes - List available node types
• GET  /api/executions/{id} - Get execution results
""")

def print_key_points():
    """Print key points about the workflow system."""
    print_header("KEY POINTS")
    
    print("""
🎯 WORKFLOW CHARACTERISTICS:
1. ➡️  LEFT TO RIGHT: All workflows flow naturally from left to right
2. 🏗️  LAYERED: Each layer builds on the previous one
3. 👁️  VISUAL: The visual editor mirrors the actual execution
4. 🔄  COMPATIBLE: Works with both traditional and visual workflows
5. 🔧  EXTENSIBLE: Easy to add new nodes and capabilities

🔄 EXECUTION FLOW:
1. Visual Dashboard → User creates workflow visually
2. Workflow API → Receives workflow via REST API
3. Workflow Engine → Converts visual workflow to PocketFlow flow
4. Original PocketFlow → Executes using proven flow system
5. Services → Perform actual work (email, content, etc.)
6. Results → Returned through the same path

🤖 AGENT WORKFLOW BENEFITS:
• ✅ Intelligent Decision Making: AI agents analyze emails and make routing decisions
• ✅ Automated Content Creation: Generate various types of content automatically
• ✅ Research & Investigation: Perform web searches and gather information
• ✅ Smart Messaging: Send appropriate responses based on context
• ✅ Complete Processing: Full workflow from email to response with logging

💡 BENEFITS:
• ✅ Backward Compatibility: All existing PocketFlow functionality preserved
• ✅ Visual Workflows: Modern n8n-like interface for complex workflows
• ✅ Hybrid Usage: Use traditional flows or visual workflows as needed
• ✅ Extensible: Easy to add new nodes and capabilities
• ✅ Robust: Built on proven PocketFlow foundation
""")

def main():
    """Main function to display the workflow visualization."""
    print("🚀 PocketFlow Workflow Visualization")
    print("   Showing left-to-right workflow flow with Agent nodes")
    
    print_workflow_visualization()
    print_agent_workflows()
    print_node_categories()
    print_api_flow()
    print_key_points()
    
    print("\n" + "="*80)
    print(" 📚 For more details, see:")
    print("    • docs/workflow_visualization.md - Detailed visualization")
    print("    • docs/ascii_workflow.md - ASCII art examples")
    print("    • docs/index.md - Main documentation")
    print("    • docs/workflows.md - API documentation")
    print("    • data/workflows/agent_workflow.json - Sample agent workflow")
    print("="*80)

if __name__ == "__main__":
    main() 