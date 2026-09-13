from pydantic import BaseModel

class AttributeValueCreate(BaseModel):
    attribute_id: int
    value: str
    sort_order: int = 0

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

class AttributeResponse(BaseModel):
    id: int
    name: str
    is_active: bool

    class Config:
        from_attributes = True