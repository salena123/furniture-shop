from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.schemas.validators import (
    normalize_optional_text,
    normalize_required_text,
    validate_phone,
    validate_true,
)

from app.schemas.furniture_comment import FurnitureCommentResponse
from app.schemas.product import ProductDetailResponse
from app.schemas.user import UserResponse

RequestStatus = Literal[
    "new",
    "in_progress",
    "contacted",
    "measurement_scheduled",
    "quote_prepared",
    "completed",
    "cancelled",
]

class FurnitureRequestCreate(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "product_id": 1,
                "material_id": 2,
                "needs_measurements": True,
                "dimensions": "3200 мм",
                "client_name": "Анна",
                "phone": "+7 900 100-20-30",
                "city": "Екатеринбург",
                "preferred_contact_time": "после 14:00",
                "personal_data_consent": True,
                "comment": "Перезвонить после обеда",
            }
        }
    )

    product_id: int | None = Field(default=None, gt=0)
    material_id: int | None = Field(default=None, gt=0)
    product_name: str | None = None
    color_name: str | None = None
    needs_measurements: bool
    dimensions: str | None = None
    client_name: str
    phone: str
    city: str | None = None
    preferred_contact_time: str | None = None
    personal_data_consent: bool
    comment: str | None = None

    @field_validator("client_name", mode="before")
    @classmethod
    def validate_required_text_fields(cls, value):
        return normalize_required_text(value)

    @field_validator("product_name", mode="before")
    @classmethod
    def normalize_product_name_field(cls, value):
        return normalize_optional_text(value)

    @field_validator("phone", mode="before")
    @classmethod
    def validate_phone_field(cls, value):
        return validate_phone(value)

    @field_validator(
        "color_name",
        "dimensions",
        "city",
        "preferred_contact_time",
        "comment",
        mode="before",
    )
    @classmethod
    def normalize_optional_text_fields(cls, value):
        return normalize_optional_text(value)

    @field_validator("personal_data_consent")
    @classmethod
    def validate_personal_data_consent_field(cls, value):
        return validate_true(value, "personal_data_consent")

    @model_validator(mode="after")
    def validate_product_reference(self):
        if self.product_id is None and self.product_name is None:
            raise ValueError("Нужно выбрать товар или указать название товара")

        return self

class FurnitureRequestResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    product_id: int | None
    product_slug: str | None = None
    category_id: int | None = None
    category_name: str | None = None
    material_id: int | None = None
    material_name: str | None = None
    product_name: str
    color_name: str | None
    needs_measurements: bool
    dimensions: str | None
    client_name: str
    phone: str
    city: str | None = None
    preferred_contact_time: str | None = None
    personal_data_consent: bool
    status: str
    assigned_manager_id: int | None
    assigned_manager_name: str | None = None
    comment: str | None
    created_at: datetime
    updated_at: datetime
    contacted_at: datetime | None
    completed_at: datetime | None
    comments_count: int = 0
    events_count: int = 0

class FurnitureRequestStatusUpdate(BaseModel):
    status: RequestStatus

class FurnitureRequestManagerUpdate(BaseModel):
    assigned_manager_id: int | None = Field(default=None, gt=0)

class FurnitureRequestUpdate(BaseModel):
    product_id: int | None = Field(default=None, gt=0)
    material_id: int | None = Field(default=None, gt=0)
    product_name: str | None = None
    color_name: str | None = None
    needs_measurements: bool | None = None
    dimensions: str | None = None
    client_name: str | None = None
    phone: str | None = None
    city: str | None = None
    preferred_contact_time: str | None = None
    personal_data_consent: bool | None = None
    status: RequestStatus | None = None
    assigned_manager_id: int | None = Field(default=None, gt=0)
    comment: str | None = None

    @field_validator("product_name", "client_name", "phone", mode="before")
    @classmethod
    def validate_required_text_fields(cls, value):
        if value is None:
            return value
        return normalize_required_text(value)

    @field_validator("phone", mode="after")
    @classmethod
    def validate_phone_field(cls, value):
        if value is None:
            return value
        return validate_phone(value)

    @field_validator(
        "color_name",
        "dimensions",
        "city",
        "preferred_contact_time",
        "comment",
        mode="before",
    )
    @classmethod
    def normalize_optional_text_fields(cls, value):
        return normalize_optional_text(value)

    @field_validator("personal_data_consent")
    @classmethod
    def validate_personal_data_consent_field(cls, value):
        if value is None:
            return value
        return validate_true(value, "personal_data_consent")

class RequestEventResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    request_id: int
    user_id: int
    user_name: str | None = None
    user_role: str | None = None
    event_type: str
    old_status: str | None
    new_status: str | None
    message: str | None
    created_at: datetime

class FurnitureRequestDetailResponse(FurnitureRequestResponse):
    assigned_manager: UserResponse | None = None
    product: ProductDetailResponse | None = None
    comments: list[FurnitureCommentResponse] = Field(default_factory=list)
    events: list[RequestEventResponse] = Field(default_factory=list)

class FurnitureRequestListResponse(BaseModel):
    items: list[FurnitureRequestResponse] = Field(default_factory=list)
    total: int
    limit: int
    offset: int
