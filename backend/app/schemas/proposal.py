from __future__ import annotations

from datetime import datetime
from typing import Any, Dict

from pydantic import BaseModel, ConfigDict, Field


class ProposalBase(BaseModel):
    opportunity_id: str = Field(..., description="ID of the related Opportunity record")
    version: int = Field(..., description="Proposal version number")
    content: Dict[str, Any] = Field(
        ..., description="Generated proposal content (title, sections, pricing, timeline, etc.)"
    )

    model_config = ConfigDict(from_attributes=True)


class ProposalCreate(ProposalBase):
    pass


class ProposalResponse(ProposalBase):
    id: str = Field(..., description="Proposal record ID")
    created_at: datetime = Field(..., description="Timestamp of creation")
    updated_at: datetime = Field(..., description="Timestamp of last update")
