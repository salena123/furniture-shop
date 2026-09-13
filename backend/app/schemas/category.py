from pydantic import BaseModel

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

class CategoryResponse(BaseModel):
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

    class Config:
        from_attributes = True