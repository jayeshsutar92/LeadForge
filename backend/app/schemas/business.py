from typing import Optional

from pydantic import BaseModel, ConfigDict


class BusinessCard(BaseModel):
    id: str
    slug: str
    name: str
    category: str
    city: str
    country: str
    bio: str
    followers: int
    engagement_rate: float
    website: Optional[str]
    instagram: Optional[str]
    facebook: Optional[str]
    cover_image: str
    opportunity_score: int
    tier: str
    verified: bool

    model_config = ConfigDict(from_attributes=True)


class BusinessDetail(BaseModel):
    business: BusinessCard
    detail: dict
    recommendation: dict


class BusinessListResponse(BaseModel):
    total: int
    results: list[BusinessCard]
