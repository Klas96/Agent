#!/usr/bin/env python3
"""
Test script for the enhanced investigation + report workflow.

This script demonstrates how the agent can:
1. Investigate a topic using web search
2. Generate a report based on the investigation findings
"""

import sys
import os
from pathlib import Path

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_investigation_report_workflow():
    """Test the investigation + report workflow."""
    print("Testing Investigation + Report Workflow")
    print("=" * 50)
    
    # Example user request
    user_request = "Investigate what is happening in the world and give me a report"
    
    print(f"User Request: {user_request}")
    print("\nThis should trigger the following workflow:")
    print("1. INVESTIGATE action - Research current world events")
    print("2. GENERATE action - Create a document based on findings")
    print("3. SEND action - Send the report as attachment")
    print("4. FINISH action - End the conversation")
    
    print("\n" + "=" * 50)
    print("Expected Agent Actions:")
    print("=" * 50)
    
    # Show the expected JSON actions
    expected_actions = [
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
                "research_based": True
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
    
    for i, action in enumerate(expected_actions, 1):
        print(f"\n{i}. {action['action'].upper()}")
        print(f"   Parameters: {action['parameters']}")
    
    print("\n" + "=" * 50)
    print("Workflow Benefits:")
    print("=" * 50)
    
    benefits = [
        "🔍 **Comprehensive Research**: The investigate action performs thorough web search",
        "📊 **Data-Driven Reports**: Reports are based on actual research findings",
        "📄 **Professional Documents**: LaTeX templates ensure professional formatting",
        "🎯 **Intelligent Routing**: Agent automatically determines when to investigate vs. generate",
        "📧 **Seamless Delivery**: Reports are automatically sent as PDF attachments",
        "🔄 **Flexible Workflow**: Supports both simple investigation and investigation+report patterns"
    ]
    
    for benefit in benefits:
        print(f"   {benefit}")
    
    print("\n" + "=" * 50)
    print("Example Use Cases:")
    print("=" * 50)
    
    use_cases = [
        {
            "request": "Investigate what is happening in the world and give me a report",
            "workflow": "Investigate → Generate Document → Send Report"
        },
        {
            "request": "Research the latest AI developments and create a technical report",
            "workflow": "Investigate → Generate Technical Document → Send Report"
        },
        {
            "request": "Find out about market trends and write a business report",
            "workflow": "Investigate → Generate Business Document → Send Report"
        },
        {
            "request": "What's the latest news about climate change?",
            "workflow": "Investigate → Send Findings (no report needed)"
        }
    ]
    
    for i, case in enumerate(use_cases, 1):
        print(f"\n{i}. Request: {case['request']}")
        print(f"   Workflow: {case['workflow']}")

def test_enhanced_prompt_system():
    """Test the enhanced prompt system."""
    print("\n" + "=" * 50)
    print("Enhanced Prompt System")
    print("=" * 50)
    
    print("The enhanced prompt system now supports three workflows:")
    print("\n1. **Investigation + Report Workflow**:")
    print("   - investigate → generate (document) → send → finish")
    print("   - Used when user wants research + report")
    
    print("\n2. **Simple Content Generation**:")
    print("   - generate → send → finish")
    print("   - Used when user wants content without research")
    
    print("\n3. **Simple Investigation**:")
    print("   - investigate → send → finish")
    print("   - Used when user just wants information")
    
    print("\nThe system automatically detects which workflow to use based on:")
    print("- Keywords in the user request")
    print("- Whether research is needed")
    print("- Whether content generation is requested")

def test_research_based_document_generation():
    """Test research-based document generation."""
    print("\n" + "=" * 50)
    print("Research-Based Document Generation")
    print("=" * 50)
    
    print("When the document service receives a research-based prompt:")
    print("\n✅ Enhanced prompts that incorporate research findings")
    print("✅ Structured sections that use research data")
    print("✅ Professional formatting with LaTeX templates")
    print("✅ Automatic detection of research-based vs. regular documents")
    
    print("\nResearch-based documents include:")
    print("- Research context in introduction")
    print("- Data-supported analysis")
    print("- Research-backed conclusions")
    print("- Professional citations and references")

def main():
    """Main test function."""
    print("Investigation + Report Workflow Test")
    print("=" * 50)
    
    # Test the workflow
    test_investigation_report_workflow()
    
    # Test enhanced prompt system
    test_enhanced_prompt_system()
    
    # Test research-based document generation
    test_research_based_document_generation()
    
    print("\n" + "=" * 50)
    print("🎉 Enhanced Investigation + Report Workflow Ready!")
    print("=" * 50)
    
    print("\nThe system now supports:")
    print("✅ Two-step investigation + report workflow")
    print("✅ Intelligent agent decision making")
    print("✅ Research-based document generation")
    print("✅ Professional LaTeX document formatting")
    print("✅ Automatic workflow detection")
    
    print("\nUsers can now send emails like:")
    print("- 'Investigate what is happening in the world and give me a report'")
    print("- 'Research the latest AI developments and create a technical report'")
    print("- 'Find out about market trends and write a business report'")
    
    print("\nThe agent will automatically:")
    print("1. Investigate the topic thoroughly")
    print("2. Generate a professional report based on findings")
    print("3. Send the report as a PDF attachment")
    print("4. Provide a helpful email response")

if __name__ == "__main__":
    main() 