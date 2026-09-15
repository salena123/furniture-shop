from pydantic import BaseModel, Field

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

class ProductUpdate(BaseModel):
    product_name: str | None = None
    slug: str | None = None
    description: str | None = None
    short_description: str | None = None
    article: str | None = None
    category_id: int | None = None
    price: str | None = None
    material: str | None = None
    is_custom: bool | None = None
    is_active: bool | None = None
    sort_order: int | None = None
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

class ProductImageCreate(BaseModel):
    image_url: str
    alt_text: str | None = None
    sort_order: int = 0
    is_main: bool = False

class ProductImageResponse(BaseModel):
    id: int
    product_id: int
    image_url: str
    alt_text: str | None
    sort_order: int = 0
    is_main: bool = False

    class Config:
        from_attributes = True

class ProductAttributeValueResponse(BaseModel):
    id: int
    attribute_id: int
    attribute_name: str | None = None
    value: str
    sort_order: int

    class Config:
        from_attributes = True

class ProductDetailResponse(ProductResponse):
    images: list[ProductImageResponse] = Field(default_factory=list)
    attributes: list[ProductAttributeValueResponse] = Field(default_factory=list)
