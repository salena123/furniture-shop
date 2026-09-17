import os
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, selectinload
from starlette.datastructures import UploadFile as StarletteUploadFile

from app.database import get_db
from app.models.attribute_value import AttributeValue
from app.models.category import Category
from app.models.material import Material
from app.models.product import Product
from app.models.product_attribute import ProductAttribute
from app.models.product_image import ProductImage
from app.models.user import User
from app.schemas.product import (
    ProductAttributeValueResponse,
    ProductCreate,
    ProductDetailResponse,
    ProductImageCreate,
    ProductImageResponse,
    ProductListResponse,
    ProductUpdate,
)
from app.security import get_optional_current_user, require_admin
from app.services.pagination import paginate_query
from app.services.serializers import (
    serialize_product,
    serialize_product_attribute,
    serialize_product_image,
)


router = APIRouter(
    prefix="/api/products",
    tags=["Товары"]
)

UPLOAD_ROOT = Path(__file__).resolve().parents[2] / "static" / "uploads" / "products"
UPLOAD_URL_PREFIX = "/static/uploads/products"
MAX_IMAGE_SIZE_BYTES = int(os.getenv("MAX_IMAGE_SIZE_BYTES", str(5 * 1024 * 1024)))
ALLOWED_IMAGE_TYPES = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
    "image/gif": ".gif",
}
NON_NULL_PRODUCT_FIELDS = {
    "product_name",
    "slug",
    "category_id",
    "price",
    "is_custom",
    "is_active",
    "sort_order",
}


def _product_query(db: Session):
    return db.query(Product).options(
        selectinload(Product.material_ref),
        selectinload(Product.images),
        selectinload(Product.product_attributes)
        .selectinload(ProductAttribute.attribute_value)
        .selectinload(AttributeValue.attribute),
    )


def _get_product_or_404(
    product_id: int,
    db: Session,
    include_inactive: bool = True,
) -> Product:
    query = _product_query(db).filter(
        Product.id == product_id
    )

    if not include_inactive:
        query = query.filter(
            Product.is_active == True
        )

    product = query.first()

    if not product:
        raise HTTPException(
            status_code=404,
            detail="Товар не найден"
        )

    return product


def _get_category_or_404(category_id: int, db: Session) -> Category:
    category = db.query(Category).filter(
        Category.id == category_id
    ).first()

    if not category:
        raise HTTPException(
            status_code=404,
            detail="Категория не найдена"
        )

    return category


def _get_material_or_404(material_id: int, db: Session) -> Material:
    material = db.query(Material).filter(
        Material.id == material_id
    ).first()

    if not material:
        raise HTTPException(
            status_code=404,
            detail="Материал не найден"
        )

    return material


def _ensure_product_slug_is_free(
    slug: str,
    db: Session,
    current_product_id: int | None = None,
) -> None:
    existing_product = db.query(Product).filter(
        Product.slug == slug
    ).first()

    if existing_product and existing_product.id != current_product_id:
        raise HTTPException(
            status_code=400,
            detail="Товар с таким slug уже существует"
        )


def _unset_main_images(
    product_id: int,
    db: Session,
    current_image_id: int | None = None,
) -> None:
    query = db.query(ProductImage).filter(
        ProductImage.product_id == product_id,
        ProductImage.is_main == True,
    )

    if current_image_id is not None:
        query = query.filter(
            ProductImage.id != current_image_id
        )

    query.update(
        {ProductImage.is_main: False},
        synchronize_session=False
    )


def _product_has_images(product_id: int, db: Session) -> bool:
    return db.query(ProductImage.id).filter(
        ProductImage.product_id == product_id
    ).first() is not None


def _ensure_product_has_main_image(
    product_id: int,
    db: Session,
    excluded_image_id: int | None = None,
) -> None:
    has_main = db.query(ProductImage.id).filter(
        ProductImage.product_id == product_id,
        ProductImage.is_main == True,
    ).first()

    if has_main:
        return

    query = db.query(ProductImage).filter(
        ProductImage.product_id == product_id,
    )

    if excluded_image_id is not None:
        query = query.filter(
            ProductImage.id != excluded_image_id
        )

    replacement = query.order_by(
        ProductImage.sort_order,
        ProductImage.id
    ).first()

    if replacement is None and excluded_image_id is not None:
        replacement = db.query(ProductImage).filter(
            ProductImage.product_id == product_id,
            ProductImage.id == excluded_image_id,
        ).first()

    if replacement:
        replacement.is_main = True


def _commit_product_changes(db: Session) -> None:
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail="Не удалось сохранить товар: проверьте уникальность slug и связи"
        )


def _parse_bool(value) -> bool:
    if isinstance(value, bool):
        return value

    if value is None:
        return False

    return str(value).lower() in {"1", "true", "yes", "on", "да"}


def _parse_int(value, default: int = 0) -> int:
    if value is None or value == "":
        return default

    try:
        parsed_value = int(value)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="sort_order должен быть числом"
        )

    if parsed_value < 0:
        raise HTTPException(
            status_code=400,
            detail="sort_order не может быть отрицательным"
        )

    return parsed_value


def _delete_uploaded_image_file(image_url: str) -> None:
    if not image_url.startswith(UPLOAD_URL_PREFIX):
        return

    relative_path = image_url.removeprefix(UPLOAD_URL_PREFIX).lstrip("/")
    file_path = UPLOAD_ROOT / relative_path

    try:
        file_path.relative_to(UPLOAD_ROOT)
    except ValueError:
        return

    if file_path.is_file():
        file_path.unlink()


@router.post(
    "/",
    response_model=ProductDetailResponse,
)
def create_product(
    product: ProductCreate,
    db: Session = Depends(get_db),
    _current_user: User = Depends(require_admin)
):
    _get_category_or_404(product.category_id, db)
    if product.material_id is not None:
        _get_material_or_404(product.material_id, db)
    _ensure_product_slug_is_free(product.slug, db)

    new_product = Product(
        product_name=product.product_name,
        slug=product.slug,
        description=product.description,
        short_description=product.short_description,
        article=product.article,
        category_id=product.category_id,
        material_id=product.material_id,
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
    _commit_product_changes(db)
    db.refresh(new_product)

    return serialize_product(new_product)


@router.get(
    "/",
    response_model=ProductListResponse,
)
def get_products(
    category_id: int | None = None,
    material_id: int | None = None,
    search: str | None = None,
    include_inactive: bool = False,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_optional_current_user),
):
    if include_inactive and (not current_user or current_user.role != "admin"):
        raise HTTPException(
            status_code=403,
            detail="Неактивные товары может смотреть только администратор"
        )

    query = _product_query(db)

    if not include_inactive:
        query = query.filter(
            Product.is_active == True
        )

    if category_id is not None:
        query = query.filter(
            Product.category_id == category_id
        )

    if material_id is not None:
        query = query.filter(
            Product.material_id == material_id
        )

    if search:
        search_filter = f"%{search}%"
        query = query.filter(
            or_(
                Product.product_name.ilike(search_filter),
                Product.description.ilike(search_filter),
                Product.short_description.ilike(search_filter),
                Product.article.ilike(search_filter),
                Product.material.ilike(search_filter),
                Product.material_ref.has(Material.name.ilike(search_filter)),
                Product.color.ilike(search_filter),
            )
        )

    query = query.order_by(
        Product.sort_order,
        Product.id
    )
    products, total = paginate_query(query, limit, offset)

    return {
        "items": [
            serialize_product(product)
            for product in products
        ],
        "total": total,
        "limit": limit,
        "offset": offset,
    }


@router.get(
    "/slug/{slug}",
    response_model=ProductDetailResponse
)
def get_product_by_slug(
    slug: str,
    include_inactive: bool = False,
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_optional_current_user),
):
    if include_inactive and (not current_user or current_user.role != "admin"):
        raise HTTPException(
            status_code=403,
            detail="Неактивные товары может смотреть только администратор"
        )

    query = _product_query(db).filter(
        Product.slug == slug
    )

    if not include_inactive:
        query = query.filter(
            Product.is_active == True
        )

    product = query.first()

    if not product:
        raise HTTPException(
            status_code=404,
            detail="Товар не найден"
        )

    return serialize_product(product)


@router.get(
    "/{product_id}",
    response_model=ProductDetailResponse
)
def get_product(
    product_id: int,
    include_inactive: bool = False,
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_optional_current_user),
):
    if include_inactive and (not current_user or current_user.role != "admin"):
        raise HTTPException(
            status_code=403,
            detail="Неактивные товары может смотреть только администратор"
        )

    product = _get_product_or_404(
        product_id,
        db,
        include_inactive=include_inactive
    )
    return serialize_product(product)


@router.put(
    "/{product_id}",
    response_model=ProductDetailResponse,
)
def update_product(
    product_id: int,
    product_data: ProductCreate,
    db: Session = Depends(get_db),
    _current_user: User = Depends(require_admin)
):
    product = _get_product_or_404(product_id, db)
    _get_category_or_404(product_data.category_id, db)
    if product_data.material_id is not None:
        _get_material_or_404(product_data.material_id, db)
    _ensure_product_slug_is_free(
        product_data.slug,
        db,
        current_product_id=product.id,
    )

    product.product_name = product_data.product_name
    product.slug = product_data.slug
    product.description = product_data.description
    product.short_description = product_data.short_description
    product.article = product_data.article
    product.category_id = product_data.category_id
    product.material_id = product_data.material_id
    product.price = product_data.price
    product.material = product_data.material
    product.is_custom = product_data.is_custom
    product.is_active = product_data.is_active
    product.sort_order = product_data.sort_order
    product.dimensions = product_data.dimensions
    product.color = product_data.color
    product.meta_title = product_data.meta_title
    product.meta_description = product_data.meta_description

    _commit_product_changes(db)
    db.refresh(product)

    return serialize_product(product)


@router.patch(
    "/{product_id}",
    response_model=ProductDetailResponse,
)
def patch_product(
    product_id: int,
    product_data: ProductUpdate,
    db: Session = Depends(get_db),
    _current_user: User = Depends(require_admin)
):
    product = _get_product_or_404(product_id, db)
    update_data = product_data.model_dump(exclude_unset=True)

    for field in NON_NULL_PRODUCT_FIELDS:
        if field in update_data and update_data[field] is None:
            raise HTTPException(
                status_code=400,
                detail=f"Поле {field} не может быть пустым"
            )

    if "category_id" in update_data:
        _get_category_or_404(update_data["category_id"], db)

    if "material_id" in update_data and update_data["material_id"] is not None:
        _get_material_or_404(update_data["material_id"], db)

    if "slug" in update_data:
        _ensure_product_slug_is_free(
            update_data["slug"],
            db,
            current_product_id=product.id,
        )

    for field, value in update_data.items():
        setattr(product, field, value)

    _commit_product_changes(db)
    db.refresh(product)

    return serialize_product(product)


@router.delete(
    "/{product_id}",
)
def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    _current_user: User = Depends(require_admin)
):
    product = _get_product_or_404(product_id, db)

    product.is_active = False
    product.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(product)

    return {
        "message": "Товар скрыт с сайта",
        "product_id": product.id,
        "is_active": product.is_active,
    }


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
    product = _get_product_or_404(product_id, db)

    is_main = image.is_main or not _product_has_images(product.id, db)
    if is_main:
        _unset_main_images(product.id, db)

    new_image = ProductImage(
        product_id=product.id,
        image_url=image.image_url,
        alt_text=image.alt_text,
        sort_order=image.sort_order,
        is_main=is_main,
    )

    db.add(new_image)
    db.commit()
    db.refresh(new_image)

    return serialize_product_image(new_image)


@router.post(
    "/{product_id}/images/upload",
    response_model=ProductImageResponse,
    openapi_extra={
        "requestBody": {
            "required": True,
            "content": {
                "multipart/form-data": {
                    "schema": {
                        "type": "object",
                        "required": ["file"],
                        "properties": {
                            "file": {
                                "type": "string",
                                "format": "binary",
                            },
                            "alt_text": {
                                "type": "string",
                            },
                            "sort_order": {
                                "type": "integer",
                                "default": 0,
                            },
                            "is_main": {
                                "type": "boolean",
                                "default": False,
                            },
                        },
                    }
                }
            },
        }
    }
)
async def upload_product_image(
    product_id: int,
    request: Request,
    db: Session = Depends(get_db),
    _current_user: User = Depends(require_admin)
):
    product = _get_product_or_404(product_id, db)

    try:
        form = await request.form()
    except (AssertionError, RuntimeError):
        raise HTTPException(
            status_code=500,
            detail="Для загрузки файлов установите пакет python-multipart"
        )

    upload = form.get("file")
    if not isinstance(upload, StarletteUploadFile):
        raise HTTPException(
            status_code=400,
            detail="Файл не передан"
        )

    if upload.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=400,
            detail="Можно загрузить только jpg, png, webp или gif"
        )

    is_main = _parse_bool(form.get("is_main"))
    sort_order = _parse_int(form.get("sort_order"), default=0)
    alt_text = form.get("alt_text")
    alt_text = alt_text.strip() if isinstance(alt_text, str) else alt_text
    alt_text = alt_text or None

    file_bytes = await upload.read()
    if not file_bytes:
        raise HTTPException(
            status_code=400,
            detail="Файл пустой"
        )

    if len(file_bytes) > MAX_IMAGE_SIZE_BYTES:
        max_size_mb = MAX_IMAGE_SIZE_BYTES // (1024 * 1024)
        raise HTTPException(
            status_code=400,
            detail=f"Размер файла не должен превышать {max_size_mb} МБ"
        )

    is_main = is_main or not _product_has_images(product.id, db)
    if is_main:
        _unset_main_images(product.id, db)

    extension = ALLOWED_IMAGE_TYPES[upload.content_type]
    file_name = f"{uuid4().hex}{extension}"
    upload_dir = UPLOAD_ROOT / str(product.id)
    upload_dir.mkdir(parents=True, exist_ok=True)
    file_path = upload_dir / file_name
    file_path.write_bytes(file_bytes)

    image_url = f"{UPLOAD_URL_PREFIX}/{product.id}/{file_name}"
    new_image = ProductImage(
        product_id=product.id,
        image_url=image_url,
        alt_text=alt_text,
        sort_order=sort_order,
        is_main=is_main,
    )

    db.add(new_image)
    db.commit()
    db.refresh(new_image)

    return serialize_product_image(new_image)


@router.get(
    "/{product_id}/images",
    response_model=list[ProductImageResponse]
)
def get_product_images(
    product_id: int,
    db: Session = Depends(get_db)
):
    product = _get_product_or_404(product_id, db, include_inactive=False)

    return [
        serialize_product_image(image)
        for image in sorted(
            product.images,
            key=lambda image: (image.sort_order, image.id),
        )
    ]


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

    return serialize_product_image(image)


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
        _unset_main_images(
            image.product_id,
            db,
            current_image_id=image.id,
        )

    image.image_url = image_data.image_url
    image.alt_text = image_data.alt_text
    image.sort_order = image_data.sort_order
    image.is_main = image_data.is_main
    if not image.is_main:
        _ensure_product_has_main_image(
            image.product_id,
            db,
            excluded_image_id=image.id
        )

    db.commit()
    db.refresh(image)

    return serialize_product_image(image)


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

    image_url = image.image_url
    image_was_main = image.is_main
    product_id = image.product_id
    db.delete(image)
    db.flush()
    if image_was_main:
        _ensure_product_has_main_image(
            product_id,
            db,
            excluded_image_id=image.id
        )
    db.commit()
    _delete_uploaded_image_file(image_url)

    return {"message": "Фотография успешно удалена"}


@router.get(
    "/{product_id}/attributes",
    response_model=list[ProductAttributeValueResponse]
)
def get_product_attributes(
    product_id: int,
    db: Session = Depends(get_db)
):
    product = _get_product_or_404(product_id, db, include_inactive=False)

    return [
        serialize_product_attribute(product_attribute)
        for product_attribute in sorted(
            product.product_attributes,
            key=lambda product_attribute: (
                product_attribute.attribute_value.sort_order,
                product_attribute.attribute_value.id,
            ),
        )
    ]
