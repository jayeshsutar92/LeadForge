from pydantic import BaseModel, ConfigDict, EmailStr, Field, model_validator


class UserBase(BaseModel):
    email: EmailStr
    name: str | None = None
    full_name: str | None = None
    role: str = "user"


class UserCreate(UserBase):
    password: str = Field(min_length=6, max_length=128)
    name: str | None = Field(default=None, max_length=80)
    full_name: str | None = Field(default=None, max_length=80)

    @model_validator(mode="after")
    def validate_name_fields(self) -> "UserCreate":
        effective_name = self.name or self.full_name
        if not effective_name or not effective_name.strip():
            raise ValueError("Name is required")
        self.name = effective_name.strip()
        self.full_name = effective_name.strip()
        return self


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(UserBase):
    id: str

    model_config = ConfigDict(from_attributes=True)


class AuthResponse(UserResponse):
    access_token: str

