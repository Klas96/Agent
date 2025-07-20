"""
Performance monitoring utilities for PocketFlow.

This module provides performance tracking and monitoring capabilities.
"""

import time
import functools
from typing import Dict, Any, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime
import threading
from collections import defaultdict

from .logging import get_logger


@dataclass
class PerformanceMetrics:
    """Performance metrics for a component."""
    component_name: str
    start_time: float
    end_time: Optional[float] = None
    duration: Optional[float] = None
    success: bool = True
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        if self.end_time and not self.duration:
            self.duration = self.end_time - self.start_time


class PerformanceMonitor:
    """Monitor for tracking performance metrics."""
    
    def __init__(self):
        self.logger = get_logger("PerformanceMonitor")
        self._metrics: Dict[str, list] = defaultdict(list)
        self._lock = threading.Lock()
    
    def start_timer(self, component_name: str, metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Start timing a component.
        
        Args:
            component_name: Name of the component being timed
            metadata: Additional metadata for the component
            
        Returns:
            Timer ID for tracking
        """
        timer_id = f"{component_name}_{int(time.time() * 1000)}"
        
        with self._lock:
            self._metrics[timer_id] = PerformanceMetrics(
                component_name=component_name,
                start_time=time.time(),
                metadata=metadata or {}
            )
        
        self.logger.debug(f"Started timer for {component_name}: {timer_id}")
        return timer_id
    
    def end_timer(self, timer_id: str, success: bool = True, error: Optional[str] = None) -> Optional[PerformanceMetrics]:
        """
        End timing a component.
        
        Args:
            timer_id: Timer ID from start_timer
            success: Whether the operation was successful
            error: Error message if failed
            
        Returns:
            Performance metrics or None if timer not found
        """
        with self._lock:
            if timer_id not in self._metrics:
                self.logger.warning(f"Timer not found: {timer_id}")
                return None
            
            metrics = self._metrics[timer_id]
            metrics.end_time = time.time()
            metrics.duration = metrics.end_time - metrics.start_time
            metrics.success = success
            metrics.error = error
            
            self.logger.debug(f"Ended timer for {metrics.component_name}: {metrics.duration:.3f}s")
            return metrics
    
    def get_metrics(self, component_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Get performance metrics.
        
        Args:
            component_name: Optional component name filter
            
        Returns:
            Dictionary of performance metrics
        """
        with self._lock:
            if component_name:
                filtered_metrics = {
                    timer_id: metrics for timer_id, metrics in self._metrics.items()
                    if metrics.component_name == component_name
                }
            else:
                filtered_metrics = dict(self._metrics)
            
            # Calculate summary statistics
            summary = self._calculate_summary(filtered_metrics)
            
            return {
                "metrics": filtered_metrics,
                "summary": summary
            }
    
    def _calculate_summary(self, metrics: Dict[str, PerformanceMetrics]) -> Dict[str, Any]:
        """Calculate summary statistics for metrics."""
        if not metrics:
            return {}
        
        durations = [m.duration for m in metrics.values() if m.duration is not None]
        success_count = sum(1 for m in metrics.values() if m.success)
        error_count = len(metrics) - success_count
        
        return {
            "total_operations": len(metrics),
            "successful_operations": success_count,
            "failed_operations": error_count,
            "success_rate": success_count / len(metrics) if metrics else 0,
            "average_duration": sum(durations) / len(durations) if durations else 0,
            "min_duration": min(durations) if durations else 0,
            "max_duration": max(durations) if durations else 0,
            "total_duration": sum(durations) if durations else 0
        }
    
    def clear_metrics(self, component_name: Optional[str] = None):
        """
        Clear performance metrics.
        
        Args:
            component_name: Optional component name filter
        """
        with self._lock:
            if component_name:
                # Remove metrics for specific component
                timer_ids_to_remove = [
                    timer_id for timer_id, metrics in self._metrics.items()
                    if metrics.component_name == component_name
                ]
                for timer_id in timer_ids_to_remove:
                    del self._metrics[timer_id]
            else:
                # Clear all metrics
                self._metrics.clear()
        
        self.logger.info(f"Cleared metrics for {component_name or 'all components'}")


def monitor_performance(component_name: Optional[str] = None):
    """
    Decorator for monitoring function performance.
    
    Args:
        component_name: Name of the component (defaults to function name)
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            monitor = PerformanceMonitor()
            name = component_name or func.__name__
            timer_id = monitor.start_timer(name)
            
            try:
                result = func(*args, **kwargs)
                monitor.end_timer(timer_id, success=True)
                return result
            except Exception as e:
                monitor.end_timer(timer_id, success=False, error=str(e))
                raise
        
        return wrapper
    return decorator


def monitor_flow_performance(flow_name: str):
    """
    Decorator for monitoring flow performance.
    
    Args:
        flow_name: Name of the flow
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            monitor = PerformanceMonitor()
            timer_id = monitor.start_timer(f"flow_{flow_name}")
            
            try:
                result = func(*args, **kwargs)
                monitor.end_timer(timer_id, success=True)
                return result
            except Exception as e:
                monitor.end_timer(timer_id, success=False, error=str(e))
                raise
        
        return wrapper
    return decorator


# Global performance monitor instance
performance_monitor = PerformanceMonitor() 