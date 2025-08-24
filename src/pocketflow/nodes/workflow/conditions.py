"""
Condition and transform nodes for PocketFlow n8n-like workflow system.

This module provides nodes for conditional logic and data transformation.
"""

import json
import re
from typing import Dict, Any, List
from datetime import datetime

from .base import ConditionNode, TransformNode, NodeInput, NodeOutput, NodeMetadata
from ..core.types import SharedState


class IfElseNode(ConditionNode):
    """
    Condition node that evaluates a condition and routes execution.
    """
    
    def execute(self, shared: SharedState) -> Dict[str, Any]:
        """
        Evaluate a condition and return the result.
        
        Args:
            shared: Shared state
            
        Returns:
            Dictionary with condition result
        """
        try:
            condition = self.get_input_value("condition", "")
            value1 = self.get_input_value("value1", "")
            operator = self.get_input_value("operator", "equals")
            value2 = self.get_input_value("value2", "")
            
            if not condition:
                raise ValueError("No condition specified")
            
            self.logger.info(f"Evaluating condition: {value1} {operator} {value2}")
            
            # Evaluate condition
            result = self._evaluate_condition(value1, operator, value2)
            
            # Set outputs
            self.set_output(shared, "condition_result", result)
            self.set_output(shared, "condition_evaluated", condition)
            
            return {
                "success": True,
                "condition_result": result,
                "condition_evaluated": condition,
                "message": f"Condition evaluated: {result}"
            }
            
        except Exception as e:
            self.logger.error(f"Error evaluating condition: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _evaluate_condition(self, value1: Any, operator: str, value2: Any) -> bool:
        """Evaluate a condition with the given operator."""
        try:
            if operator == "equals":
                return value1 == value2
            elif operator == "not_equals":
                return value1 != value2
            elif operator == "greater_than":
                return float(value1) > float(value2)
            elif operator == "less_than":
                return float(value1) < float(value2)
            elif operator == "greater_than_or_equal":
                return float(value1) >= float(value2)
            elif operator == "less_than_or_equal":
                return float(value1) <= float(value2)
            elif operator == "contains":
                return str(value2) in str(value1)
            elif operator == "not_contains":
                return str(value2) not in str(value1)
            elif operator == "starts_with":
                return str(value1).startswith(str(value2))
            elif operator == "ends_with":
                return str(value1).endswith(str(value2))
            elif operator == "regex_match":
                return bool(re.search(str(value2), str(value1)))
            elif operator == "is_empty":
                return not value1 or str(value1).strip() == ""
            elif operator == "is_not_empty":
                return value1 and str(value1).strip() != ""
            else:
                raise ValueError(f"Unknown operator: {operator}")
        except (ValueError, TypeError):
            return False
    
    @classmethod
    def get_metadata(cls) -> NodeMetadata:
        """Get metadata for IfElseNode."""
        return NodeMetadata(
            name="IfElseNode",
            description="Evaluates conditions and routes workflow execution",
            category="condition",
            inputs=[
                NodeInput("condition", "string", "Condition description", False, ""),
                NodeInput("value1", "string", "First value to compare", True),
                NodeInput("operator", "string", "Comparison operator", True),
                NodeInput("value2", "string", "Second value to compare", True)
            ],
            outputs=[
                NodeOutput("condition_result", "boolean", "Result of condition evaluation"),
                NodeOutput("condition_evaluated", "string", "Description of condition evaluated")
            ],
            icon="if",
            color="#FF9800"
        )


class TransformNode(TransformNode):
    """
    Transform node that manipulates JSON data.
    """
    
    def execute(self, shared: SharedState) -> Dict[str, Any]:
        """
        Transform data based on the specified operation.
        
        Args:
            shared: Shared state
            
        Returns:
            Dictionary with transformation result
        """
        try:
            operation = self.get_input_value("operation", "extract")
            input_data = self.get_input_value("input_data", "")
            transform_config = self.get_input_value("transform_config", {})
            
            if not input_data:
                raise ValueError("No input data specified")
            
            self.logger.info(f"Performing transform operation: {operation}")
            
            # Perform transformation based on operation
            if operation == "extract":
                result = self._extract_data(input_data, transform_config)
            elif operation == "format":
                result = self._format_data(input_data, transform_config)
            elif operation == "filter":
                result = self._filter_data(input_data, transform_config)
            elif operation == "map":
                result = self._map_data(input_data, transform_config)
            elif operation == "join":
                result = self._join_data(input_data, transform_config)
            elif operation == "split":
                result = self._split_data(input_data, transform_config)
            else:
                raise ValueError(f"Unknown operation: {operation}")
            
            # Set outputs
            self.set_output(shared, "transformed_data", result)
            self.set_output(shared, "operation_performed", operation)
            
            return {
                "success": True,
                "transformed_data": result,
                "operation_performed": operation,
                "message": f"Transform operation '{operation}' completed successfully"
            }
            
        except Exception as e:
            self.logger.error(f"Error performing transform: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _extract_data(self, input_data: Any, config: Dict[str, Any]) -> Any:
        """Extract data from input using JSONPath-like syntax."""
        try:
            if isinstance(input_data, str):
                data = json.loads(input_data)
            else:
                data = input_data
            
            path = config.get("path", "")
            if not path:
                return data
            
            # Simple path extraction (can be enhanced with proper JSONPath)
            keys = path.split(".")
            result = data
            for key in keys:
                if isinstance(result, dict) and key in result:
                    result = result[key]
                elif isinstance(result, list) and key.isdigit():
                    result = result[int(key)]
                else:
                    return None
            
            return result
        except Exception:
            return None
    
    def _format_data(self, input_data: Any, config: Dict[str, Any]) -> str:
        """Format data according to specified format."""
        format_type = config.get("format", "json")
        
        if format_type == "json":
            return json.dumps(input_data, indent=2)
        elif format_type == "csv":
            # Simple CSV formatting
            if isinstance(input_data, list):
                return "\n".join([str(item) for item in input_data])
            else:
                return str(input_data)
        elif format_type == "text":
            return str(input_data)
        else:
            return str(input_data)
    
    def _filter_data(self, input_data: Any, config: Dict[str, Any]) -> Any:
        """Filter data based on conditions."""
        if not isinstance(input_data, list):
            return input_data
        
        filter_key = config.get("filter_key", "")
        filter_value = config.get("filter_value", "")
        filter_operator = config.get("filter_operator", "equals")
        
        filtered = []
        for item in input_data:
            if isinstance(item, dict) and filter_key in item:
                if self._evaluate_filter(item[filter_key], filter_operator, filter_value):
                    filtered.append(item)
        
        return filtered
    
    def _evaluate_filter(self, value1: Any, operator: str, value2: Any) -> bool:
        """Evaluate a filter condition."""
        try:
            if operator == "equals":
                return value1 == value2
            elif operator == "contains":
                return str(value2) in str(value1)
            elif operator == "greater_than":
                return float(value1) > float(value2)
            elif operator == "less_than":
                return float(value1) < float(value2)
            else:
                return False
        except (ValueError, TypeError):
            return False
    
    def _map_data(self, input_data: Any, config: Dict[str, Any]) -> Any:
        """Map data using a transformation function."""
        if not isinstance(input_data, list):
            return input_data
        
        map_key = config.get("map_key", "")
        map_function = config.get("map_function", "uppercase")
        
        mapped = []
        for item in input_data:
            if isinstance(item, dict) and map_key in item:
                value = item[map_key]
                if map_function == "uppercase":
                    item[map_key] = str(value).upper()
                elif map_function == "lowercase":
                    item[map_key] = str(value).lower()
                elif map_function == "trim":
                    item[map_key] = str(value).strip()
                mapped.append(item)
        
        return mapped
    
    def _join_data(self, input_data: Any, config: Dict[str, Any]) -> str:
        """Join data with a separator."""
        if isinstance(input_data, list):
            separator = config.get("separator", ", ")
            return separator.join([str(item) for item in input_data])
        else:
            return str(input_data)
    
    def _split_data(self, input_data: Any, config: Dict[str, Any]) -> List[str]:
        """Split data by a separator."""
        if isinstance(input_data, str):
            separator = config.get("separator", ",")
            return [item.strip() for item in input_data.split(separator)]
        else:
            return [str(input_data)]
    
    @classmethod
    def get_metadata(cls) -> NodeMetadata:
        """Get metadata for TransformNode."""
        return NodeMetadata(
            name="TransformNode",
            description="Transforms and manipulates data",
            category="transform",
            inputs=[
                NodeInput("operation", "string", "Transform operation", True),
                NodeInput("input_data", "string", "Input data to transform", True),
                NodeInput("transform_config", "object", "Configuration for transformation", False, {})
            ],
            outputs=[
                NodeOutput("transformed_data", "any", "Transformed data"),
                NodeOutput("operation_performed", "string", "Operation that was performed")
            ],
            icon="transform",
            color="#2196F3"
        )


class DelayNode(TransformNode):
    """
    Node that adds a delay to workflow execution.
    """
    
    def execute(self, shared: SharedState) -> Dict[str, Any]:
        """
        Add a delay to workflow execution.
        
        Args:
            shared: Shared state
            
        Returns:
            Dictionary with delay result
        """
        try:
            import time
            
            delay_seconds = self.get_input_value("delay_seconds", 1)
            
            self.logger.info(f"Adding delay of {delay_seconds} seconds")
            
            # Add delay
            time.sleep(delay_seconds)
            
            # Set outputs
            self.set_output(shared, "delay_completed", datetime.now().isoformat())
            self.set_output(shared, "delay_duration", delay_seconds)
            
            return {
                "success": True,
                "delay_completed": datetime.now().isoformat(),
                "delay_duration": delay_seconds,
                "message": f"Delay of {delay_seconds} seconds completed"
            }
            
        except Exception as e:
            self.logger.error(f"Error in delay node: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    @classmethod
    def get_metadata(cls) -> NodeMetadata:
        """Get metadata for DelayNode."""
        return NodeMetadata(
            name="DelayNode",
            description="Adds a delay to workflow execution",
            category="transform",
            inputs=[
                NodeInput("delay_seconds", "number", "Delay duration in seconds", False, 1)
            ],
            outputs=[
                NodeOutput("delay_completed", "string", "When the delay completed"),
                NodeOutput("delay_duration", "number", "Duration of the delay")
            ],
            icon="timer",
            color="#607D8B"
        )


class LogNode(TransformNode):
    """
    Node that logs data to the workflow execution log.
    """
    
    def execute(self, shared: SharedState) -> Dict[str, Any]:
        """
        Log data to the workflow execution log.
        
        Args:
            shared: Shared state
            
        Returns:
            Dictionary with log result
        """
        try:
            message = self.get_input_value("message", "")
            log_level = self.get_input_value("log_level", "INFO")
            data_to_log = self.get_input_value("data_to_log", {})
            
            if not message:
                raise ValueError("No message specified for logging")
            
            self.logger.info(f"Log node: {message}")
            
            # Log the message with the specified level
            if log_level == "DEBUG":
                self.logger.debug(message)
            elif log_level == "INFO":
                self.logger.info(message)
            elif log_level == "WARNING":
                self.logger.warning(message)
            elif log_level == "ERROR":
                self.logger.error(message)
            else:
                self.logger.info(message)
            
            # Set outputs
            self.set_output(shared, "logged_message", message)
            self.set_output(shared, "log_level", log_level)
            self.set_output(shared, "logged_at", datetime.now().isoformat())
            
            return {
                "success": True,
                "logged_message": message,
                "log_level": log_level,
                "logged_at": datetime.now().isoformat(),
                "message": f"Data logged with level {log_level}"
            }
            
        except Exception as e:
            self.logger.error(f"Error in log node: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    @classmethod
    def get_metadata(cls) -> NodeMetadata:
        """Get metadata for LogNode."""
        return NodeMetadata(
            name="LogNode",
            description="Logs data to the workflow execution log",
            category="transform",
            inputs=[
                NodeInput("message", "string", "Message to log", True),
                NodeInput("log_level", "string", "Log level", False, "INFO"),
                NodeInput("data_to_log", "object", "Additional data to log", False, {})
            ],
            outputs=[
                NodeOutput("logged_message", "string", "Message that was logged"),
                NodeOutput("log_level", "string", "Log level used"),
                NodeOutput("logged_at", "string", "When the log was created")
            ],
            icon="log",
            color="#795548"
        ) 