from typing import Optional
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class BusinessCard(BaseModel):
    id: UUID
    slug: str
    name: str
    category: str
    city: str
    state: Optional[str] = None
    country: str
    bio: str
    followers: int
    engagement_rate: float
    website: Optional[str] = None
    website_status: Optional[str] = None
    instagram_status: Optional[str] = None
    facebook_status: Optional[str] = None
    evidence_log: Optional[dict] = None
    evidence_hash: Optional[str] = None
    instagram: Optional[str]
    facebook: Optional[str]
    cover_image: str
    opportunity_score: int
    tier: str
    verified: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class BusinessDetail(BaseModel):
    business: BusinessCard
    detail: dict
    recommendation: dict


class BusinessListResponse(BaseModel):
    total: int
    results: list[BusinessCard]
