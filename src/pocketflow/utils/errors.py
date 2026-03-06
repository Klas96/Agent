"""
Error handling utilities for PocketFlow.

This module provides custom exceptions and error handling utilities.
"""

import logging
import time
from enum import Enum
from typing import Dict, Any, Optional, Type, Callable
from .logging import get_logger


class ErrorSeverity(str, Enum):
    """Error severity levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class PocketFlowError(Exception):
    """Base exception for PocketFlow errors."""
    
    def __init__(self, message: str, severity: ErrorSeverity = ErrorSeverity.MEDIUM, 
                 context: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.severity = severity
        self.context = context or {}
    
    def __str__(self):
        return f"{self.severity.value.upper()}: {super().__str__()}"


class ConfigurationError(PocketFlowError):
    """Error related to configuration issues."""
    
    def __init__(self, message: str, config_key: Optional[str] = None):
        super().__init__(message, ErrorSeverity.HIGH, {"config_key": config_key})


class EmailError(PocketFlowError):
    """Error related to email operations."""
    
    def __init__(self, message: str, email_id: Optional[str] = None):
        super().__init__(message, ErrorSeverity.MEDIUM, {"email_id": email_id})


class LLMError(PocketFlowError):
    """Error related to LLM operations."""
    
    def __init__(self, message: str, model: Optional[str] = None, provider: Optional[str] = None):
        super().__init__(message, ErrorSeverity.MEDIUM, {"model": model, "provider": provider})


class ContentGenerationError(PocketFlowError):
    """Error related to content generation."""
    
    def __init__(self, message: str, content_type: Optional[str] = None):
        super().__init__(message, ErrorSeverity.MEDIUM, {"content_type": content_type})


# BitcoinError has been moved to bitcoin-MPC package
# Import from bitcoin_mpc.errors if needed
# class BitcoinError(PocketFlowError):
#     """Error related to Bitcoin operations."""
#     
#     def __init__(self, message: str, address: Optional[str] = None):
#         super().__init__(message, ErrorSeverity.MEDIUM, {"address": address})


class DatabaseError(PocketFlowError):
    """Error related to database operations."""
    
    def __init__(self, message: str, table: Optional[str] = None, operation: Optional[str] = None):
        super().__init__(message, ErrorSeverity.HIGH, {"table": table, "operation": operation})


class WebSearchError(PocketFlowError):
    """Error related to web search operations."""
    
    def __init__(self, message: str, query: Optional[str] = None):
        super().__init__(message, ErrorSeverity.MEDIUM, {"query": query})


class FlowError(PocketFlowError):
    """Error related to flow execution."""
    
    def __init__(self, message: str, flow_name: Optional[str] = None, step_name: Optional[str] = None):
        super().__init__(message, ErrorSeverity.HIGH, {"flow_name": flow_name, "step_name": step_name})


class NodeError(PocketFlowError):
    """Error related to node execution."""
    
    def __init__(self, message: str, node_name: Optional[str] = None):
        super().__init__(message, ErrorSeverity.MEDIUM, {"node_name": node_name})


class ValidationError(PocketFlowError):
    """Error related to data validation."""
    
    def __init__(self, message: str, field: Optional[str] = None, value: Any = None):
        super().__init__(message, ErrorSeverity.MEDIUM, {"field": field, "value": value})


class TimeoutError(PocketFlowError):
    """Error related to timeouts."""
    
    def __init__(self, message: str, timeout_seconds: Optional[int] = None):
        super().__init__(message, ErrorSeverity.MEDIUM, {"timeout_seconds": timeout_seconds})


class RetryableError(PocketFlowError):
    """Error that can be retried."""
    
    def __init__(self, message: str, max_retries: int = 3, retry_delay: float = 1.0):
        super().__init__(message, ErrorSeverity.LOW, {"max_retries": max_retries, "retry_delay": retry_delay})


class NetworkError(RetryableError):
    """Error related to network operations."""
    
    def __init__(self, message: str):
        super().__init__(message, max_retries=5, retry_delay=2.0)


class ServiceUnavailableError(RetryableError):
    """Error when a service is temporarily unavailable."""
    
    def __init__(self, message: str):
        super().__init__(message, max_retries=3, retry_delay=5.0)


class ErrorHandler:
    """Handles errors with logging and recovery strategies."""
    
    def __init__(self):
        self.logger = get_logger("errors")
        self.error_counts: Dict[Type[Exception], int] = {}
        self.recovery_strategies: Dict[Type[Exception], callable] = {}
    
    def handle_error(self, error: Exception, context: Optional[Dict[str, Any]] = None) -> bool:
        """
        Handle an error with logging and recovery.
        
        Args:
            error: The exception that occurred
            context: Additional context information
            
        Returns:
            True if the error was handled successfully, False otherwise
        """
        # Log the error
        self._log_error(error, context)
        
        # Update error counts
        error_type = type(error)
        self.error_counts[error_type] = self.error_counts.get(error_type, 0) + 1
        
        # Try recovery strategy
        if error_type in self.recovery_strategies:
            try:
                return self.recovery_strategies[error_type](error, context)
            except Exception as recovery_error:
                self.logger.error(f"Recovery strategy failed: {recovery_error}")
                return False
        
        # Default handling based on error type
        return self._default_recovery(error, context)
    
    def _log_error(self, error: Exception, context: Optional[Dict[str, Any]] = None):
        """Log the error with structured information."""
        log_data = {
            "error_type": type(error).__name__,
            "error_message": str(error),
            "context": context or {}
        }
        
        if isinstance(error, PocketFlowError):
            log_data.update({
                "severity": error.severity.value,
                "error_context": error.context
            })
        
        self.logger.error("Error occurred", extra=log_data, exc_info=True)
    
    def _default_recovery(self, error: Exception, context: Optional[Dict[str, Any]] = None) -> bool:
        """Default error recovery strategy."""
        if isinstance(error, RetryableError):
            # For retryable errors, we could implement retry logic here
            return True
        elif isinstance(error, (ConfigurationError, ValidationError)):
            # These are usually fatal and should stop execution
            return False
        else:
            # For other errors, log and continue if possible
            return True
    
    def add_recovery_strategy(self, error_type: Type[Exception], strategy: callable):
        """Add a custom recovery strategy for an error type."""
        self.recovery_strategies[error_type] = strategy
    
    def get_error_stats(self) -> Dict[str, Any]:
        """Get error statistics."""
        return {
            "error_counts": self.error_counts.copy(),
            "total_errors": sum(self.error_counts.values())
        }


def retry_on_error(max_retries: int = 3, delay: float = 1.0, 
                  backoff_factor: float = 2.0, 
                  retryable_exceptions: tuple = (RetryableError,)):
    """
    Decorator to retry functions on specific exceptions.
    
    Args:
        max_retries: Maximum number of retry attempts
        delay: Initial delay between retries in seconds
        backoff_factor: Factor to multiply delay by on each retry
        retryable_exceptions: Tuple of exception types to retry on
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            last_exception = None
            current_delay = delay
            
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except retryable_exceptions as e:
                    last_exception = e
                    if attempt < max_retries:
                        import time
                        time.sleep(current_delay)
                        current_delay *= backoff_factor
                    else:
                        raise last_exception
                except Exception as e:
                    # Don't retry on non-retryable exceptions
                    raise e
            
            raise last_exception
        return wrapper
    return decorator


def safe_execute(func: callable, *args, **kwargs) -> tuple[Any, Optional[Exception]]:
    """
    Safely execute a function and return result with any exception.
    
    Returns:
        Tuple of (result, exception) where exception is None if successful
    """
    try:
        result = func(*args, **kwargs)
        return result, None
    except Exception as e:
        return None, e


# Global error handler instance
error_handler = ErrorHandler() 