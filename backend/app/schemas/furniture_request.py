from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

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
    product_id: int | None = None
    product_name: str
    color_name: str | None = None
    needs_measurements: bool
    dimensions: str | None = None
    client_name: str
    phone: str
    comment: str | None = None

class FurnitureRequestResponse(BaseModel):
    id: int
    product_id: int | None
    product_name: str
    color_name: str | None
    needs_measurements: bool
    dimensions: str | None
    client_name: str
    phone: str
    status: str
    assigned_manager_id: int | None
    assigned_manager_name: str | None = None
    comment: str | None
    created_at: datetime
    updated_at: datetime
    contacted_at: datetime | None
    completed_at: datetime | None

    class Config:
        from_attributes = True

class FurnitureRequestStatusUpdate(BaseModel):
    status: RequestStatus

class FurnitureRequestManagerUpdate(BaseModel):
    assigned_manager_id: int | None

class FurnitureRequestUpdate(BaseModel):
    product_id: int | None = None
    product_name: str | None = None
    color_name: str | None = None
    needs_measurements: bool | None = None
    dimensions: str | None = None
    client_name: str | None = None
    phone: str | None = None
    status: RequestStatus | None = None
    assigned_manager_id: int | None = None
    comment: str | None = None

class RequestEventResponse(BaseModel):
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

    class Config:
        from_attributes = True

class FurnitureRequestDetailResponse(FurnitureRequestResponse):
    assigned_manager: UserResponse | None = None
    product: ProductDetailResponse | None = None
    comments: list[FurnitureCommentResponse] = Field(default_factory=list)
    events: list[RequestEventResponse] = Field(default_factory=list)
