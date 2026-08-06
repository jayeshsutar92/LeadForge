from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class BusinessContactBase(BaseModel):
    slug: str = Field(..., max_length=255)
    name: str = Field(..., max_length=255)
    title: str | None = None
    email: str | None = None
    phone: str | None = None
    notes: str | None = None


class BusinessContactCreate(BusinessContactBase):
    """Create payload — business_id is inferred from the URL path."""
    pass


class BusinessContactUpdate(BaseModel):
    slug: str | None = None
    name: str | None = None
    title: str | None = None
    email: str | None = None
    phone: str | None = None
    notes: str | None = None


class BusinessContactOut(BusinessContactBase):
    id: UUID
    business_id: UUID

    model_config = ConfigDict(from_attributes=True)
