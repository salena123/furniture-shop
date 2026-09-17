from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.schemas.validators import (
    normalize_optional_text,
    normalize_required_text,
    validate_slug,
)

class CategoryCreate(BaseModel):
    name: str
    description: str | None = None
    parent_id: int | None = Field(default=None, gt=0)
    slug: str
    image_url: str | None = None
    meta_title: str | None = None
    meta_description: str | None = None
    sort_order: int = Field(default=0, ge=0)
    is_active: bool  = True

    @field_validator("name", mode="before")
    @classmethod
    def validate_name_field(cls, value):
        return normalize_required_text(value, "name")

    @field_validator("slug", mode="before")
    @classmethod
    def validate_slug_field(cls, value):
        return validate_slug(value)

    @field_validator(
        "description",
        "image_url",
        "meta_title",
        "meta_description",
        mode="before",
    )
    @classmethod
    def normalize_optional_text_fields(cls, value):
        return normalize_optional_text(value)

class CategoryUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    parent_id: int | None = Field(default=None, gt=0)
    slug: str | None = None
    image_url: str | None = None
    meta_title: str | None = None
    meta_description: str | None = None
    sort_order: int | None = Field(default=None, ge=0)
    is_active: bool | None = None

    @field_validator("name", mode="before")
    @classmethod
    def validate_name_field(cls, value):
        if value is None:
            return value
        return normalize_required_text(value, "name")

    @field_validator("slug", mode="before")
    @classmethod
    def validate_slug_field(cls, value):
        if value is None:
            return value
        return validate_slug(value)

    @field_validator(
        "description",
        "image_url",
        "meta_title",
        "meta_description",
        mode="before",
    )
    @classmethod
    def normalize_optional_text_fields(cls, value):
        return normalize_optional_text(value)

class CategoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: str | None = None
    parent_id: int | None = None
    slug: str
    image_url: str | None = None
    meta_title: str | None = None
    meta_description: str | None = None
    sort_order: int
    is_active: bool

class CategoryListResponse(BaseModel):
    items: list[CategoryResponse] = Field(default_factory=list)
    total: int
    limit: int
    offset: int
