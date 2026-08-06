from __future__ import annotations

from datetime import datetime
from typing import Any, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


# ─── Activity Schemas ─────────────────────────────────────────────────────────

class ActivityBase(BaseModel):
    activity_type: str = Field(..., description="Type of activity (e.g., call, email, note, stage_change)")
    description: str = Field(..., description="Description of the activity")
    metadata_: dict[str, Any] = Field(default_factory=dict, alias="metadata")


class ActivityCreate(ActivityBase):
    pass


class ActivityResponse(ActivityBase):
    id: UUID
    lead_id: UUID
    user_id: Optional[UUID] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


# ─── Lead Schemas ─────────────────────────────────────────────────────────────

class LeadBase(BaseModel):
    status: str = Field(default="new")
    priority: int = Field(default=3, ge=1, le=3)
    source: str = Field(default="system")
    tags: list[str] = Field(default_factory=list)
    next_follow_up: Optional[datetime] = None
    notes: str = Field(default="")


class LeadCreate(LeadBase):
    business_id: UUID


class LeadUpdate(BaseModel):
    status: Optional[str] = None
    priority: Optional[int] = Field(None, ge=1, le=3)
    assigned_to: Optional[UUID] = None
    tags: Optional[list[str]] = None
    next_follow_up: Optional[datetime] = None
    notes: Optional[str] = None


class LeadResponse(LeadBase):
    id: UUID
    business_id: UUID
    assigned_to: Optional[UUID] = None
    last_contacted: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class LeadDetailResponse(LeadResponse):
    activities: list[ActivityResponse] = Field(default_factory=list)


class LeadListResponse(BaseModel):
    total: int
    results: list[LeadResponse]
