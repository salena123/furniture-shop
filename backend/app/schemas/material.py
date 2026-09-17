from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.schemas.validators import normalize_optional_text, normalize_required_text


class MaterialCreate(BaseModel):
    name: str
    description: str | None = None

    @field_validator("name", mode="before")
    @classmethod
    def validate_name_field(cls, value):
        return normalize_required_text(value, "name")

    @field_validator("description", mode="before")
    @classmethod
    def normalize_description_field(cls, value):
        return normalize_optional_text(value)


class MaterialUpdate(BaseModel):
    name: str | None = None
    description: str | None = None

    @field_validator("name", mode="before")
    @classmethod
    def validate_name_field(cls, value):
        if value is None:
            return value
        return normalize_required_text(value, "name")

    @field_validator("description", mode="before")
    @classmethod
    def normalize_description_field(cls, value):
        return normalize_optional_text(value)


class MaterialResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: str | None
    created_at: datetime
    updated_at: datetime


class MaterialListResponse(BaseModel):
    items: list[MaterialResponse] = Field(default_factory=list)
    total: int
    limit: int
    offset: int
