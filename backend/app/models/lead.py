from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, Index, Integer, String, Text, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base
from app.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin


class Lead(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "leads"
    __table_args__ = (
        Index("ix_leads_business_id", "business_id", unique=True),
        Index("ix_leads_status", "status"),
        Index("ix_leads_assigned_to", "assigned_to"),
        Index("ix_leads_user_id", "user_id"),
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )

    business_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("businesses.id", ondelete="CASCADE"),
        nullable=False,
    )
    assigned_to: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    status: Mapped[str] = mapped_column(String(50), nullable=False, default="new")
    priority: Mapped[int] = mapped_column(Integer, nullable=False, default=3) # 1: High, 2: Medium, 3: Low
    source: Mapped[str] = mapped_column(String(100), nullable=False, default="system")
    tags: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    discovery_session_ids: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)

    next_follow_up: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_contacted: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    notes: Mapped[str] = mapped_column(Text, nullable=False, default="")

    business: Mapped["Business"] = relationship("Business")
    assignee: Mapped["User"] = relationship("User", foreign_keys=[assigned_to])
    owner: Mapped["User"] = relationship("User", foreign_keys=[user_id])
    activities: Mapped[list["Activity"]] = relationship(
        "Activity",
        back_populates="lead",
        cascade="all, delete-orphan",
        order_by="desc(Activity.created_at)",
    )


class Activity(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "activities"
    __table_args__ = (
        Index("ix_activities_lead_id_created", "lead_id", "created_at"),
    )

    lead_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("leads.id", ondelete="CASCADE"),
        nullable=False,
    )
    user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    activity_type: Mapped[str] = mapped_column(String(50), nullable=False) # e.g., 'email', 'call', 'note', 'stage_change'
    description: Mapped[str] = mapped_column(Text, nullable=False)
    metadata_: Mapped[dict] = mapped_column("metadata", JSON, nullable=False, default=dict)

    lead: Mapped["Lead"] = relationship("Lead", back_populates="activities")
    user: Mapped["User"] = relationship("User")
