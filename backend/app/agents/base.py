from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from typing import Any, Dict

from app.agents.context import SharedContext
from app.agents.llm_provider import LLMProvider


class BaseAgent(ABC):
    """Abstract base class for all agents.

    Agents receive a shared context, can use an LLM provider, and must implement
    an asynchronous `run` method that returns a result dictionary.
    """

    def __init__(
        self,
        name: str,
        context: SharedContext | None = None,
        llm_provider: LLMProvider | None = None,
        logger: logging.Logger | None = None,
    ) -> None:
        self.name = name
        self.context = context or SharedContext()
        self.llm_provider = llm_provider
        self.logger = logger or logging.getLogger(name)

    @abstractmethod
    async def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the agent logic.

        Args:
            input_data: Arbitrary payload provided by the caller or previous agents.
        Returns:
            A dictionary with the agent's output that will be merged back into the shared context.
        """
        raise NotImplementedError

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Agent {self.name}>"
