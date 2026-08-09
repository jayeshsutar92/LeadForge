from typing import Any, Dict

from app.agents.providers.base import LLMProvider
from app.agents.providers.dummy import DummyProvider
from app.agents.providers.groq_provider import GroqProvider


class ProviderFactory:
    """Factory to instantiate interchangeable LLM providers based on configuration."""

    _PROVIDERS = {
        "dummy": DummyProvider,
        "groq": GroqProvider,
    }

    @classmethod
    def get_provider(cls, name: str, config: Dict[str, Any]) -> LLMProvider:
        name = name.lower()
        if name not in cls._PROVIDERS:
            raise ValueError(f"Unknown provider '{name}'. Available: {list(cls._PROVIDERS.keys())}")
        
        provider_class = cls._PROVIDERS[name]
        return provider_class(config)
