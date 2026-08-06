import asyncio
import logging
from functools import wraps
from typing import Any, Callable

logger = logging.getLogger("AgentUtils")


def retry_on_failure(max_retries: int = 3, delay: float = 1.0, backoff: float = 2.0) -> Callable:
    """Decorator to retry an async function upon failure."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            current_delay = delay
            for attempt in range(max_retries):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_retries - 1:
                        logger.error(f"Function {func.__name__} failed after {max_retries} attempts. Error: {str(e)}")
                        raise
                    logger.warning(f"Function {func.__name__} failed (attempt {attempt + 1}/{max_retries}). Retrying in {current_delay}s... Error: {str(e)}")
                    await asyncio.sleep(current_delay)
                    current_delay *= backoff
        return wrapper
    return decorator


def validate_agent_input(required_keys: list[str]) -> Callable:
    """Decorator to validate that specific keys exist in the input payload before execution."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(self: Any, input_data: dict[str, Any], *args: Any, **kwargs: Any) -> Any:
            missing = [k for k in required_keys if k not in input_data]
            if missing:
                raise ValueError(f"Agent {self.name} missing required input keys: {missing}")
            return await func(self, input_data, *args, **kwargs)
        return wrapper
    return decorator
