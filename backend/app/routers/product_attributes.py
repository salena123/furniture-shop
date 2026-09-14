from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.product import Product
from app.models.attribute_value import AttributeValue
from app.models.product_attribute import ProductAttribute
from app.models.user import User
from app.security import require_admin


router = APIRouter(
    prefix="/api/products",
    tags=["Характеристики товаров"]
)


@router.post(
    "/{product_id}/attributes/{attribute_value_id}"
)
def add_attribute_to_product(
    product_id: int,
    attribute_value_id: int,
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

    attribute_value = db.query(AttributeValue).filter(
        AttributeValue.id == attribute_value_id
    ).first()

    if not attribute_value:
        raise HTTPException(
            status_code=404,
            detail="Значение атрибута не найдено"
        )

    existing = db.query(ProductAttribute).filter(
        ProductAttribute.product_id == product_id,
        ProductAttribute.attribute_value_id == attribute_value_id
    ).first()

    if existing:
        raise HTTPException(
            status_code=400,
            detail="Это значение атрибута уже добавлено товару"
        )

    new_product_attribute = ProductAttribute(
        product_id=product_id,
        attribute_value_id=attribute_value_id
    )

    db.add(new_product_attribute)
    db.commit()

    return {
        "message": "Атрибут успешно добавлен к товару",
        "product_id": product_id,
        "attribute_value_id": attribute_value_id
    }


@router.get(
    "/{product_id}/attributes"
)
def get_product_attributes(
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

    product_attributes = db.query(ProductAttribute).filter(
        ProductAttribute.product_id == product_id
    ).all()

    result = []

    for product_attribute in product_attributes:
        attribute_value = product_attribute.attribute_value

        result.append({
            "id": attribute_value.id,
            "attribute_id": attribute_value.attribute_id,
            "value": attribute_value.value,
            "sort_order": attribute_value.sort_order
        })

    return result


@router.delete(
    "/{product_id}/attributes/{attribute_value_id}"
)
def delete_attribute_from_product(
    product_id: int,
    attribute_value_id: int,
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

    product_attribute = db.query(ProductAttribute).filter(
        ProductAttribute.product_id == product_id,
        ProductAttribute.attribute_value_id == attribute_value_id
    ).first()

    if not product_attribute:
        raise HTTPException(
            status_code=404,
            detail="Это значение атрибута не добавлено товару"
        )

    db.delete(product_attribute)
    db.commit()

    return {
        "message": "Атрибут успешно удалён у товара",
        "product_id": product_id,
        "attribute_value_id": attribute_value_id
    }
