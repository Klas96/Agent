"""
Tool registry for PocketFlow agents.

This module provides a centralized registry for managing available tools.
"""

from typing import Dict, List, Optional, Any
from .base import Tool, ToolResult, ToolRegistry
from ..utils.logging import get_logger

logger = get_logger("ToolRegistry")

class AgentToolRegistry(ToolRegistry):
    """
    Extended tool registry specifically for agent use.
    """
    
    def __init__(self):
        super().__init__()
        self.logger = get_logger("AgentToolRegistry")
    
    def get_available_tools_prompt(self) -> str:
        """
        Generate a prompt describing all available tools.
        
        Returns:
            Formatted string describing available tools
        """
        if not self.tools:
            return "No tools available."
        
        prompt = "Available tools:\n\n"
        
        for tool in self.tools.values():
            prompt += f"Tool: {tool.name}\n"
            prompt += f"Description: {tool.description}\n"
            prompt += "Parameters:\n"
            
            for param_name, param_spec in tool.parameters.items():
                required = param_spec.get('required', False)
                param_type = param_spec.get('type', 'str')
                description = param_spec.get('description', '')
                
                prompt += f"  - {param_name} ({param_type}){' [required]' if required else ''}: {description}\n"
            
            prompt += "\n"
        
        return prompt
    
    def execute_tool_with_validation(self, tool_name: str, **kwargs) -> ToolResult:
        """
        Execute a tool with additional validation and logging.
        
        Args:
            tool_name: Name of the tool to execute
            **kwargs: Parameters to pass to the tool
            
        Returns:
            ToolResult from the tool execution
        """
        self.logger.info(f"Agent requesting to execute tool: {tool_name} with params: {kwargs}")
        
        result = self.execute_tool(tool_name, **kwargs)
        
        if result.success:
            self.logger.info(f"Tool {tool_name} executed successfully")
        else:
            self.logger.error(f"Tool {tool_name} failed: {result.error}")
        
        return result


# Global agent tool registry
agent_tool_registry = AgentToolRegistry() 