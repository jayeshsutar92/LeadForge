from __future__ import annotations

from sqlalchemy import JSON, String, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base_class import Base
from app.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin


class Proposal(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = 'proposal'
    __table_args__ = (
        Index('ix_proposal_opportunity_id_created', 'opportunity_id', 'created_at'),
    )

    opportunity_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey('opportunity.id', ondelete='CASCADE'),
        nullable=False,
        index=True,
    )
    version: Mapped[int] = mapped_column(String, nullable=False, default='1')
    # Store the generated proposal content (title, sections, pricing, timeline, etc.)
    content: Mapped[dict] = mapped_column(JSON, nullable=False)
