from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy import ForeignKey, Index, String, JSON
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base_class import Base
from app.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin


class SearchHistory(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "search_history"
    __table_args__ = (
        Index("ix_search_history_user_id_created_at", "user_id", "created_at"),
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    query: Mapped[str] = mapped_column(String(2048), nullable=False, default="")
    filters: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    result_count: Mapped[int] = mapped_column(nullable=False, default=0)
