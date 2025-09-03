"""
XMRT-Ecosystem Memory Optimizer
Comprehensive memory management for Render's 512MB free tier limit.

Features:
- Real-time memory monitoring with 30-second intervals
- Automatic garbage collection at 80% memory threshold
- Vector embedding batch size limiting
- Smart cache management with LRU eviction
- Memory usage logging and emergency cleanup
- Integration with autonomous learning system
"""

import os
import gc
import time
import threading
import psutil
import logging
from datetime import datetime, timedelta
from functools import wraps
from typing import Optional, Dict, Any, Callable, List
import weakref
import sys
from collections import OrderedDict
import json

class MemoryOptimizer:
    """
    Advanced memory management system for Render 512MB deployment.
    Monitors, optimizes, and prevents memory overruns in autonomous learning system.
    """

    def __init__(self, max_memory_mb: int = 450, gc_threshold: float = 0.8):
        self.max_memory_mb = int(os.getenv('MAX_MEMORY_MB', max_memory_mb))
        self.gc_threshold = float(os.getenv('GC_THRESHOLD_RATIO', gc_threshold))
        self.monitoring = True
        self.cleanup_count = 0
        self.peak_memory = 0
        self.last_cleanup = None

        # Setup logging
        self.logger = self._setup_logging()

        # Memory tracking
        self.memory_history = []
        self.max_history_size = 100

        # Cache management
        self.caches = {}
        self.cache_limits = {
            'vector_embeddings': int(os.getenv('VECTOR_CACHE_SIZE', 50)),
            'github_data': int(os.getenv('GITHUB_CACHE_SIZE', 30)),
            'agent_responses': int(os.getenv('AGENT_CACHE_SIZE', 20)),
            'memory_patterns': int(os.getenv('PATTERN_CACHE_SIZE', 40))
        }

        # Emergency thresholds
        self.emergency_threshold = 0.95  # 95% of max memory
        self.critical_threshold = 0.98   # 98% of max memory

        self.logger.info(f"MemoryOptimizer initialized: {self.max_memory_mb}MB limit, {self.gc_threshold:.1%} GC threshold")

    def _setup_logging(self) -> logging.Logger:
        """Setup memory-specific logging"""
        logger = logging.getLogger('memory_optimizer')
        logger.setLevel(logging.INFO)

        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)

        return logger

    def get_memory_info(self) -> Dict[str, float]:
        """Get detailed memory information"""
        try:
            process = psutil.Process()
            memory_info = process.memory_info()

            return {
                'rss_mb': memory_info.rss / 1024 / 1024,  # Resident Set Size
                'vms_mb': memory_info.vms / 1024 / 1024,  # Virtual Memory Size
                'percent': process.memory_percent(),
                'available_mb': self.max_memory_mb - (memory_info.rss / 1024 / 1024),
                'threshold_mb': self.max_memory_mb * self.gc_threshold,
                'emergency_mb': self.max_memory_mb * self.emergency_threshold
            }
        except Exception as e:
            self.logger.error(f"Failed to get memory info: {e}")
            return {'rss_mb': 0, 'vms_mb': 0, 'percent': 0, 'available_mb': self.max_memory_mb}

    def check_memory_usage(self) -> bool:
        """Check current memory usage and trigger cleanup if needed"""
        memory_info = self._get_memory_usage()
        current_memory = memory_info['rss_mb']

        # Update peak memory
        if current_memory > self.peak_memory:
            self.peak_memory = current_memory

        # Add to history
        self._add_to_history(memory_info)

        # Check thresholds
        threshold_memory = self.max_memory_mb * self.gc_threshold
        emergency_memory = self.max_memory_mb * self.emergency_threshold
        critical_memory = self.max_memory_mb * self.critical_threshold

        if current_memory > critical_memory:
            self.logger.critical(f"CRITICAL MEMORY: {current_memory:.1f}MB (>{critical_memory:.1f}MB)")
            return self._emergency_cleanup()
        elif current_memory > emergency_memory:
            self.logger.warning(f"EMERGENCY MEMORY: {current_memory:.1f}MB (>{emergency_memory:.1f}MB)")
            return self._aggressive_cleanup()
        elif current_memory > threshold_memory:
            self.logger.info(f"Memory cleanup triggered: {current_memory:.1f}MB (>{threshold_memory:.1f}MB)")
            return self._standard_cleanup()

        return False

    def _get_memory_usage(self) -> Dict[str, float]:
        """Internal method to get memory usage"""
        try:
            process = psutil.Process()
            memory_info = process.memory_info()
            return {
                'rss_mb': memory_info.rss / 1024 / 1024,
                'vms_mb': memory_info.vms / 1024 / 1024,
                'percent': process.memory_percent(),
                'timestamp': datetime.now().isoformat()
            }
        except Exception:
            return {'rss_mb': 0, 'vms_mb': 0, 'percent': 0, 'timestamp': datetime.now().isoformat()}

    def _add_to_history(self, memory_info: Dict[str, float]):
        """Add memory info to history with size limit"""
        self.memory_history.append(memory_info)
        if len(self.memory_history) > self.max_history_size:
            self.memory_history = self.memory_history[-self.max_history_size:]

    def _standard_cleanup(self) -> bool:
        """Standard cleanup procedure"""
        initial_memory = self._get_memory_usage()['rss_mb']

        # Force garbage collection
        collected = gc.collect()

        # Clear least important caches
        self._cleanup_caches(['agent_responses'])

        final_memory = self._get_memory_usage()['rss_mb']
        saved_memory = initial_memory - final_memory

        self.cleanup_count += 1
        self.last_cleanup = datetime.now()

        self.logger.info(f"Standard cleanup: {initial_memory:.1f}MB -> {final_memory:.1f}MB (saved {saved_memory:.1f}MB, collected {collected} objects)")
        return True

    def _aggressive_cleanup(self) -> bool:
        """Aggressive cleanup for high memory usage"""
        initial_memory = self._get_memory_usage()['rss_mb']

        # Multiple garbage collection passes
        total_collected = 0
        for _ in range(3):
            total_collected += gc.collect()

        # Clear multiple cache types
        self._cleanup_caches(['agent_responses', 'github_data', 'memory_patterns'])

        # Trim memory history
        if len(self.memory_history) > 20:
            self.memory_history = self.memory_history[-20:]

        final_memory = self._get_memory_usage()['rss_mb']
        saved_memory = initial_memory - final_memory

        self.cleanup_count += 1
        self.last_cleanup = datetime.now()

        self.logger.warning(f"Aggressive cleanup: {initial_memory:.1f}MB -> {final_memory:.1f}MB (saved {saved_memory:.1f}MB, collected {total_collected} objects)")
        return True

    def _emergency_cleanup(self) -> bool:
        """Emergency cleanup for critical memory usage"""
        initial_memory = self._get_memory_usage()['rss_mb']

        # Maximum garbage collection
        total_collected = 0
        for _ in range(5):
            total_collected += gc.collect()

        # Clear ALL caches
        self._cleanup_caches(list(self.cache_limits.keys()))

        # Minimal memory history
        self.memory_history = self.memory_history[-10:] if self.memory_history else []

        # Force immediate memory release
        try:
            import ctypes
            libc = ctypes.CDLL("libc.so.6")
            libc.malloc_trim(0)
        except Exception:
            pass  # Not available on all systems

        final_memory = self._get_memory_usage()['rss_mb']
        saved_memory = initial_memory - final_memory

        self.cleanup_count += 1
        self.last_cleanup = datetime.now()

        self.logger.critical(f"EMERGENCY cleanup: {initial_memory:.1f}MB -> {final_memory:.1f}MB (saved {saved_memory:.1f}MB, collected {total_collected} objects)")
        return True

    def _cleanup_caches(self, cache_types: List[str]):
        """Clean up specified cache types"""
        for cache_type in cache_types:
            if cache_type in self.caches:
                original_size = len(self.caches[cache_type])
                self.caches[cache_type].clear()
                self.logger.debug(f"Cleared {cache_type} cache: {original_size} items")

    def monitor_memory(self):
        """Background memory monitoring loop"""
        self.logger.info("Starting memory monitoring (30s intervals)")

        while self.monitoring:
            try:
                self.check_memory_usage()
                time.sleep(30)  # Check every 30 seconds
            except Exception as e:
                self.logger.error(f"Memory monitoring error: {e}")
                time.sleep(60)  # Longer sleep on error

    def start_monitoring(self):
        """Start background memory monitoring thread"""
        if hasattr(self, '_monitor_thread') and self._monitor_thread.is_alive():
            self.logger.warning("Memory monitoring already running")
            return

        self._monitor_thread = threading.Thread(target=self.monitor_memory, daemon=True)
        self._monitor_thread.start()
        self.logger.info("Memory monitoring started")

    def stop_monitoring(self):
        """Stop memory monitoring"""
        self.monitoring = False
        if hasattr(self, '_monitor_thread'):
            self._monitor_thread.join(timeout=5)
        self.logger.info("Memory monitoring stopped")

    def get_cache(self, cache_type: str, max_size: Optional[int] = None) -> 'LRUCache':
        """Get or create an LRU cache of specified type"""
        if cache_type not in self.caches:
            limit = max_size or self.cache_limits.get(cache_type, 50)
            self.caches[cache_type] = LRUCache(limit)
            self.logger.debug(f"Created {cache_type} cache with limit {limit}")

        return self.caches[cache_type]

    def get_memory_stats(self) -> Dict[str, Any]:
        """Get comprehensive memory statistics"""
        current_memory = self.get_memory_info()

        return {
            'current': current_memory,
            'peak_memory_mb': self.peak_memory,
            'cleanup_count': self.cleanup_count,
            'last_cleanup': self.last_cleanup.isoformat() if self.last_cleanup else None,
            'cache_stats': {
                cache_type: len(cache) for cache_type, cache in self.caches.items()
            },
            'memory_history_size': len(self.memory_history),
            'monitoring_active': self.monitoring
        }

    def log_memory_stats(self):
        """Log current memory statistics"""
        stats = self.get_memory_stats()
        current = stats['current']

        self.logger.info(
            f"Memory Stats: {current['rss_mb']:.1f}MB used, "
            f"{current['available_mb']:.1f}MB available, "
            f"{self.cleanup_count} cleanups, "
            f"Peak: {self.peak_memory:.1f}MB"
        )


class LRUCache:
    """Least Recently Used cache with size limit for memory management"""

    def __init__(self, max_size: int):
        self.max_size = max_size
        self.cache = OrderedDict()

    def get(self, key: str, default=None):
        """Get item from cache, moving it to end (most recent)"""
        if key in self.cache:
            # Move to end (most recent)
            value = self.cache.pop(key)
            self.cache[key] = value
            return value
        return default

    def put(self, key: str, value: Any):
        """Add item to cache, evicting oldest if at capacity"""
        if key in self.cache:
            # Update existing item
            self.cache.pop(key)
        elif len(self.cache) >= self.max_size:
            # Evict oldest item
            self.cache.popitem(last=False)

        self.cache[key] = value

    def clear(self):
        """Clear all items from cache"""
        self.cache.clear()

    def __len__(self):
        return len(self.cache)

    def __contains__(self, key):
        return key in self.cache


def memory_limited(batch_size: int = 50, cache_type: str = 'default'):
    """
    Decorator to limit batch operations and add caching for memory management
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Get memory optimizer instance
            optimizer = get_memory_optimizer()

            # Check memory before operation
            if optimizer:
                optimizer.check_memory_usage()

            # Limit batch size for memory-intensive operations
            if 'batch_size' in kwargs:
                kwargs['batch_size'] = min(kwargs['batch_size'], batch_size)
            elif 'limit' in kwargs:
                kwargs['limit'] = min(kwargs['limit'], batch_size)

            # Add caching if cache_key provided
            cache_key = kwargs.pop('cache_key', None)
            if cache_key and optimizer:
                cache = optimizer.get_cache(cache_type)
                cached_result = cache.get(cache_key)
                if cached_result is not None:
                    return cached_result

            # Execute function
            result = func(*args, **kwargs)

            # Cache result if cache_key provided
            if cache_key and optimizer and result is not None:
                cache = optimizer.get_cache(cache_type)
                cache.put(cache_key, result)

            return result
        return wrapper
    return decorator


def batch_processor(items: List[Any], batch_size: int = 50, processor_func: Callable = None):
    """
    Process items in memory-safe batches with automatic cleanup
    """
    optimizer = get_memory_optimizer()
    results = []

    for i in range(0, len(items), batch_size):
        batch = items[i:i + batch_size]

        # Check memory before processing batch
        if optimizer:
            optimizer.check_memory_usage()

        # Process batch
        if processor_func:
            batch_results = processor_func(batch)
            if isinstance(batch_results, list):
                results.extend(batch_results)
            else:
                results.append(batch_results)

        # Force cleanup after every 5th batch
        if (i // batch_size) % 5 == 0 and optimizer:
            gc.collect()

    return results


# Global memory optimizer instance
_memory_optimizer: Optional[MemoryOptimizer] = None

def get_memory_optimizer() -> Optional[MemoryOptimizer]:
    """Get the global memory optimizer instance"""
    return _memory_optimizer

def initialize_memory_optimizer(max_memory_mb: int = 450, gc_threshold: float = 0.8) -> MemoryOptimizer:
    """Initialize the global memory optimizer"""
    global _memory_optimizer

    if _memory_optimizer is None:
        _memory_optimizer = MemoryOptimizer(max_memory_mb, gc_threshold)
        _memory_optimizer.start_monitoring()

    return _memory_optimizer

def cleanup_memory_optimizer():
    """Cleanup and stop the memory optimizer"""
    global _memory_optimizer

    if _memory_optimizer:
        _memory_optimizer.stop_monitoring()
        _memory_optimizer = None


# Integration hooks for autonomous learning system
class AutonomousMemoryIntegration:
    """Integration class for autonomous learning system memory management"""

    @staticmethod
    def pre_learning_cycle():
        """Call before starting a learning cycle"""
        optimizer = get_memory_optimizer()
        if optimizer:
            optimizer.check_memory_usage()
            optimizer.log_memory_stats()

    @staticmethod
    def post_learning_cycle():
        """Call after completing a learning cycle"""
        optimizer = get_memory_optimizer()
        if optimizer:
            gc.collect()  # Cleanup after cycle
            optimizer.log_memory_stats()

    @staticmethod
    def pre_agent_collaboration():
        """Call before multi-agent collaboration"""
        optimizer = get_memory_optimizer()
        if optimizer and optimizer.get_memory_info()['rss_mb'] > optimizer.max_memory_mb * 0.7:
            optimizer._standard_cleanup()

    @staticmethod
    def emergency_memory_check() -> bool:
        """Emergency memory check - returns True if memory is critical"""
        optimizer = get_memory_optimizer()
        if optimizer:
            memory_info = optimizer.get_memory_info()
            return memory_info['rss_mb'] > optimizer.max_memory_mb * 0.95
        return False


# Environment variable configuration
def setup_render_environment():
    """Setup environment variables for Render deployment"""
    env_config = {
        'MAX_MEMORY_MB': '450',
        'GC_THRESHOLD_RATIO': '0.8',
        'VECTOR_BATCH_SIZE': '50',
        'VECTOR_CACHE_SIZE': '50',
        'GITHUB_CACHE_SIZE': '30',
        'AGENT_CACHE_SIZE': '20',
        'PATTERN_CACHE_SIZE': '40'
    }

    for key, default_value in env_config.items():
        if key not in os.environ:
            os.environ[key] = default_value


if __name__ == "__main__":
    # Setup environment and initialize optimizer for testing
    setup_render_environment()
    optimizer = initialize_memory_optimizer()

    print("Memory Optimizer initialized for XMRT-Ecosystem")
    print(f"Max Memory: {optimizer.max_memory_mb}MB")
    print(f"GC Threshold: {optimizer.gc_threshold:.1%}")

    # Log initial stats
    optimizer.log_memory_stats()

    try:
        # Keep running for testing
        time.sleep(60)
    except KeyboardInterrupt:
        print("\nStopping memory optimizer...")
    finally:
        cleanup_memory_optimizer()
        print("Memory optimizer stopped")
