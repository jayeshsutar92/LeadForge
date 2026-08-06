from __future__ import annotations

from typing import Dict, Any


class SharedContext:
    """Simple shared context for agents.

    Acts as a mutable store that agents can read from and write to.
    Internally uses a dict.
    """

    def __init__(self, initial: Dict[str, Any] | None = None) -> None:
        self._store: Dict[str, Any] = initial or {}

    def get(self, key: str, default: Any = None) -> Any:
        return self._store.get(key, default)

    def set(self, key: str, value: Any) -> None:
        self._store[key] = value

    def as_dict(self) -> Dict[str, Any]:
        return dict(self._store)
