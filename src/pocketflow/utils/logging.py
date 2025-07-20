"""
Logging utilities for PocketFlow.

This module provides structured logging with monitoring capabilities.
"""

import logging
import logging.handlers
import sys
from typing import Optional, Dict, Any
from pathlib import Path
from datetime import datetime
import json
from functools import wraps


class StructuredFormatter(logging.Formatter):
    """Custom formatter that outputs structured JSON logs."""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # Add extra fields if present
        if hasattr(record, 'extra_fields'):
            log_entry.update(record.extra_fields)
        
        # Add exception info if present
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)
        
        return json.dumps(log_entry)


class FlowLogger:
    """Specialized logger for flow execution."""
    
    def __init__(self, flow_name: str):
        self.flow_name = flow_name
        self.logger = logging.getLogger(f"pocketflow.flow.{flow_name}")
        self.start_time: Optional[datetime] = None
        self.step_times: Dict[str, float] = {}
    
    def start_flow(self):
        """Log the start of a flow execution."""
        self.start_time = datetime.utcnow()
        self.logger.info("Flow started", extra={
            "flow_name": self.flow_name,
            "event": "flow_start"
        })
    
    def end_flow(self, success: bool, error: Optional[str] = None):
        """Log the end of a flow execution."""
        if self.start_time:
            duration = (datetime.utcnow() - self.start_time).total_seconds()
            self.logger.info("Flow ended", extra={
                "flow_name": self.flow_name,
                "event": "flow_end",
                "success": success,
                "duration_seconds": duration,
                "error": error
            })
    
    def step_start(self, step_name: str):
        """Log the start of a step execution."""
        self.step_times[step_name] = datetime.utcnow().timestamp()
        self.logger.info("Step started", extra={
            "flow_name": self.flow_name,
            "step_name": step_name,
            "event": "step_start"
        })
    
    def step_end(self, step_name: str, success: bool, error: Optional[str] = None):
        """Log the end of a step execution."""
        if step_name in self.step_times:
            duration = datetime.utcnow().timestamp() - self.step_times[step_name]
            self.logger.info("Step ended", extra={
                "flow_name": self.flow_name,
                "step_name": step_name,
                "event": "step_end",
                "success": success,
                "duration_seconds": duration,
                "error": error
            })


def setup_logging(
    level: str = "INFO",
    log_file: Optional[str] = None,
    log_format: str = "structured",
    max_size: int = 10,
    backup_count: int = 5
) -> None:
    """
    Set up logging configuration.
    
    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Path to log file (optional)
        log_format: Log format ("structured" or "standard")
        max_size: Maximum log file size in MB
        backup_count: Number of backup files to keep
    """
    # Clear existing handlers
    root_logger = logging.getLogger()
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Set log level
    log_level = getattr(logging, level.upper())
    root_logger.setLevel(log_level)
    
    # Create formatter
    if log_format == "structured":
        formatter = StructuredFormatter()
    else:
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # File handler (if specified)
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=max_size * 1024 * 1024,  # Convert MB to bytes
            backupCount=backup_count
        )
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)


def get_logger(name: str) -> logging.Logger:
    """Get a logger with the specified name."""
    return logging.getLogger(f"pocketflow.{name}")


def log_execution_time(logger: logging.Logger):
    """Decorator to log function execution time."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = datetime.utcnow()
            try:
                result = func(*args, **kwargs)
                duration = (datetime.utcnow() - start_time).total_seconds()
                logger.info(
                    f"Function {func.__name__} completed successfully",
                    extra={
                        "function": func.__name__,
                        "duration_seconds": duration,
                        "event": "function_complete"
                    }
                )
                return result
            except Exception as e:
                duration = (datetime.utcnow() - start_time).total_seconds()
                logger.error(
                    f"Function {func.__name__} failed",
                    extra={
                        "function": func.__name__,
                        "duration_seconds": duration,
                        "error": str(e),
                        "event": "function_error"
                    },
                    exc_info=True
                )
                raise
        return wrapper
    return decorator


class MetricsCollector:
    """Collect and track metrics during execution."""
    
    def __init__(self):
        self.metrics: Dict[str, Any] = {}
        self.counters: Dict[str, int] = {}
        self.timers: Dict[str, float] = {}
    
    def increment_counter(self, name: str, value: int = 1):
        """Increment a counter metric."""
        self.counters[name] = self.counters.get(name, 0) + value
    
    def record_timer(self, name: str, duration: float):
        """Record a timer metric."""
        if name not in self.timers:
            self.timers[name] = []
        self.timers[name].append(duration)
    
    def set_gauge(self, name: str, value: Any):
        """Set a gauge metric."""
        self.metrics[name] = value
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get all collected metrics."""
        return {
            "counters": self.counters.copy(),
            "timers": {k: {
                "count": len(v),
                "total": sum(v),
                "average": sum(v) / len(v) if v else 0,
                "min": min(v) if v else 0,
                "max": max(v) if v else 0
            } for k, v in self.timers.items()},
            "gauges": self.metrics.copy()
        }


# Global metrics collector
metrics = MetricsCollector() 