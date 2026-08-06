from typing import Any, Dict

from app.agents.providers.base import LLMProvider
from app.agents.providers.dummy import DummyProvider


class ProviderFactory:
    """Factory to instantiate interchangeable LLM providers based on configuration."""

    _PROVIDERS = {
        "dummy": DummyProvider,
        # Future integrations:
        # "openai": OpenAIProvider,
        # "anthropic": AnthropicProvider,
        # "gemini": GeminiProvider,
    }

    @classmethod
    def get_provider(cls, name: str, config: Dict[str, Any]) -> LLMProvider:
        name = name.lower()
        if name not in cls._PROVIDERS:
            raise ValueError(f"Unknown provider '{name}'. Available: {list(cls._PROVIDERS.keys())}")
        
        provider_class = cls._PROVIDERS[name]
        return provider_class(config)
