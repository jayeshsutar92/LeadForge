from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserBase(BaseModel):
    email: EmailStr
    name: str | None = None
    role: str = "user"


class UserCreate(UserBase):
    password: str = Field(min_length=6, max_length=128)
    name: str = Field(min_length=1, max_length=80)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(UserBase):
    id: str

    model_config = ConfigDict(from_attributes=True)


class AuthResponse(UserResponse):
    access_token: str
