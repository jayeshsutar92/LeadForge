from __future__ import annotations

import uuid

from sqlalchemy import JSON, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base_class import Base
from app.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin


class BusinessIntelligence(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "business_intelligence"
    __table_args__ = (
        Index("ix_business_intelligence_business_id_created", "business_id", "created_at"),
    )

    business_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("businesses.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    analysis_type: Mapped[str] = mapped_column(nullable=False, default="deterministic", server_default="deterministic")
    data: Mapped[dict] = mapped_column(JSON, nullable=False)
