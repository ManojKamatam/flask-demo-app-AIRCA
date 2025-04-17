import time
import random
import requests
import logging
import threading
from functools import wraps

# Global cache for memory leak demonstration
_memory_leak_cache = []

def simulate_memory_leak(data_size=1000):
    """Simulates a memory leak by storing data in a global cache that's never cleared"""
    from config import Config
    
    if Config.MEMORY_LEAK_ENABLED:
        # Generate random data and add to global cache (never cleaned up)
        leaked_data = [random.random() for _ in range(data_size)]
        _memory_leak_cache.append(leaked_data)
        return len(_memory_leak_cache)
    return 0

def slow_external_api_call(endpoint="https://httpbin.org/delay/2"):
    """Simulates a slow external API call"""
    try:
        from config import Config
        timeout = Config.API_TIMEOUT
        
        response = requests.get(endpoint, timeout=timeout)
        return response.json()
    except requests.exceptions.Timeout:
        # Swallowed exception - bad practice
        return {"error": "Timeout"}
    except Exception as e:
        # Generic exception catching - another bad practice
        return {"error": str(e)}

def heavy_calculation(iterations=10**7):
    """CPU-intensive calculation that can cause performance issues"""
    result = 0
    for i in range(iterations):
        result += i * random.random()
    return result

def sometimes_fails(failure_rate=0.3):
    """Function that randomly fails a percentage of the time"""
    if random.random() < failure_rate:
        error_types = [
            ValueError("Random value error occurred"),
            TypeError("Unexpected type conversion error"),
            RuntimeError("Runtime exception occurred"),
            KeyError("Missing key in dictionary"),
            ZeroDivisionError("Division by zero"),
            # Uncomment to see uncaught exceptions:
            # Exception("Unhandled generic exception")
        ]
        raise random.choice(error_types)
    return "Function executed successfully"

def background_task():
    """Long-running background task that blocks a thread"""
    time.sleep(10)  # Blocks a thread for 10 seconds
    return "Background task completed"

def start_background_task():
    """Starts a background task in a separate thread"""
    thread = threading.Thread(target=background_task)
    thread.daemon = True  # Thread will exit when main program exits
    thread.start()
    return thread

def timed_function(f):
    """Decorator to time function execution"""
    @wraps(f)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = f(*args, **kwargs)
        end = time.time()
        elapsed = end - start
        if elapsed > 1:  # Log if function takes more than 1 second
            logging.warning(f"Slow function: {f.__name__} took {elapsed:.2f} seconds")
        return result
    return wrapper
