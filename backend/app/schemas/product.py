from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.schemas.validators import (
    normalize_optional_text,
    normalize_required_text,
    validate_slug,
)

class ProductCreate(BaseModel):
    product_name: str
    slug: str
    description: str | None = None
    short_description: str | None = None
    article: str | None = None
    category_id: int = Field(gt=0)
    material_id: int | None = Field(default=None, gt=0)
    price: str
    material: str | None = None
    is_custom: bool
    is_active: bool = True
    sort_order: int = Field(default=0, ge=0)
    dimensions: str | None = None
    color: str | None = None
    meta_title: str | None = None
    meta_description: str | None = None

    @field_validator("product_name", "price", mode="before")
    @classmethod
    def validate_required_text_fields(cls, value):
        return normalize_required_text(value)

    @field_validator("slug", mode="before")
    @classmethod
    def validate_slug_field(cls, value):
        return validate_slug(value)

    @field_validator(
        "description",
        "short_description",
        "article",
        "material",
        "dimensions",
        "color",
        "meta_title",
        "meta_description",
        mode="before",
    )
    @classmethod
    def normalize_optional_text_fields(cls, value):
        return normalize_optional_text(value)

class ProductUpdate(BaseModel):
    product_name: str | None = None
    slug: str | None = None
    description: str | None = None
    short_description: str | None = None
    article: str | None = None
    category_id: int | None = Field(default=None, gt=0)
    material_id: int | None = Field(default=None, gt=0)
    price: str | None = None
    material: str | None = None
    is_custom: bool | None = None
    is_active: bool | None = None
    sort_order: int | None = Field(default=None, ge=0)
    dimensions: str | None = None
    color: str | None = None
    meta_title: str | None = None
    meta_description: str | None = None

    @field_validator("product_name", "price", mode="before")
    @classmethod
    def validate_required_text_fields(cls, value):
        if value is None:
            return value
        return normalize_required_text(value)

    @field_validator("slug", mode="before")
    @classmethod
    def validate_slug_field(cls, value):
        if value is None:
            return value
        return validate_slug(value)

    @field_validator(
        "description",
        "short_description",
        "article",
        "material",
        "dimensions",
        "color",
        "meta_title",
        "meta_description",
        mode="before",
    )
    @classmethod
    def normalize_optional_text_fields(cls, value):
        return normalize_optional_text(value)

class ProductResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    product_name: str
    slug: str
    description: str | None
    short_description: str | None
    article: str | None
    category_id: int
    material_id: int | None = None
    material_name: str | None = None
    price: str
    material: str | None
    is_custom: bool
    is_active: bool
    sort_order: int
    dimensions: str | None
    color: str | None
    meta_title: str | None
    meta_description: str | None

class ProductImageCreate(BaseModel):
    image_url: str
    alt_text: str | None = None
    sort_order: int = Field(default=0, ge=0)
    is_main: bool = False

    @field_validator("image_url", mode="before")
    @classmethod
    def validate_image_url_field(cls, value):
        return normalize_required_text(value, "image_url")

    @field_validator("alt_text", mode="before")
    @classmethod
    def normalize_alt_text_field(cls, value):
        return normalize_optional_text(value)

class ProductImageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    product_id: int
    image_url: str
    alt_text: str | None
    sort_order: int = 0
    is_main: bool = False

class ProductAttributeValueResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    attribute_id: int
    attribute_name: str | None = None
    value: str
    sort_order: int

class ProductDetailResponse(ProductResponse):
    images: list[ProductImageResponse] = Field(default_factory=list)
    attributes: list[ProductAttributeValueResponse] = Field(default_factory=list)

class ProductListResponse(BaseModel):
    items: list[ProductDetailResponse] = Field(default_factory=list)
    total: int
    limit: int
    offset: int
