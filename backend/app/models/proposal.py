from __future__ import annotations

import uuid

from sqlalchemy import JSON, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base_class import Base
from app.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin


class Proposal(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "proposal"
    __table_args__ = (
        Index("ix_proposal_opportunity_id_created", "opportunity_id", "created_at"),
    )

    opportunity_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("opportunity.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    version: Mapped[int] = mapped_column(nullable=False, default=1, server_default="1")
    # Store the generated proposal content (title, sections, pricing, timeline, etc.)
    content: Mapped[dict] = mapped_column(JSON, nullable=False)
