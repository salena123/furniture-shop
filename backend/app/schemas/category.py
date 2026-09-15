from pydantic import BaseModel, ConfigDict, Field

class CategoryCreate(BaseModel):
    name: str
    description: str | None = None
    parent_id: int | None = None
    slug: str
    image_url: str | None = None
    meta_title: str | None = None
    meta_description: str | None = None
    sort_order: int  = 0
    is_active: bool  = True

class CategoryUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    parent_id: int | None = None
    slug: str | None = None
    image_url: str | None = None
    meta_title: str | None = None
    meta_description: str | None = None
    sort_order: int | None = None
    is_active: bool | None = None

class CategoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: str | None = None
    parent_id: int | None = None
    slug: str
    image_url: str | None = None
    meta_title: str | None = None
    meta_description: str | None = None
    sort_order: int
    is_active: bool

class CategoryListResponse(BaseModel):
    items: list[CategoryResponse] = Field(default_factory=list)
    total: int
    limit: int
    offset: int
