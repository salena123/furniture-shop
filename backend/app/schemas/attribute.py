from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.schemas.validators import normalize_required_text

class AttributeValueCreate(BaseModel):
    value: str
    sort_order: int = Field(default=0, ge=0)

    @field_validator("value", mode="before")
    @classmethod
    def validate_value_field(cls, value):
        return normalize_required_text(value, "value")

class AttributeValueUpdate(BaseModel):
    value: str | None = None
    sort_order: int | None = Field(default=None, ge=0)

    @field_validator("value", mode="before")
    @classmethod
    def validate_value_field(cls, value):
        if value is None:
            return value
        return normalize_required_text(value, "value")

class AttributeValueResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    attribute_id: int
    value: str
    sort_order: int

class AttributeCreate(BaseModel):
    name: str
    is_active: bool = True

    @field_validator("name", mode="before")
    @classmethod
    def validate_name_field(cls, value):
        return normalize_required_text(value, "name")

class AttributeUpdate(BaseModel):
    name: str | None = None
    is_active: bool | None = None

    @field_validator("name", mode="before")
    @classmethod
    def validate_name_field(cls, value):
        if value is None:
            return value
        return normalize_required_text(value, "name")

class AttributeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    is_active: bool

class AttributeDetailResponse(AttributeResponse):
    values: list[AttributeValueResponse] = Field(default_factory=list)

class AttributeListResponse(BaseModel):
    items: list[AttributeResponse] = Field(default_factory=list)
    total: int
    limit: int
    offset: int

class AttributeValueListResponse(BaseModel):
    items: list[AttributeValueResponse] = Field(default_factory=list)
    total: int
    limit: int
    offset: int
