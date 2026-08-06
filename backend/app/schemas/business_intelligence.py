from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field


class BusinessIntelligenceData(BaseModel):
    """Full deterministic analysis payload"""
    website_metadata: Dict[str, Any]
    contacts: List[Dict[str, Any]]
    social_links: Dict[str, Any]
    technologies: List[str]
    seo: Dict[str, Any]
    structure: Dict[str, Any]
    summary: str

    model_config = ConfigDict(from_attributes=True)


class BusinessIntelligenceResult(BaseModel):
    id: str
    business_id: str
    analysis_type: str = Field(default="deterministic")
    created_at: str
    data: BusinessIntelligenceData

    model_config = ConfigDict(from_attributes=True)


class BusinessIntelligenceCreate(BaseModel):
    """Trigger deterministic analysis – no input needed"""

    model_config = ConfigDict(from_attributes=True)


class BusinessIntelligenceListResponse(BaseModel):
    total: int
    results: List[BusinessIntelligenceResult]

    model_config = ConfigDict(from_attributes=True)
