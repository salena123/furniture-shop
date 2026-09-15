from datetime import datetime

from pydantic import BaseModel


class MaterialCreate(BaseModel):
    name: str
    description: str | None = None


class MaterialUpdate(BaseModel):
    name: str | None = None
    description: str | None = None


class MaterialResponse(BaseModel):
    id: int
    name: str
    description: str | None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
