from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.attribute import Attribute
from app.models.attribute_value import AttributeValue
from app.models.user import User
from app.schemas.attribute import (
    AttributeCreate,
    AttributeResponse,
    AttributeValueCreate,
    AttributeValueResponse
)
from app.security import require_admin

router = APIRouter(
    prefix="/api/attributes",
    tags=["Атрибуты"]
)


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
    response_model=list[AttributeResponse]
)
def get_attributes(
    db: Session = Depends(get_db)
):
    attributes = db.query(Attribute).order_by(
        Attribute.id
    ).all()

    return attributes


@router.get(
    "/{attribute_id}",
    response_model=AttributeResponse
)
def get_attribute(
    attribute_id: int,
    db: Session = Depends(get_db)
):
    attribute = db.query(Attribute).filter(
        Attribute.id == attribute_id
    ).first()

    if not attribute:
        raise HTTPException(
            status_code=404,
            detail="Атрибут не найден"
        )

    return attribute


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
    attribute = db.query(Attribute).filter(
        Attribute.id == attribute_id
    ).first()

    if not attribute:
        raise HTTPException(
            status_code=404,
            detail="Атрибут не найден"
        )

    attribute.name = attribute_data.name
    attribute.is_active = attribute_data.is_active

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
    attribute = db.query(Attribute).filter(
        Attribute.id == attribute_id
    ).first()

    if not attribute:
        raise HTTPException(
            status_code=404,
            detail="Атрибут не найден"
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
    attribute = db.query(Attribute).filter(
        Attribute.id == attribute_id
    ).first()

    if not attribute:
        raise HTTPException(
            status_code=404,
            detail="Атрибут не найден"
        )

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
    response_model=list[AttributeValueResponse]
)
def get_attribute_values(
    attribute_id: int,
    db: Session = Depends(get_db)
):
    attribute = db.query(Attribute).filter(
        Attribute.id == attribute_id
    ).first()

    if not attribute:
        raise HTTPException(
            status_code=404,
            detail="Атрибут не найден"
        )

    values = db.query(AttributeValue).filter(
        AttributeValue.attribute_id == attribute_id
    ).order_by(
        AttributeValue.sort_order,
        AttributeValue.id
    ).all()

    return values


@router.get(
    "/values/{value_id}",
    response_model=AttributeValueResponse
)
def get_attribute_value(
    value_id: int,
    db: Session = Depends(get_db)
):
    value = db.query(AttributeValue).filter(
        AttributeValue.id == value_id
    ).first()

    if not value:
        raise HTTPException(
            status_code=404,
            detail="Значение атрибута не найдено"
        )

    return value


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
    value = db.query(AttributeValue).filter(
        AttributeValue.id == value_id
    ).first()

    if not value:
        raise HTTPException(
            status_code=404,
            detail="Значение атрибута не найдено"
        )

    value.value = value_data.value
    value.sort_order = value_data.sort_order

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
    value = db.query(AttributeValue).filter(
        AttributeValue.id == value_id
    ).first()

    if not value:
        raise HTTPException(
            status_code=404,
            detail="Значение атрибута не найдено"
        )

    db.delete(value)
    db.commit()

    return {
        "message": "Значение атрибута успешно удалено"
    }
