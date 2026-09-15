from pydantic import BaseModel, Field

from app.schemas.attribute import AttributeDetailResponse
from app.schemas.category import CategoryResponse
from app.schemas.material import MaterialResponse


class CatalogOptionsResponse(BaseModel):
    categories: list[CategoryResponse] = Field(default_factory=list)
    materials: list[MaterialResponse] = Field(default_factory=list)
    attributes: list[AttributeDetailResponse] = Field(default_factory=list)


class RequestStatusOption(BaseModel):
    value: str
    label: str
