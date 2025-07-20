"""
Error handling utilities for PocketFlow.

This module provides custom exceptions and error handling strategies.
"""

from typing import Optional, Dict, Any, Type
import logging
from enum import Enum


class ErrorSeverity(str, Enum):
    """Error severity levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class PocketFlowError(Exception):
    """Base exception for PocketFlow."""
    
    def __init__(self, message: str, severity: ErrorSeverity = ErrorSeverity.MEDIUM, 
                 context: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.severity = severity
        self.context = context or {}
        self.timestamp = None  # Will be set by error handler
    
    def __str__(self):
        return f"[{self.severity.value.upper()}] {self.message}"


class ConfigurationError(PocketFlowError):
    """Raised when there's a configuration issue."""
    
    def __init__(self, message: str, config_key: Optional[str] = None):
        super().__init__(message, ErrorSeverity.HIGH, {"config_key": config_key})


class EmailError(PocketFlowError):
    """Raised when there's an email-related error."""
    
    def __init__(self, message: str, email_id: Optional[str] = None):
        super().__init__(message, ErrorSeverity.MEDIUM, {"email_id": email_id})


class LLMError(PocketFlowError):
    """Raised when there's an LLM-related error."""
    
    def __init__(self, message: str, model: Optional[str] = None, provider: Optional[str] = None):
        super().__init__(message, ErrorSeverity.MEDIUM, {"model": model, "provider": provider})


class ContentGenerationError(PocketFlowError):
    """Raised when content generation fails."""
    
    def __init__(self, message: str, content_type: Optional[str] = None):
        super().__init__(message, ErrorSeverity.MEDIUM, {"content_type": content_type})


class BitcoinError(PocketFlowError):
    """Raised when there's a Bitcoin-related error."""
    
    def __init__(self, message: str, address: Optional[str] = None):
        super().__init__(message, ErrorSeverity.HIGH, {"address": address})


class FlowError(PocketFlowError):
    """Raised when there's a flow execution error."""
    
    def __init__(self, message: str, flow_name: Optional[str] = None, step_name: Optional[str] = None):
        super().__init__(message, ErrorSeverity.HIGH, {"flow_name": flow_name, "step_name": step_name})


class NodeError(PocketFlowError):
    """Raised when a node execution fails."""
    
    def __init__(self, message: str, node_name: Optional[str] = None):
        super().__init__(message, ErrorSeverity.MEDIUM, {"node_name": node_name})


class ValidationError(PocketFlowError):
    """Raised when data validation fails."""
    
    def __init__(self, message: str, field: Optional[str] = None, value: Any = None):
        super().__init__(message, ErrorSeverity.LOW, {"field": field, "value": value})


class TimeoutError(PocketFlowError):
    """Raised when an operation times out."""
    
    def __init__(self, message: str, timeout_seconds: Optional[int] = None):
        super().__init__(message, ErrorSeverity.MEDIUM, {"timeout_seconds": timeout_seconds})


class RetryableError(PocketFlowError):
    """Base class for errors that can be retried."""
    
    def __init__(self, message: str, max_retries: int = 3, retry_delay: float = 1.0):
        super().__init__(message, ErrorSeverity.MEDIUM, {
            "max_retries": max_retries,
            "retry_delay": retry_delay
        })


class NetworkError(RetryableError):
    """Raised when there's a network-related error."""
    pass


class ServiceUnavailableError(RetryableError):
    """Raised when a service is temporarily unavailable."""
    pass


class ErrorHandler:
    """Handles errors with logging and recovery strategies."""
    
    def __init__(self):
        self.logger = logging.getLogger("pocketflow.errors")
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