from datetime import datetime
from typing import Literal

from pydantic import BaseModel

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

class RequestEventResponse(BaseModel):
    id: int
    request_id: int
    user_id: int
    event_type: str
    old_status: str | None
    new_status: str | None
    message: str | None
    created_at: datetime

    class Config:
        from_attributes = True
