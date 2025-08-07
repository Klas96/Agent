"""
Calculator tool for PocketFlow agents.
"""

import re
from typing import Dict, Any
from .base import Tool, ToolResult
from ..utils.logging import get_logger


class CalculatorTool(Tool):
    """
    Tool for performing mathematical calculations.
    """
    
    def __init__(self):
        super().__init__(
            name="calculator",
            description="Perform mathematical calculations safely"
        )
    
    @property
    def parameters(self) -> Dict[str, Dict[str, Any]]:
        return {
            "expression": {
                "type": str,
                "required": True,
                "description": "The mathematical expression to evaluate (e.g., '2 + 3 * 4')"
            }
        }
    
    def execute(self, **kwargs) -> ToolResult:
        """
        Execute a mathematical calculation.
        
        Args:
            expression: The mathematical expression to evaluate
            
        Returns:
            ToolResult with calculation result
        """
        expression = kwargs.get("expression")
        
        try:
            # Sanitize the expression for security
            sanitized_expr = self._sanitize_expression(expression)
            
            if not sanitized_expr:
                return ToolResult(
                    success=False,
                    error="Invalid mathematical expression"
                )
            
            # Evaluate the expression safely
            result = eval(sanitized_expr, {"__builtins__": {}}, {})
            
            return ToolResult(
                success=True,
                data={
                    "expression": expression,
                    "result": result,
                    "sanitized_expression": sanitized_expr
                },
                metadata={
                    "source": "calculator"
                }
            )
            
        except Exception as e:
            self.logger.error(f"Calculator failed: {str(e)}")
            return ToolResult(
                success=False,
                error=f"Calculation failed: {str(e)}"
            )
    
    def _sanitize_expression(self, expression: str) -> str:
        """
        Sanitize mathematical expression for safe evaluation.
        
        Args:
            expression: The expression to sanitize
            
        Returns:
            Sanitized expression or empty string if invalid
        """
        # Remove all whitespace
        expr = expression.replace(" ", "")
        
        # Only allow digits, operators, parentheses, and decimal points
        allowed_chars = set("0123456789+-*/.()")
        
        if not all(c in allowed_chars for c in expr):
            return ""
        
        # Basic validation - check for balanced parentheses
        if expr.count("(") != expr.count(")"):
            return ""
        
        # Prevent division by zero patterns
        if "//" in expr or "**" in expr:
            return ""
        
        return expr 