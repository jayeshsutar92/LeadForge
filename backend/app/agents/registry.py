from typing import Dict, Type

from app.agents.base import BaseAgent


class AgentRegistry:
    """Registry to keep track of available agents dynamically."""

    _agents: Dict[str, Type[BaseAgent]] = {}

    @classmethod
    def register(cls, name: str, agent_class: Type[BaseAgent]) -> None:
        if name in cls._agents:
            raise ValueError(f"Agent '{name}' is already registered.")
        cls._agents[name] = agent_class

    @classmethod
    def get(cls, name: str) -> Type[BaseAgent]:
        if name not in cls._agents:
            raise ValueError(f"Agent '{name}' not found in registry.")
        return cls._agents[name]

    @classmethod
    def list_agents(cls) -> list[str]:
        return list(cls._agents.keys())
