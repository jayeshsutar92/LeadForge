from __future__ import annotations

from datetime import datetime
from typing import Any, Dict

from pydantic import BaseModel, ConfigDict, Field


class OpportunityBase(BaseModel):
    business_intelligence_id: str = Field(..., description="ID of the related Business Intelligence record")
    data: Dict[str, Any] = Field(..., description="Full recommendation payload from scoring engine")

    model_config = ConfigDict(from_attributes=True)


class OpportunityCreate(OpportunityBase):
    pass


class OpportunityResponse(OpportunityBase):
    id: str = Field(..., description="Opportunity record ID")
    created_at: datetime = Field(..., description="Timestamp of creation")
    updated_at: datetime = Field(..., description="Timestamp of last update")
