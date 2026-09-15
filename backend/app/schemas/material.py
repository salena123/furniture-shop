from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class MaterialCreate(BaseModel):
    name: str
    description: str | None = None


class MaterialUpdate(BaseModel):
    name: str | None = None
    description: str | None = None


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
