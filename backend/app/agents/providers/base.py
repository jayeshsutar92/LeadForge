from abc import ABC, abstractmethod
from typing import Any, Dict


class LLMProvider(ABC):
    """Base interface for all LLM providers."""

    @abstractmethod
    def __init__(self, config: Dict[str, Any]) -> None:
        """Initialize with configuration (API keys, models, etc.)."""
        self.config = config

    @abstractmethod
    async def generate(self, prompt: str, **kwargs) -> str:
        """Generate text from a prompt."""
        raise NotImplementedError

    @abstractmethod
    async def generate_json(self, prompt: str, schema: Dict[str, Any] | None = None, **kwargs) -> Dict[str, Any]:
        """Generate a structured JSON response."""
        raise NotImplementedError
