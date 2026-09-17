from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.attribute import Attribute
from app.models.attribute_value import AttributeValue
from app.models.product_attribute import ProductAttribute
from app.models.user import User
from app.schemas.attribute import (
    AttributeCreate,
    AttributeDetailResponse,
    AttributeListResponse,
    AttributeResponse,
    AttributeUpdate,
    AttributeValueCreate,
    AttributeValueListResponse,
    AttributeValueResponse,
    AttributeValueUpdate
)
from app.security import get_optional_current_user, require_admin
from app.services.pagination import paginate_query

router = APIRouter(
    prefix="/api/attributes",
    tags=["Атрибуты"]
)


def _get_attribute_or_404(
    attribute_id: int,
    db: Session,
    include_inactive: bool = True
) -> Attribute:
    query = db.query(Attribute).filter(
        Attribute.id == attribute_id
    )

    if not include_inactive:
        query = query.filter(
            Attribute.is_active == True
        )

    attribute = query.first()

    if not attribute:
        raise HTTPException(
            status_code=404,
            detail="Атрибут не найден"
        )

    return attribute


def _get_attribute_value_or_404(value_id: int, db: Session) -> AttributeValue:
    value = db.query(AttributeValue).filter(
        AttributeValue.id == value_id
    ).first()

    if not value:
        raise HTTPException(
            status_code=404,
            detail="Значение атрибута не найдено"
        )

    return value


@router.post(
    "/",
    response_model=AttributeResponse
)
def create_attribute(
    attribute: AttributeCreate,
    db: Session = Depends(get_db),
    _current_user: User = Depends(require_admin)
):
    new_attribute = Attribute(
        name=attribute.name,
        is_active=attribute.is_active
    )

    db.add(new_attribute)
    db.commit()
    db.refresh(new_attribute)

    return new_attribute


@router.get(
    "/",
    response_model=AttributeListResponse
)
def get_attributes(
    include_inactive: bool = False,
    limit: int = Query(100, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_optional_current_user)
):
    if include_inactive and (not current_user or current_user.role != "admin"):
        raise HTTPException(
            status_code=403,
            detail="Неактивные атрибуты может смотреть только администратор"
        )

    query = db.query(Attribute)

    if not include_inactive:
        query = query.filter(
            Attribute.is_active == True
        )

    query = query.order_by(
        Attribute.id
    )
    attributes, total = paginate_query(query, limit, offset)

    return {
        "items": attributes,
        "total": total,
        "limit": limit,
        "offset": offset,
    }


@router.get(
    "/{attribute_id}/details",
    response_model=AttributeDetailResponse
)
def get_attribute_details(
    attribute_id: int,
    include_inactive: bool = False,
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_optional_current_user)
):
    if include_inactive and (not current_user or current_user.role != "admin"):
        raise HTTPException(
            status_code=403,
            detail="Неактивные атрибуты может смотреть только администратор"
        )

    return _get_attribute_or_404(
        attribute_id,
        db,
        include_inactive=include_inactive
    )


@router.get(
    "/{attribute_id}",
    response_model=AttributeResponse
)
def get_attribute(
    attribute_id: int,
    include_inactive: bool = False,
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_optional_current_user)
):
    if include_inactive and (not current_user or current_user.role != "admin"):
        raise HTTPException(
            status_code=403,
            detail="Неактивные атрибуты может смотреть только администратор"
        )

    return _get_attribute_or_404(
        attribute_id,
        db,
        include_inactive=include_inactive
    )


@router.put(
    "/{attribute_id}",
    response_model=AttributeResponse
)
def update_attribute(
    attribute_id: int,
    attribute_data: AttributeCreate,
    db: Session = Depends(get_db),
    _current_user: User = Depends(require_admin)
):
    attribute = _get_attribute_or_404(attribute_id, db)

    attribute.name = attribute_data.name
    attribute.is_active = attribute_data.is_active

    db.commit()
    db.refresh(attribute)

    return attribute


@router.patch(
    "/{attribute_id}",
    response_model=AttributeResponse
)
def patch_attribute(
    attribute_id: int,
    attribute_data: AttributeUpdate,
    db: Session = Depends(get_db),
    _current_user: User = Depends(require_admin)
):
    attribute = _get_attribute_or_404(attribute_id, db)
    update_data = attribute_data.model_dump(exclude_unset=True)

    for field in {"name", "is_active"}:
        if field in update_data and update_data[field] is None:
            raise HTTPException(
                status_code=400,
                detail=f"Поле {field} не может быть пустым"
            )

    for field, value in update_data.items():
        setattr(attribute, field, value)

    db.commit()
    db.refresh(attribute)

    return attribute


@router.delete(
    "/{attribute_id}"
)
def delete_attribute(
    attribute_id: int,
    db: Session = Depends(get_db),
    _current_user: User = Depends(require_admin)
):
    attribute = _get_attribute_or_404(attribute_id, db)
    used_values_count = db.query(ProductAttribute).join(AttributeValue).filter(
        AttributeValue.attribute_id == attribute.id
    ).count()

    if used_values_count:
        raise HTTPException(
            status_code=400,
            detail=(
                "Атрибут нельзя удалить: "
                f"его значения используются у товаров ({used_values_count})"
            )
        )

    db.delete(attribute)
    db.commit()

    return {
        "message": "Атрибут успешно удалён"
    }


@router.post(
    "/{attribute_id}/values",
    response_model=AttributeValueResponse
)
def create_attribute_value(
    attribute_id: int,
    value: AttributeValueCreate,
    db: Session = Depends(get_db),
    _current_user: User = Depends(require_admin)
):
    _get_attribute_or_404(attribute_id, db)

    new_value = AttributeValue(
        attribute_id=attribute_id,
        value=value.value,
        sort_order=value.sort_order
    )

    db.add(new_value)
    db.commit()
    db.refresh(new_value)

    return new_value


@router.get(
    "/{attribute_id}/values",
    response_model=AttributeValueListResponse
)
def get_attribute_values(
    attribute_id: int,
    limit: int = Query(100, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    _get_attribute_or_404(attribute_id, db, include_inactive=False)

    query = db.query(AttributeValue).filter(
        AttributeValue.attribute_id == attribute_id
    ).order_by(
        AttributeValue.sort_order,
        AttributeValue.id
    )
    values, total = paginate_query(query, limit, offset)

    return {
        "items": values,
        "total": total,
        "limit": limit,
        "offset": offset,
    }


@router.get(
    "/values/{value_id}",
    response_model=AttributeValueResponse
)
def get_attribute_value(
    value_id: int,
    db: Session = Depends(get_db)
):
    return _get_attribute_value_or_404(value_id, db)


@router.put(
    "/values/{value_id}",
    response_model=AttributeValueResponse
)
def update_attribute_value(
    value_id: int,
    value_data: AttributeValueCreate,
    db: Session = Depends(get_db),
    _current_user: User = Depends(require_admin)
):
    value = _get_attribute_value_or_404(value_id, db)

    value.value = value_data.value
    value.sort_order = value_data.sort_order

    db.commit()
    db.refresh(value)

    return value


@router.patch(
    "/values/{value_id}",
    response_model=AttributeValueResponse
)
def patch_attribute_value(
    value_id: int,
    value_data: AttributeValueUpdate,
    db: Session = Depends(get_db),
    _current_user: User = Depends(require_admin)
):
    value = _get_attribute_value_or_404(value_id, db)
    update_data = value_data.model_dump(exclude_unset=True)

    for field in {"value", "sort_order"}:
        if field in update_data and update_data[field] is None:
            raise HTTPException(
                status_code=400,
                detail=f"Поле {field} не может быть пустым"
            )

    for field, field_value in update_data.items():
        setattr(value, field, field_value)

    db.commit()
    db.refresh(value)

    return value


@router.delete(
    "/values/{value_id}"
)
def delete_attribute_value(
    value_id: int,
    db: Session = Depends(get_db),
    _current_user: User = Depends(require_admin)
):
    value = _get_attribute_value_or_404(value_id, db)
    products_count = db.query(ProductAttribute).filter(
        ProductAttribute.attribute_value_id == value.id
    ).count()

    if products_count:
        raise HTTPException(
            status_code=400,
            detail=(
                "Значение атрибута нельзя удалить: "
                f"оно используется у товаров ({products_count})"
            )
        )

    db.delete(value)
    db.commit()

    return {
        "message": "Значение атрибута успешно удалено"
    }
