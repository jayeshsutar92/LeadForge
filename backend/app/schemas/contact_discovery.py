from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class ContactDiscoveryCandidate(BaseModel):
    platform: str
    title: str
    href: str
    username: str | None = None
    display_name: str | None = None
    bio: str | None = None
    body: str
    confidence: int = 0
    status: str = "Rejected"  # "Verified", "Possible Match", "Rejected"
    evidence: list[str] = []


class ContactDiscoveryResult(BaseModel):
    candidates: list[ContactDiscoveryCandidate]
    recommended_platform: str | None = None
    messages: dict[str, str] | None = None


class ContactDiscoveryResponse(BaseModel):
    id: UUID
    business_id: UUID
    data: ContactDiscoveryResult
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
