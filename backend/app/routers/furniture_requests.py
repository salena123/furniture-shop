from datetime import datetime, timezone

from fastapi import Depends, APIRouter, HTTPException, Query
from sqlalchemy import or_
from sqlalchemy.orm import Session, selectinload

from app.database import get_db
from app.models.attribute_value import AttributeValue
from app.models.furniture_comment import FurnitureComment
from app.models.furniture_request import FurnitureRequest
from app.models.material import Material
from app.models.product import Product
from app.models.product_attribute import ProductAttribute
from app.models.request_event import RequestEvent
from app.models.user import User
from app.schemas.furniture_request import (
    FurnitureRequestCreate,
    FurnitureRequestDetailResponse,
    FurnitureRequestListResponse,
    FurnitureRequestManagerUpdate,
    FurnitureRequestResponse,
    FurnitureRequestStatusUpdate,
    FurnitureRequestUpdate,
    RequestEventResponse,
    RequestStatus,
)
from app.schemas.catalog import RequestStatusOption
from app.security import require_admin, require_manager_or_admin
from app.services.pagination import paginate_query
from app.services.serializers import (
    serialize_request,
    serialize_request_detail,
    serialize_request_event,
)


router = APIRouter(
    prefix="/api/requests",
    tags=["Заявки"]
)

REQUEST_STATUS_OPTIONS = [
    {"value": "new", "label": "Новая"},
    {"value": "in_progress", "label": "В работе"},
    {"value": "contacted", "label": "Связались"},
    {"value": "measurement_scheduled", "label": "Замер назначен"},
    {"value": "quote_prepared", "label": "Расчёт подготовлен"},
    {"value": "completed", "label": "Завершена"},
    {"value": "cancelled", "label": "Отменена"},
]


def _request_query(db: Session):
    return db.query(FurnitureRequest).options(
        selectinload(FurnitureRequest.material),
        selectinload(FurnitureRequest.assigned_manager),
        selectinload(FurnitureRequest.comments)
        .selectinload(FurnitureComment.user),
        selectinload(FurnitureRequest.events)
        .selectinload(RequestEvent.user),
        selectinload(FurnitureRequest.product)
        .selectinload(Product.material_ref),
        selectinload(FurnitureRequest.product)
        .selectinload(Product.category),
        selectinload(FurnitureRequest.product)
        .selectinload(Product.images),
        selectinload(FurnitureRequest.product)
        .selectinload(Product.product_attributes)
        .selectinload(ProductAttribute.attribute_value)
        .selectinload(AttributeValue.attribute),
    )


def _get_request_or_404(request_id: int, db: Session) -> FurnitureRequest:
    request = _request_query(db).filter(
        FurnitureRequest.id == request_id
    ).first()

    if not request:
        raise HTTPException(
            status_code=404,
            detail="Заявка не найдена"
        )

    return request


def _get_product_or_404(product_id: int, db: Session) -> Product:
    product = db.query(Product).filter(
        Product.id == product_id
    ).first()

    if not product:
        raise HTTPException(
            status_code=404,
            detail="Товар не найден"
        )

    return product


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


def _get_assignable_manager_or_404(
    manager_id: int,
    db: Session,
) -> User:
    manager = db.query(User).filter(
        User.id == manager_id
    ).first()

    if not manager:
        raise HTTPException(
            status_code=404,
            detail="Менеджер не найден"
        )

    if manager.role not in {"admin", "manager"}:
        raise HTTPException(
            status_code=400,
            detail="Заявку можно назначить только сотруднику"
        )

    return manager


def _add_request_event(
    request: FurnitureRequest,
    user: User,
    event_type: str,
    db: Session,
    old_status: str | None = None,
    new_status: str | None = None,
    message: str | None = None,
) -> None:
    event = RequestEvent(
        request_id=request.id,
        user_id=user.id,
        event_type=event_type,
        old_status=old_status,
        new_status=new_status,
        message=message
    )
    db.add(event)


def _set_request_timestamps(request: FurnitureRequest, status: str) -> None:
    now = datetime.now(timezone.utc)
    request.updated_at = now

    if status in {"contacted", "measurement_scheduled", "quote_prepared", "completed"}:
        request.contacted_at = request.contacted_at or now

    if status == "completed":
        request.completed_at = request.completed_at or now
    elif request.completed_at is not None:
        request.completed_at = None


def _change_request_status(
    request: FurnitureRequest,
    new_status: RequestStatus,
    current_user: User,
    db: Session,
) -> None:
    old_status = request.status

    if old_status == new_status:
        return

    request.status = new_status
    _set_request_timestamps(request, new_status)
    _add_request_event(
        request=request,
        user=current_user,
        event_type="status_changed",
        old_status=old_status,
        new_status=new_status,
        message=f"Статус изменён с {old_status} на {new_status}",
        db=db,
    )


def _assign_request_manager(
    request: FurnitureRequest,
    manager_id: int | None,
    current_user: User,
    db: Session,
) -> None:
    if (
        current_user.role == "manager"
        and manager_id not in {current_user.id, None}
    ):
        raise HTTPException(
            status_code=403,
            detail="Менеджер может назначить заявку только на себя"
        )

    manager = None
    if manager_id is not None:
        manager = _get_assignable_manager_or_404(manager_id, db)

    old_manager_id = request.assigned_manager_id
    new_manager_id = manager.id if manager else None

    if old_manager_id == new_manager_id:
        return

    request.assigned_manager_id = new_manager_id
    request.updated_at = datetime.now(timezone.utc)
    _add_request_event(
        request=request,
        user=current_user,
        event_type="manager_assigned",
        message=(
            f"Ответственный изменён с {old_manager_id} "
            f"на {new_manager_id}"
        ),
        db=db,
    )


@router.post(
    "/",
    response_model=FurnitureRequestResponse,
)
def create_request(
    request: FurnitureRequestCreate,
    db: Session = Depends(get_db)
):
    product = None
    if request.product_id is not None:
        product = _get_product_or_404(request.product_id, db)

    material_id = request.material_id
    if material_id is not None:
        _get_material_or_404(material_id, db)
    elif product and product.material_id is not None:
        material_id = product.material_id

    product_name = product.product_name if product else request.product_name
    color_name = request.color_name or (product.color if product else None)

    new_request = FurnitureRequest(
        product_id=request.product_id,
        material_id=material_id,
        product_name=product_name,
        color_name=color_name,
        needs_measurements=request.needs_measurements,
        dimensions=request.dimensions,
        client_name=request.client_name,
        phone=request.phone,
        city=request.city,
        preferred_contact_time=request.preferred_contact_time,
        personal_data_consent=request.personal_data_consent,
        status="new",
        comment=request.comment
    )
    db.add(new_request)
    db.commit()
    db.refresh(new_request)

    return serialize_request(new_request)


@router.get(
    "/",
    response_model=FurnitureRequestListResponse
)
def get_requests(
    status: RequestStatus | None = None,
    assigned_manager_id: int | None = None,
    unassigned_only: bool = False,
    product_id: int | None = None,
    material_id: int | None = None,
    phone: str | None = None,
    city: str | None = None,
    search: str | None = None,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    _current_user: User = Depends(require_manager_or_admin)
):
    query = _request_query(db)

    if status is not None:
        query = query.filter(
            FurnitureRequest.status == status
        )

    if unassigned_only:
        query = query.filter(
            FurnitureRequest.assigned_manager_id.is_(None)
        )
    elif assigned_manager_id is not None:
        query = query.filter(
            FurnitureRequest.assigned_manager_id == assigned_manager_id
        )

    if product_id is not None:
        query = query.filter(
            FurnitureRequest.product_id == product_id
        )

    if material_id is not None:
        query = query.filter(
            FurnitureRequest.material_id == material_id
        )

    if phone:
        query = query.filter(
            FurnitureRequest.phone.ilike(f"%{phone}%")
        )

    if city:
        query = query.filter(
            FurnitureRequest.city.ilike(f"%{city}%")
        )

    if search:
        search_filter = f"%{search}%"
        query = query.filter(
            or_(
                FurnitureRequest.product_name.ilike(search_filter),
                FurnitureRequest.material.has(Material.name.ilike(search_filter)),
                FurnitureRequest.client_name.ilike(search_filter),
                FurnitureRequest.phone.ilike(search_filter),
                FurnitureRequest.city.ilike(search_filter),
                FurnitureRequest.preferred_contact_time.ilike(search_filter),
                FurnitureRequest.comment.ilike(search_filter),
            )
        )

    query = query.order_by(
        FurnitureRequest.created_at.desc(),
        FurnitureRequest.id.desc()
    )
    requests, total = paginate_query(query, limit, offset)

    return {
        "items": [
            serialize_request(request)
            for request in requests
        ],
        "total": total,
        "limit": limit,
        "offset": offset,
    }


@router.get(
    "/my",
    response_model=FurnitureRequestListResponse
)
def get_my_requests(
    status: RequestStatus | None = None,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_manager_or_admin)
):
    query = _request_query(db).filter(
        FurnitureRequest.assigned_manager_id == current_user.id
    )

    if status is not None:
        query = query.filter(
            FurnitureRequest.status == status
        )

    query = query.order_by(
        FurnitureRequest.created_at.desc(),
        FurnitureRequest.id.desc()
    )
    requests, total = paginate_query(query, limit, offset)

    return {
        "items": [
            serialize_request(request)
            for request in requests
        ],
        "total": total,
        "limit": limit,
        "offset": offset,
    }


@router.get(
    "/statuses",
    response_model=list[RequestStatusOption]
)
def get_request_statuses(
    _current_user: User = Depends(require_manager_or_admin)
):
    return REQUEST_STATUS_OPTIONS


@router.get(
    "/{request_id}",
    response_model=FurnitureRequestResponse
)
def get_request(
    request_id: int,
    db: Session = Depends(get_db),
    _current_user: User = Depends(require_manager_or_admin)
):
    return serialize_request(
        _get_request_or_404(request_id, db)
    )


@router.get(
    "/{request_id}/details",
    response_model=FurnitureRequestDetailResponse
)
def get_request_details(
    request_id: int,
    db: Session = Depends(get_db),
    _current_user: User = Depends(require_manager_or_admin)
):
    return serialize_request_detail(
        _get_request_or_404(request_id, db)
    )


@router.patch(
    "/{request_id}",
    response_model=FurnitureRequestResponse
)
def patch_request(
    request_id: int,
    request_data: FurnitureRequestUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_manager_or_admin)
):
    request = _get_request_or_404(request_id, db)
    update_data = request_data.model_dump(exclude_unset=True)

    for field in {
        "product_name",
        "needs_measurements",
        "client_name",
        "phone",
        "personal_data_consent",
    }:
        if field in update_data and update_data[field] is None:
            raise HTTPException(
                status_code=400,
                detail=f"Поле {field} не может быть пустым"
            )

    if "product_id" in update_data and update_data["product_id"] is not None:
        product = _get_product_or_404(update_data["product_id"], db)
        update_data["product_name"] = product.product_name
        if "material_id" not in update_data and product.material_id is not None:
            update_data["material_id"] = product.material_id
        if "color_name" not in update_data and product.color is not None:
            update_data["color_name"] = product.color

    if "material_id" in update_data and update_data["material_id"] is not None:
        _get_material_or_404(update_data["material_id"], db)

    if "status" in update_data:
        new_status = update_data.pop("status")
        if new_status is not None:
            _change_request_status(request, new_status, current_user, db)

    if "assigned_manager_id" in update_data:
        manager_id = update_data.pop("assigned_manager_id")
        _assign_request_manager(request, manager_id, current_user, db)

    for field, value in update_data.items():
        setattr(request, field, value)

    if update_data:
        request.updated_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(request)

    return serialize_request(request)


@router.patch(
    "/{request_id}/status",
    response_model=FurnitureRequestResponse
)
def update_request_status(
    request_id: int,
    status_data: FurnitureRequestStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_manager_or_admin)
):
    request = _get_request_or_404(request_id, db)
    _change_request_status(request, status_data.status, current_user, db)

    db.commit()
    db.refresh(request)

    return serialize_request(request)


@router.patch(
    "/{request_id}/manager",
    response_model=FurnitureRequestResponse
)
def update_request_manager(
    request_id: int,
    manager_data: FurnitureRequestManagerUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_manager_or_admin)
):
    request = _get_request_or_404(request_id, db)
    _assign_request_manager(
        request,
        manager_data.assigned_manager_id,
        current_user,
        db
    )

    db.commit()
    db.refresh(request)

    return serialize_request(request)


@router.patch(
    "/{request_id}/take",
    response_model=FurnitureRequestResponse
)
def take_request(
    request_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_manager_or_admin)
):
    request = _get_request_or_404(request_id, db)
    _assign_request_manager(request, current_user.id, current_user, db)

    db.commit()
    db.refresh(request)

    return serialize_request(request)


@router.get(
    "/{request_id}/events",
    response_model=list[RequestEventResponse]
)
def get_request_events(
    request_id: int,
    db: Session = Depends(get_db),
    _current_user: User = Depends(require_manager_or_admin)
):
    request = _get_request_or_404(request_id, db)

    return [
        serialize_request_event(event)
        for event in sorted(
            request.events,
            key=lambda event: (event.created_at, event.id),
        )
    ]


@router.delete(
    "/{request_id}"
)
def delete_request(
    request_id: int,
    db: Session = Depends(get_db),
    _current_user: User = Depends(require_admin)
):
    request = _get_request_or_404(request_id, db)

    db.delete(request)
    db.commit()

    return {
        "message": "Заявка успешно удалена"
    }
