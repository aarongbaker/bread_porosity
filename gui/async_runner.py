"""
Async/Threading Manager
Centralizes all async operations and thread management
"""

import threading
from typing import Callable, Optional, Any
from queue import Queue
import logging

logger = logging.getLogger(__name__)


class AsyncRunner:
    """Manages asynchronous operations using threading"""
    
    def __init__(self):
        self._threads = {}
        self._counter = 0
    
    def run_async(self,
                  func: Callable,
                  callback: Optional[Callable[[Any], None]] = None,
                  error_callback: Optional[Callable[[Exception], None]] = None,
                  name: Optional[str] = None) -> str:
        """
        Run a function asynchronously in a thread
        
        Args:
            func: Function to execute
            callback: Function to call with result when complete
            error_callback: Function to call if error occurs
            name: Optional name for the thread (for debugging)
        
        Returns:
            Thread ID for reference
        """
        self._counter += 1
        thread_id = name or f"async_{self._counter}"
        
        def worker():
            try:
                result = func()
                if callback:
                    callback(result)
            except Exception as e:
                logger.error(f"Error in async operation {thread_id}: {e}", exc_info=True)
                if error_callback:
                    error_callback(e)
                else:
                    raise
        
        thread = threading.Thread(target=worker, daemon=True, name=thread_id)
        self._threads[thread_id] = thread
        thread.start()
        
        return thread_id
    
    def wait_for_thread(self, thread_id: str, timeout: Optional[float] = None) -> bool:
        """
        Wait for a specific thread to complete
        
        Args:
            thread_id: ID of thread to wait for
            timeout: Maximum time to wait (seconds)
        
        Returns:
            True if thread completed, False if timeout
        """
        if thread_id not in self._threads:
            logger.warning(f"Thread {thread_id} not found")
            return False
        
        self._threads[thread_id].join(timeout=timeout)
        return not self._threads[thread_id].is_alive()
    
    def is_running(self, thread_id: str) -> bool:
        """Check if a thread is still running"""
        if thread_id not in self._threads:
            return False
        return self._threads[thread_id].is_alive()


# Global async runner instance
_async_runner_instance = None


def get_async_runner() -> AsyncRunner:
    """Get global async runner instance (singleton)"""
    global _async_runner_instance
    if _async_runner_instance is None:
        _async_runner_instance = AsyncRunner()
    return _async_runner_instance
