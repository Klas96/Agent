"""
Tools module for PocketFlow agents.

This module provides a framework for creating and using tools that agents can utilize.
"""

from .base import Tool, ToolResult, ToolError
from .registry import ToolRegistry, agent_tool_registry
from .database import DatabaseQueryTool
from .email_tools import EmailSearchTool, EmailSendTool
from .mcp_tools import (
    MCPToolWrapper,
    LibriscribeDocumentTool,
    LibriscribeResearchTool,
    LibriscribeOutlineTool,
    PodcastfyTool
)

# Tools moved to MPC processes:
# - WebSearchTool -> Research-MPC
# - FileReadTool, FileWriteTool -> Tools-MPC
# - CalculatorTool -> Tools-MPC
# - WeatherTool -> Tools-MPC
# - PolymarketTool -> Tools-MPC

__all__ = [
    'Tool',
    'ToolResult', 
    'ToolError',
    'ToolRegistry',
    'agent_tool_registry',
    'DatabaseQueryTool',
    'EmailSearchTool',
    'EmailSendTool',
    'MCPToolWrapper',
    'LibriscribeDocumentTool',
    'LibriscribeResearchTool',
    'LibriscribeOutlineTool',
    'PodcastfyTool',
] 