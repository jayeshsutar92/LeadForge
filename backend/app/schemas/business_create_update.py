from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, validator


class BusinessCreate(BaseModel):
    slug: str = Field(..., min_length=1, max_length=255)
    name: str = Field(..., min_length=1, max_length=255)
    category: str = Field(..., min_length=1, max_length=255)
    city: str = Field(..., min_length=1, max_length=255)
    country: str = Field(..., min_length=1, max_length=255)
    bio: Optional[str] = None
    website: Optional[str] = None
    instagram: Optional[str] = None
    facebook: Optional[str] = None
    cover_image: Optional[str] = None
    verified: Optional[bool] = False

    model_config = ConfigDict(from_attributes=True)

    @validator("cover_image", pre=True, always=True)
    def default_cover_image(cls, v):
        return v or ""


class BusinessUpdate(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    bio: Optional[str] = None
    website: Optional[str] = None
    instagram: Optional[str] = None
    facebook: Optional[str] = None
    cover_image: Optional[str] = None
    verified: Optional[bool] = None

    model_config = ConfigDict(from_attributes=True)
