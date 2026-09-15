from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.furniture_request import FurnitureRequest
from app.models.material import Material
from app.models.product import Product
from app.models.user import User
from app.schemas.material import (
    MaterialCreate,
    MaterialListResponse,
    MaterialResponse,
    MaterialUpdate,
)
from app.security import require_admin
from app.services.pagination import paginate_query


router = APIRouter(
    prefix="/api/materials",
    tags=["Материалы"]
)


def _get_material_or_404(
    material_id: int,
    db: Session,
) -> Material:
    material = db.query(Material).filter(
        Material.id == material_id
    ).first()

    if not material:
        raise HTTPException(
            status_code=404,
            detail="Материал не найден"
        )

    return material


def _ensure_material_name_is_free(
    name: str,
    db: Session,
    current_material_id: int | None = None
) -> None:
    existing_material = db.query(Material).filter(
        Material.name == name
    ).first()

    if existing_material and existing_material.id != current_material_id:
        raise HTTPException(
            status_code=400,
            detail="Материал с таким названием уже существует"
        )


def _commit_material_changes(db: Session) -> None:
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail="Не удалось сохранить материал"
        )


@router.post(
    "/",
    response_model=MaterialResponse
)
def create_material(
    material_data: MaterialCreate,
    db: Session = Depends(get_db),
    _current_user: User = Depends(require_admin)
):
    _ensure_material_name_is_free(material_data.name, db)

    material = Material(
        name=material_data.name,
        description=material_data.description
    )

    db.add(material)
    _commit_material_changes(db)
    db.refresh(material)

    return material


@router.get(
    "/",
    response_model=MaterialListResponse
)
def get_materials(
    search: str | None = None,
    limit: int = Query(100, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    query = db.query(Material)

    if search:
        query = query.filter(
            Material.name.ilike(f"%{search}%")
        )

    query = query.order_by(
        Material.name,
        Material.id
    )
    materials, total = paginate_query(query, limit, offset)

    return {
        "items": materials,
        "total": total,
        "limit": limit,
        "offset": offset,
    }


@router.get(
    "/{material_id}",
    response_model=MaterialResponse
)
def get_material(
    material_id: int,
    db: Session = Depends(get_db),
):
    return _get_material_or_404(material_id, db)


@router.put(
    "/{material_id}",
    response_model=MaterialResponse
)
def update_material(
    material_id: int,
    material_data: MaterialCreate,
    db: Session = Depends(get_db),
    _current_user: User = Depends(require_admin)
):
    material = _get_material_or_404(material_id, db)
    _ensure_material_name_is_free(
        material_data.name,
        db,
        current_material_id=material.id
    )

    material.name = material_data.name
    material.description = material_data.description
    material.updated_at = datetime.now(timezone.utc)

    _commit_material_changes(db)
    db.refresh(material)

    return material


@router.patch(
    "/{material_id}",
    response_model=MaterialResponse
)
def patch_material(
    material_id: int,
    material_data: MaterialUpdate,
    db: Session = Depends(get_db),
    _current_user: User = Depends(require_admin)
):
    material = _get_material_or_404(material_id, db)
    update_data = material_data.model_dump(exclude_unset=True)

    if "name" in update_data and update_data["name"] is None:
        raise HTTPException(
            status_code=400,
            detail="Поле name не может быть пустым"
        )

    if "name" in update_data:
        _ensure_material_name_is_free(
            update_data["name"],
            db,
            current_material_id=material.id
        )

    for field, value in update_data.items():
        setattr(material, field, value)

    if update_data:
        material.updated_at = datetime.now(timezone.utc)

    _commit_material_changes(db)
    db.refresh(material)

    return material


@router.delete(
    "/{material_id}"
)
def delete_material(
    material_id: int,
    db: Session = Depends(get_db),
    _current_user: User = Depends(require_admin)
):
    material = _get_material_or_404(material_id, db)

    db.query(Product).filter(
        Product.material_id == material.id
    ).update(
        {Product.material_id: None},
        synchronize_session=False
    )
    db.query(FurnitureRequest).filter(
        FurnitureRequest.material_id == material.id
    ).update(
        {FurnitureRequest.material_id: None},
        synchronize_session=False
    )

    db.delete(material)
    db.commit()

    return {
        "message": "Материал успешно удалён"
    }
