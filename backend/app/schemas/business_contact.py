from pydantic import BaseModel, Field
from uuid import UUID

class BusinessContactBase(BaseModel):
    slug: str = Field(..., max_length=255)
    name: str = Field(..., max_length=255)
    title: str | None = None
    email: str | None = None
    phone: str | None = None
    notes: str | None = None

class BusinessContactCreate(BusinessContactBase):
    business_id: UUID

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

    class Config:
        from_attributes = True
