"""
Error Handler Utilities
Provides decorators for retry logic, error handling, and performance logging
"""

import logging
import time
from functools import wraps
from typing import Callable, Any
import os
from pathlib import Path

# Create logs directory
logs_dir = Path("logs")
logs_dir.mkdir(exist_ok=True)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(logs_dir / 'content_creation.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger('ContentCreation')


def retry_with_backoff(max_retries: int = 3, base_delay: float = 1.0):
    """
    Decorator for retry logic with exponential backoff
    
    Args:
        max_retries: Maximum number of retry attempts
        base_delay: Base delay in seconds (doubles each retry)
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            retries = 0
            last_exception = None
            
            while retries < max_retries:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    retries += 1
                    
                    if retries >= max_retries:
                        logger.error(f"Failed after {max_retries} attempts: {func.__name__}")
                        raise
                    
                    delay = base_delay * (2 ** (retries - 1))
                    logger.warning(f"Retry {retries}/{max_retries} for {func.__name__} after {delay}s delay")
                    time.sleep(delay)
            
            raise last_exception
            
        return wrapper
    return decorator


def handle_errors(error_message: str = "Operation failed"):
    """
    Decorator to gracefully handle errors with custom message
    
    Args:
        error_message: Custom error message to display
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logger.error(f"Error in {func.__name__}: {str(e)}", exc_info=True)
                return f"{error_message}: {str(e)}"
        return wrapper
    return decorator


def log_performance(func: Callable) -> Callable:
    """
    Decorator to log function performance
    
    Logs start time, end time, and duration of function execution
    """
    @wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        start_time = time.time()
        logger.info(f"Starting {func.__name__}")
        
        try:
            result = func(*args, **kwargs)
            duration = time.time() - start_time
            logger.info(f"Completed {func.__name__} in {duration:.2f}s")
            return result
        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"Failed {func.__name__} after {duration:.2f}s: {str(e)}")
            raise
    
    return wrapper


def log_agent_execution(agent_name: str):
    """
    Decorator specifically for logging agent executions
    
    Args:
        agent_name: Name of the agent being executed
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            logger.info(f"{'='*60}")
            logger.info(f"AGENT: {agent_name}")
            logger.info(f"{'='*60}")
            
            start_time = time.time()
            
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                logger.info(f"✅ {agent_name} completed successfully in {duration:.2f}s")
                return result
            except Exception as e:
                duration = time.time() - start_time
                logger.error(f"❌ {agent_name} failed after {duration:.2f}s: {str(e)}")
                raise
        
        return wrapper
    return decorator