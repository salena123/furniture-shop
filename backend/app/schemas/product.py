from pydantic import BaseModel

class ProductCreate(BaseModel):
    product_name: str
    slug: str
    description: str | None = None
    short_description: str | None = None
    article: str | None = None
    category_id: int
    price: str
    material: str | None = None
    is_custom: bool
    is_active: bool = True
    sort_order: int = 0
    dimensions: str | None = None
    color: str | None = None
    meta_title: str | None = None
    meta_description: str | None = None

class ProductResponse(BaseModel):
    id: int
    product_name: str
    slug: str
    description: str | None
    short_description: str | None
    article: str | None
    category_id: int
    price: str
    material: str | None
    is_custom: bool
    is_active: bool
    sort_order: int
    dimensions: str | None
    color: str | None
    meta_title: str | None
    meta_description: str | None

    class Config:
        from_attributes = True