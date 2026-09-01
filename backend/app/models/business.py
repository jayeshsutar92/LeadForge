from __future__ import annotations

from sqlalchemy import Boolean, Float, Index, Integer, String, Text, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
import uuid

from app.db.base_class import Base
from app.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin


class Business(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "businesses"
    __table_args__ = (
        Index("ix_businesses_slug_user", "slug", "user_id", unique=True),
        Index("ix_businesses_category", "category"),
        Index("ix_businesses_user_id", "user_id"),
    )

    discovery_session_ids: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )

    slug: Mapped[str] = mapped_column(String(255), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    category: Mapped[str] = mapped_column(String(255), nullable=False)
    city: Mapped[str] = mapped_column(String(255), nullable=False)
    country: Mapped[str] = mapped_column(String(255), nullable=False)
    bio: Mapped[str] = mapped_column(Text, nullable=False, default="")
    followers: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    engagement_rate: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    website: Mapped[str | None] = mapped_column(String(2048), nullable=True)
    instagram: Mapped[str | None] = mapped_column(String(2048), nullable=True)
    facebook: Mapped[str | None] = mapped_column(String(2048), nullable=True)
    cover_image: Mapped[str] = mapped_column(String(2048), nullable=False, default="")
    verified: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    # Detail fields used in get_business
    phone: Mapped[str | None] = mapped_column(String(50), nullable=True)
    has_online_orders: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    posts_last_30: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    # Relationship to contacts
    contacts: Mapped[list["BusinessContact"]] = relationship(
        "BusinessContact",
        back_populates="business",
        cascade="all, delete-orphan",
    )

    @property
    def opportunity_score(self) -> int:
        from app.services.scoring import compute_opportunity_score
        return compute_opportunity_score({
            "website": self.website,
            "followers": self.followers,
            "engagement_rate": self.engagement_rate,
            "posts_last_30": self.posts_last_30,
            "has_online_orders": self.has_online_orders,
            "category": self.category,
        })

    @property
    def tier(self) -> str:
        from app.services.scoring import score_tier
        return score_tier(self.opportunity_score)
