from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, field_validator

from app.schemas.validators import (
    normalize_optional_text,
    normalize_required_text,
    validate_login,
    validate_password,
)

UserRole = Literal["admin", "manager"]

class UserCreate(BaseModel):
    login: str
    name: str
    email: str | None = None
    password: str
    role: UserRole = "manager"

    @field_validator("login", mode="before")
    @classmethod
    def validate_login_field(cls, value):
        return validate_login(value)

    @field_validator("name", mode="before")
    @classmethod
    def validate_name_field(cls, value):
        return normalize_required_text(value, "name")

    @field_validator("password", mode="before")
    @classmethod
    def validate_password_field(cls, value):
        return validate_password(value)

    @field_validator("email", mode="before")
    @classmethod
    def normalize_email_field(cls, value):
        return normalize_optional_text(value)

class UserUpdate(BaseModel):
    login: str | None = None
    name: str | None = None
    email: str | None = None
    password: str | None = None
    role: UserRole | None = None

    @field_validator("login", mode="before")
    @classmethod
    def validate_login_field(cls, value):
        if value is None:
            return value
        return validate_login(value)

    @field_validator("name", mode="before")
    @classmethod
    def validate_name_field(cls, value):
        if value is None:
            return value
        return normalize_required_text(value, "name")

    @field_validator("password", mode="before")
    @classmethod
    def validate_password_field(cls, value):
        if value is None:
            return value
        return validate_password(value)

    @field_validator("email", mode="before")
    @classmethod
    def normalize_email_field(cls, value):
        return normalize_optional_text(value)

class UserLogin(BaseModel):
    login: str
    password: str

    @field_validator("login", mode="before")
    @classmethod
    def validate_login_field(cls, value):
        return validate_login(value)

    @field_validator("password", mode="before")
    @classmethod
    def validate_password_field(cls, value):
        return normalize_required_text(value, "password")

class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    login: str
    name: str
    email: str | None  
    role: str
    last_login_at: datetime | None = None

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    expires_at: datetime
    user: UserResponse
