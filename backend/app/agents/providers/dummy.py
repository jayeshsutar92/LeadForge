from typing import Any, Dict

from app.agents.providers.base import LLMProvider


class DummyProvider(LLMProvider):
    """A dummy provider that returns static responses, used for deterministic testing/fallback."""

    def __init__(self, config: Dict[str, Any]) -> None:
        super().__init__(config)
        self.config = config

    async def generate(self, prompt: str, **kwargs) -> str:
        return f"Mocked generation for: {prompt[:50]}..."

    async def generate_json(self, prompt: str, schema: Dict[str, Any] | None = None, **kwargs) -> Dict[str, Any]:
        return {"status": "success", "mocked": True, "prompt_preview": prompt[:20]}
