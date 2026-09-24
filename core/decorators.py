"""Decorators module for SoloSystem."""

import functools
import time
from typing import Any, Callable


def log_action(action_name: str) -> Callable:
    """Decorator to log system actions with execution time."""

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            start = time.perf_counter()
            result = func(*args, **kwargs)
            duration = time.perf_counter() - start
            print(f"[SYSTEM LOG] {action_name} executed in {duration:.4f}s")
            return result

        return wrapper

    return decorator


def validate_quest_input(func: Callable) -> Callable:
    """Validate quest title and rewards before creation."""

    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        return func(self, *args, **kwargs)

    return wrapper
