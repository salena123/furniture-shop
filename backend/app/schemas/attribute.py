from pydantic import BaseModel, Field

class AttributeValueCreate(BaseModel):
    value: str
    sort_order: int = 0

class AttributeValueUpdate(BaseModel):
    value: str | None = None
    sort_order: int | None = None

class AttributeValueResponse(BaseModel):
    id: int
    attribute_id: int
    value: str
    sort_order: int

    class Config:
        from_attributes = True

class AttributeCreate(BaseModel):
    name: str
    is_active: bool = True

class AttributeUpdate(BaseModel):
    name: str | None = None
    is_active: bool | None = None

class AttributeResponse(BaseModel):
    id: int
    name: str
    is_active: bool

    class Config:
        from_attributes = True

class AttributeDetailResponse(AttributeResponse):
    values: list[AttributeValueResponse] = Field(default_factory=list)
