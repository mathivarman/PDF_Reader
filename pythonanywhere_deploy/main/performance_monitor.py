"""
Performance Monitor for System Optimization
Tracks processing times, memory usage, and system performance metrics
"""

import time
import psutil
import logging
from typing import Dict, Any, Optional, Callable, List
from functools import wraps
from datetime import datetime, timedelta
from django.conf import settings

logger = logging.getLogger(__name__)

class PerformanceMonitor:
    """Monitors and tracks system performance metrics."""
    
    def __init__(self):
        self.metrics = {}
        self.start_time = None
        self.end_time = None
    
    def start_monitoring(self, operation_name: str):
        """Start monitoring an operation."""
        self.start_time = time.time()
        self.metrics[operation_name] = {
            'start_time': datetime.now(),
            'memory_before': psutil.virtual_memory().used,
            'cpu_before': psutil.cpu_percent(interval=0.1)
        }
        logger.info(f"Started monitoring: {operation_name}")
    
    def end_monitoring(self, operation_name: str) -> Dict[str, Any]:
        """End monitoring and return metrics."""
        if not self.start_time or operation_name not in self.metrics:
            return {}
        
        self.end_time = time.time()
        duration = self.end_time - self.start_time
        
        memory_after = psutil.virtual_memory().used
        cpu_after = psutil.cpu_percent(interval=0.1)
        
        metrics = {
            'operation': operation_name,
            'duration_seconds': round(duration, 3),
            'memory_used_mb': round((memory_after - self.metrics[operation_name]['memory_before']) / 1024 / 1024, 2),
            'cpu_usage_percent': round((cpu_after + self.metrics[operation_name]['cpu_before']) / 2, 2),
            'start_time': self.metrics[operation_name]['start_time'],
            'end_time': datetime.now(),
            'status': 'completed'
        }
        
        self.metrics[operation_name].update(metrics)
        
        # Log performance metrics
        logger.info(f"Performance - {operation_name}: {duration:.3f}s, "
                   f"Memory: {metrics['memory_used_mb']}MB, CPU: {metrics['cpu_usage_percent']}%")
        
        return metrics
    
    def get_system_stats(self) -> Dict[str, Any]:
        """Get current system statistics."""
        try:
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            cpu_percent = psutil.cpu_percent(interval=1)
            
            return {
                'timestamp': datetime.now(),
                'memory': {
                    'total_gb': round(memory.total / 1024 / 1024 / 1024, 2),
                    'available_gb': round(memory.available / 1024 / 1024 / 1024, 2),
                    'used_percent': memory.percent,
                    'used_gb': round(memory.used / 1024 / 1024 / 1024, 2)
                },
                'disk': {
                    'total_gb': round(disk.total / 1024 / 1024 / 1024, 2),
                    'free_gb': round(disk.free / 1024 / 1024 / 1024, 2),
                    'used_percent': round((disk.used / disk.total) * 100, 2)
                },
                'cpu': {
                    'usage_percent': cpu_percent,
                    'count': psutil.cpu_count()
                }
            }
        except Exception as e:
            logger.error(f"Error getting system stats: {e}")
            return {'error': str(e)}
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get a summary of all monitored operations."""
        if not self.metrics:
            return {'message': 'No operations monitored yet'}
        
        total_operations = len(self.metrics)
        total_duration = sum(m.get('duration_seconds', 0) for m in self.metrics.values())
        avg_duration = total_duration / total_operations if total_operations > 0 else 0
        
        return {
            'total_operations': total_operations,
            'total_duration_seconds': round(total_duration, 3),
            'average_duration_seconds': round(avg_duration, 3),
            'operations': list(self.metrics.keys()),
            'last_operation': max(self.metrics.keys()) if self.metrics else None,
            'system_stats': self.get_system_stats()
        }

# Global performance monitor instance
performance_monitor = PerformanceMonitor()

def monitor_performance(operation_name: str = None):
    """Decorator to monitor function performance."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            op_name = operation_name or f"{func.__module__}.{func.__name__}"
            
            try:
                performance_monitor.start_monitoring(op_name)
                result = func(*args, **kwargs)
                performance_monitor.end_monitoring(op_name)
                return result
            except Exception as e:
                logger.error(f"Error in monitored function {op_name}: {e}")
                raise
        
        return wrapper
    return decorator

class PerformanceTracker:
    """Context manager for tracking performance of code blocks."""
    
    def __init__(self, operation_name: str):
        self.operation_name = operation_name
    
    def __enter__(self):
        performance_monitor.start_monitoring(self.operation_name)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        performance_monitor.end_monitoring(self.operation_name)
        if exc_type:
            logger.error(f"Error in performance tracked operation {self.operation_name}: {exc_val}")
        return False  # Don't suppress exceptions

def track_performance(operation_name: str):
    """Context manager for tracking performance."""
    return PerformanceTracker(operation_name)

# Add track_performance method to PerformanceMonitor class
PerformanceMonitor.track_performance = track_performance

# Utility functions for common performance checks
def check_memory_usage() -> Dict[str, Any]:
    """Check current memory usage."""
    try:
        memory = psutil.virtual_memory()
        return {
            'used_mb': round(memory.used / 1024 / 1024, 2),
            'available_mb': round(memory.available / 1024 / 1024, 2),
            'percent': memory.percent,
            'status': 'critical' if memory.percent > 90 else 'warning' if memory.percent > 70 else 'normal'
        }
    except Exception as e:
        logger.error(f"Error checking memory usage: {e}")
        return {'error': str(e)}

def check_disk_space() -> Dict[str, Any]:
    """Check available disk space."""
    try:
        disk = psutil.disk_usage('/')
        free_gb = disk.free / 1024 / 1024 / 1024
        return {
            'free_gb': round(free_gb, 2),
            'total_gb': round(disk.total / 1024 / 1024 / 1024, 2),
            'used_percent': round((disk.used / disk.total) * 100, 2),
            'status': 'critical' if free_gb < 1 else 'warning' if free_gb < 5 else 'normal'
        }
    except Exception as e:
        logger.error(f"Error checking disk space: {e}")
        return {'error': str(e)}

def get_performance_alerts() -> List[Dict[str, Any]]:
    """Get performance alerts based on system metrics."""
    alerts = []
    
    # Check memory usage
    memory = check_memory_usage()
    if memory.get('status') in ['warning', 'critical']:
        alerts.append({
            'type': 'memory',
            'level': memory['status'],
            'message': f"High memory usage: {memory['percent']}%",
            'timestamp': datetime.now()
        })
    
    # Check disk space
    disk = check_disk_space()
    if disk.get('status') in ['warning', 'critical']:
        alerts.append({
            'type': 'disk',
            'level': disk['status'],
            'message': f"Low disk space: {disk['free_gb']}GB free",
            'timestamp': datetime.now()
        })
    
    return alerts
