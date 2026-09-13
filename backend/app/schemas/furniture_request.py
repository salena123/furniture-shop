from datetime import datetime

from pydantic import BaseModel

class FurnitureRequestCreate(BaseModel):
    product_id: int | None = None
    product_name: str
    color_name: str | None = None
    needs_measurements: bool
    dimensions: str | None = None
    client_name: str
    phone: str

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
    status: str

class FurnitureRequestManagerUpdate(BaseModel):
    assigned_manager_id: int | None