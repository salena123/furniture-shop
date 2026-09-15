from pydantic import BaseModel, ConfigDict, Field

class AttributeValueCreate(BaseModel):
    value: str
    sort_order: int = 0

class AttributeValueUpdate(BaseModel):
    value: str | None = None
    sort_order: int | None = None

class AttributeValueResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    attribute_id: int
    value: str
    sort_order: int

class AttributeCreate(BaseModel):
    name: str
    is_active: bool = True

class AttributeUpdate(BaseModel):
    name: str | None = None
    is_active: bool | None = None

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
