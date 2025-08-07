"""
Base tool classes for PocketFlow agents.

This module defines the core interfaces and base classes for tools.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass
from pydantic import BaseModel, Field
from ..utils.logging import get_logger


@dataclass
class ToolResult:
    """Result of a tool execution."""
    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class ToolError(Exception):
    """Exception raised when a tool fails."""
    pass


class Tool(ABC):
    """
    Base class for all tools that agents can use.
    
    Each tool should implement:
    - name: The name of the tool
    - description: What the tool does
    - parameters: The parameters the tool accepts
    - execute: The main execution logic
    """
    
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.logger = get_logger(f"tool.{name}")
    
    @property
    @abstractmethod
    def parameters(self) -> Dict[str, Dict[str, Any]]:
        """
        Return the parameters this tool accepts.
        
        Returns:
            Dict mapping parameter names to their specifications
        """
        pass
    
    @abstractmethod
    def execute(self, **kwargs) -> ToolResult:
        """
        Execute the tool with the given parameters.
        
        Args:
            **kwargs: Tool-specific parameters
            
        Returns:
            ToolResult containing the execution result
        """
        pass
    
    def validate_parameters(self, **kwargs) -> bool:
        """
        Validate that the provided parameters are correct.
        
        Args:
            **kwargs: Parameters to validate
            
        Returns:
            True if parameters are valid, False otherwise
        """
        required_params = {k: v for k, v in self.parameters.items() if v.get('required', False)}
        
        for param_name, param_spec in required_params.items():
            if param_name not in kwargs:
                self.logger.error(f"Missing required parameter: {param_name}")
                return False
            
            param_value = kwargs[param_name]
            param_type = param_spec.get('type', str)
            
            if not isinstance(param_value, param_type):
                self.logger.error(f"Parameter {param_name} should be {param_type}, got {type(param_value)}")
                return False
        
        return True
    
    def get_schema(self) -> Dict[str, Any]:
        """
        Get the tool schema for agent consumption.
        
        Returns:
            Dict containing tool name, description, and parameters
        """
        return {
            "name": self.name,
            "description": self.description,
            "parameters": self.parameters
        }


class ToolRegistry:
    """
    Registry for managing available tools.
    """
    
    def __init__(self):
        self.tools: Dict[str, Tool] = {}
        self.logger = get_logger("ToolRegistry")
    
    def register_tool(self, tool: Tool) -> None:
        """
        Register a tool with the registry.
        
        Args:
            tool: The tool to register
        """
        self.tools[tool.name] = tool
        self.logger.info(f"Registered tool: {tool.name}")
    
    def get_tool(self, name: str) -> Optional[Tool]:
        """
        Get a tool by name.
        
        Args:
            name: Name of the tool
            
        Returns:
            The tool if found, None otherwise
        """
        return self.tools.get(name)
    
    def list_tools(self) -> List[Dict[str, Any]]:
        """
        List all available tools.
        
        Returns:
            List of tool schemas
        """
        return [tool.get_schema() for tool in self.tools.values()]
    
    def execute_tool(self, tool_name: str, **kwargs) -> ToolResult:
        """
        Execute a tool by name.
        
        Args:
            tool_name: Name of the tool to execute
            **kwargs: Parameters to pass to the tool
            
        Returns:
            ToolResult from the tool execution
        """
        tool = self.get_tool(tool_name)
        if not tool:
            return ToolResult(
                success=False,
                error=f"Tool '{tool_name}' not found"
            )
        
        if not tool.validate_parameters(**kwargs):
            return ToolResult(
                success=False,
                error=f"Invalid parameters for tool '{tool_name}'"
            )
        
        try:
            return tool.execute(**kwargs)
        except Exception as e:
            self.logger.error(f"Error executing tool '{tool_name}': {str(e)}")
            return ToolResult(
                success=False,
                error=str(e)
            )


# Global tool registry instance
tool_registry = ToolRegistry() 