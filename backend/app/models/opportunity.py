from __future__ import annotations

from sqlalchemy import JSON, String, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base_class import Base
from app.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin


class Opportunity(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "opportunity"
    __table_args__ = (
        Index("ix_opportunity_business_intelligence_id_created", "business_intelligence_id", "created_at"),
    )

    business_intelligence_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("business_intelligence.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    # Store full recommendation payload (score, tier, theme, palette, sections, price_range, rationale)
    data: Mapped[dict] = mapped_column(JSON, nullable=False)
