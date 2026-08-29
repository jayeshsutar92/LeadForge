from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class ContactDiscoveryCandidate(BaseModel):
    platform: str
    title: str
    href: str
    username: str | None = None
    body: str


class ContactDiscoveryResult(BaseModel):
    candidates: list[ContactDiscoveryCandidate]


class ContactDiscoveryResponse(BaseModel):
    id: UUID
    business_id: UUID
    data: ContactDiscoveryResult
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
