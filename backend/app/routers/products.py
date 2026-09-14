from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.product import Product
from app.models.user import User
from app.schemas.product import ProductCreate, ProductResponse
from app.models.product_image import ProductImage
from app.schemas.product import ProductImageCreate, ProductImageResponse
from app.security import require_admin


router = APIRouter(
    prefix="/api/products",
    tags=["Товары"]
)

@router.post(
    "/",
    response_model=ProductResponse,
)
def create_product(
        product: ProductCreate,
        db: Session = Depends(get_db),
        _current_user: User = Depends(require_admin)
):
    new_product = Product(
        product_name=product.product_name,
        slug=product.slug,
        description=product.description,
        short_description=product.short_description,
        article=product.article,
        category_id=product.category_id,
        price=product.price,
        material=product.material,
        is_custom=product.is_custom,
        is_active=product.is_active,
        sort_order=product.sort_order,
        dimensions=product.dimensions,
        color=product.color,
        meta_title=product.meta_title,
        meta_description=product.meta_description
    )

    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    return new_product

@router.get(
    "/",
    response_model=list[ProductResponse],
)
def get_products(
        db: Session = Depends(get_db)
    ):
    products = db.query(Product).order_by(
        Product.sort_order,
        Product.id
        ).all()
    return products

@router.get(
    "/{product_id}",
    response_model=ProductResponse
)
def get_product(
    product_id: int,
    db: Session = Depends(get_db)
):
    product = db.query(Product).filter(
        Product.id == product_id
    ).first()
    if not product:
        raise HTTPException(
            status_code=404,
            detail="Товар не найден"
        )
    return product

@router.put(
    "/{product_id}",
    response_model=ProductResponse,
)
def update_product(
    product_id: int,
    product_data: ProductCreate,
    db: Session = Depends(get_db),
    _current_user: User = Depends(require_admin)
):
    product = db.query(Product).filter(
        Product.id == product_id
    ).first()
    if not product:
        raise HTTPException(
            status_code=404,
            detail="Товар не найден"
        )

    product.product_name = product_data.product_name
    product.slug = product_data.slug
    product.description = product_data.description
    product.short_description = product_data.short_description
    product.article = product_data.article
    product.category_id = product_data.category_id
    product.price = product_data.price
    product.material = product_data.material
    product.is_custom = product_data.is_custom
    product.is_active = product_data.is_active
    product.sort_order = product_data.sort_order
    product.dimensions = product_data.dimensions
    product.color = product_data.color
    product.meta_title = product_data.meta_title
    product.meta_description = product_data.meta_description

    db.commit()
    db.refresh(product)
    return product

@router.delete(
    "/{product_id}",
)
def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    _current_user: User = Depends(require_admin)
):
    product = db.query(Product).filter(
        Product.id == product_id
    ).first()
    if not product:
        raise HTTPException(
            status_code=404,
            detail= "Товар не найден"
        )

    db.delete(product)
    db.commit()
    return { "message" : "Товар успешно удалён"}

@router.post(
    "/{product_id}/images",
    response_model=ProductImageResponse
)
def add_product_image_to_product(
    product_id: int,
    image: ProductImageCreate,
    db: Session = Depends(get_db),
    _current_user: User = Depends(require_admin)
):
    product = db.query(Product).filter(
        Product.id == product_id
    ).first()

    if not product:
        raise HTTPException(
            status_code=404,
            detail= "Товар не найден"
        )

    if image.is_main:
        main_image = db.query(ProductImage).filter(
            ProductImage.product_id == product_id,
            ProductImage.is_main == True
        ).first()

        if main_image:
            raise HTTPException(
                status_code=400,
                detail="У товара уже есть главная фотография"
            )
    
    new_image = ProductImage(
        product_id=product.id,
        image_url=image.image_url,
        alt_text=image.alt_text,
        sort_order=image.sort_order,
        is_main=image.is_main,
    )

    db.add(new_image)
    db.commit()
    db.refresh(new_image)
    return new_image

@router.get(
    "/{product_id}/images",
    response_model=list[ProductImageResponse]
)
def get_product_images(
    product_id: int,
    db: Session = Depends(get_db)
):
    product = db.query(Product).filter(
        Product.id == product_id
    ).first()

    if not product:
        raise HTTPException(
            status_code=404,
            detail="Товар не найден"
        )

    images = product.images
    return images


@router.get(
    "/images/{image_id}",
    response_model=ProductImageResponse
)
def get_product_image(
    image_id: int,
    db: Session = Depends(get_db)
):
    image = db.query(ProductImage).filter(
        ProductImage.id == image_id
    ).first()

    if not image:
        raise HTTPException(
            status_code=404,
            detail="Фотография не найдена"
        )

    return image

@router.put(
    "/images/{image_id}",
    response_model=ProductImageResponse
)
def update_info_product_image(
    image_id: int,
    image_data: ProductImageCreate,
    db: Session = Depends(get_db),
    _current_user: User = Depends(require_admin)
):
    image = db.query(ProductImage).filter(
        ProductImage.id == image_id
    ).first()

    if not image:
        raise HTTPException(
            status_code=404,
            detail="Фотография не найдена"
        )

    if image_data.is_main:
        main_image = db.query(ProductImage).filter(
            ProductImage.product_id == image.product_id,
            ProductImage.is_main == True,
            ProductImage.id != image_id
        ).first()

        if main_image:
            raise HTTPException(
                status_code=400,
                detail="У товара уже есть главаная фотография"
            )

    image.image_url = image_data.image_url
    image.alt_text = image_data.alt_text
    image.sort_order = image_data.sort_order
    image.is_main = image_data.is_main

    db.commit()
    db.refresh(image)
    return image

@router.delete(
    "/images/{image_id}",
)
def delete_image(
    image_id: int,
    db: Session = Depends(get_db),
    _current_user: User = Depends(require_admin)
):
    image = db.query(ProductImage).filter(
        ProductImage.id == image_id
    ).first()

    if not image:
        raise HTTPException(
            status_code=404,
            detail="Фотография не найдена"
        )

    db.delete(image)
    db.commit()
    return { "message" : "Фотография успешно удалена"}
