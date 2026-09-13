# from fastapi import APIRouter, Depends, HTTPException
# from sqlalchemy.orm import Session

# from app.database import get_db
# from app.models.product import Product
# from app.models.attribute_value import AttributeValue


# router = APIRouter(
#     prefix="/api/products",
#     tags=["Характеристики товаров"]
# )


# @router.post(
#     "/{product_id}/attributes/{attribute_value_id}"
# )
# def add_attribute_to_product(
#     product_id: int,
#     attribute_value_id: int,
#     db: Session = Depends(get_db)
# ):
#     product = db.query(Product).filter(
#         Product.id == product_id
#     ).first()

#     if not product:
#         raise HTTPException(
#             status_code=404,
#             detail="Товар не найден"
#         )

#     attribute_value = db.query(AttributeValue).filter(
#         AttributeValue.id == attribute_value_id
#     ).first()

#     if not attribute_value:
#         raise HTTPException(
#             status_code=404,
#             detail="Значение атрибута не найдено"
#         )

#     if attribute_value in product.attribute_values:
#         raise HTTPException(
#             status_code=400,
#             detail="Это значение атрибута уже добавлено товару"
#         )

#     product.attribute_values.append(attribute_value)

#     db.commit()

#     return {
#         "message": "Атрибут успешно добавлен к товару",
#         "product_id": product_id,
#         "attribute_value_id": attribute_value_id
#     }

# @router.get(
#     "/{product_id}/attributes"
# )
# def get_product_attributes(
#     product_id: int,
#     db: Session = Depends(get_db)
# ):
#     product = db.query(Product).filter(
#         Product.id == product_id
#     ).first()

#     if not product:
#         raise HTTPException(
#             status_code=404,
#             detail="Товар не найден"
#         )

#     result = []

#     for attribute_value in product.attribute_values:
#         result.append({
#             "id": attribute_value.id,
#             "attribute_id": attribute_value.attribute_id,
#             "value": attribute_value.value,
#             "sort_order": attribute_value.sort_order
#         })

#     return result


# @router.delete(
#     "/{product_id}/attributes/{attribute_value_id}"
# )
# def delete_attribute_from_product(
#     product_id: int,
#     attribute_value_id: int,
#     db: Session = Depends(get_db)
# ):
#     product = db.query(Product).filter(
#         Product.id == product_id
#     ).first()

#     if not product:
#         raise HTTPException(
#             status_code=404,
#             detail="Товар не найден"
#         )

#     attribute_value = db.query(AttributeValue).filter(
#         AttributeValue.id == attribute_value_id
#     ).first()

#     if not attribute_value:
#         raise HTTPException(
#             status_code=404,
#             detail="Значение атрибута не найдено"
#         )

#     if attribute_value not in product.attribute_values:
#         raise HTTPException(
#             status_code=404,
#             detail="Это значение атрибута не добавлено товару"
#         )

#     product.attribute_values.remove(attribute_value)

#     db.commit()

#     return {
#         "message": "Атрибут успешно удалён у товара",
#         "product_id": product_id,
#         "attribute_value_id": attribute_value_id
#     }