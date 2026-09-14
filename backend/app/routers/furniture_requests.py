from datetime import datetime, timezone

from fastapi import Depends, APIRouter, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.product import Product
from app.models.request_event import RequestEvent
from app.models.user import User
from app.models.furniture_request import FurnitureRequest
from app.schemas.furniture_request import (
    FurnitureRequestCreate,
    FurnitureRequestManagerUpdate,
    FurnitureRequestResponse,
    FurnitureRequestStatusUpdate,
    RequestStatus,
    RequestEventResponse
)
from app.security import require_admin, require_manager_or_admin

router = APIRouter(
    prefix="/api/requests",
    tags=["Заявки"]
)


def _get_request_or_404(request_id: int, db: Session) -> FurnitureRequest:
    request = db.query(FurnitureRequest).filter(
        FurnitureRequest.id == request_id
    ).first()

    if not request:
        raise HTTPException(
            status_code=404,
            detail="Заявка не найдена"
        )

    return request


def _set_request_timestamps(request: FurnitureRequest, status: str) -> None:
    now = datetime.now(timezone.utc)
    request.updated_at = now

    if status in {"contacted", "measurement_scheduled", "quote_prepared", "completed"}:
        request.contacted_at = request.contacted_at or now

    if status == "completed":
        request.completed_at = request.completed_at or now
    elif request.completed_at is not None:
        request.completed_at = None


@router.post(
    "/",
    response_model=FurnitureRequestResponse,
)
def create_request(
    request: FurnitureRequestCreate,
    db: Session = Depends(get_db)
):
    if request.product_id is not None:
        product = db.query(Product).filter(
            Product.id == request.product_id
        ).first()

        if not product:
            raise HTTPException(
                status_code=404,
                detail="Товар не найден"
            )

    new_request = FurnitureRequest(
        product_id=request.product_id,
        product_name=request.product_name,
        color_name=request.color_name,
        needs_measurements=request.needs_measurements,
        dimensions=request.dimensions,
        client_name=request.client_name,
        phone=request.phone,
        status="new",
        comment=request.comment
    )
    db.add(new_request)
    db.commit()
    db.refresh(new_request)
    return new_request

@router.get(
    "/",
    response_model=list[FurnitureRequestResponse]
)
def get_requests(
    status: RequestStatus | None = None,
    assigned_manager_id: int | None = None,
    db: Session = Depends(get_db),
    _current_user: User = Depends(require_manager_or_admin)
):
    query = db.query(FurnitureRequest)

    if status is not None:
        query = query.filter(
            FurnitureRequest.status == status
        )

    if assigned_manager_id is not None:
        query = query.filter(
            FurnitureRequest.assigned_manager_id == assigned_manager_id
        )

    return query.order_by(
        FurnitureRequest.created_at.desc(),
        FurnitureRequest.id.desc()
    ).all()

@router.get(
    "/{request_id}",
    response_model=FurnitureRequestResponse
)
def get_request(
    request_id: int,
    db: Session = Depends(get_db),
    _current_user: User = Depends(require_manager_or_admin)
):
    return _get_request_or_404(request_id, db)


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
    old_status = request.status

    if old_status != status_data.status:
        request.status = status_data.status
        _set_request_timestamps(request, status_data.status)

        event = RequestEvent(
            request_id=request.id,
            user_id=current_user.id,
            event_type="status_changed",
            old_status=old_status,
            new_status=status_data.status,
            message=f"Статус изменён с {old_status} на {status_data.status}"
        )
        db.add(event)

    db.commit()
    db.refresh(request)

    return request


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

    if (
        current_user.role == "manager"
        and manager_data.assigned_manager_id not in {current_user.id, None}
    ):
        raise HTTPException(
            status_code=403,
            detail="Менеджер может назначить заявку только на себя"
        )

    manager = None
    if manager_data.assigned_manager_id is not None:
        manager = db.query(User).filter(
            User.id == manager_data.assigned_manager_id
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

    old_manager_id = request.assigned_manager_id

    if old_manager_id != manager_data.assigned_manager_id:
        request.assigned_manager_id = manager.id if manager else None
        request.updated_at = datetime.now(timezone.utc)

        event = RequestEvent(
            request_id=request.id,
            user_id=current_user.id,
            event_type="manager_assigned",
            message=(
                f"Ответственный изменён с {old_manager_id} "
                f"на {request.assigned_manager_id}"
            )
        )
        db.add(event)

    db.commit()
    db.refresh(request)

    return request


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
    old_manager_id = request.assigned_manager_id

    if old_manager_id != current_user.id:
        request.assigned_manager_id = current_user.id
        request.updated_at = datetime.now(timezone.utc)

        event = RequestEvent(
            request_id=request.id,
            user_id=current_user.id,
            event_type="manager_assigned",
            message=(
                f"Ответственный изменён с {old_manager_id} "
                f"на {current_user.id}"
            )
        )
        db.add(event)

    db.commit()
    db.refresh(request)

    return request


@router.get(
    "/{request_id}/events",
    response_model=list[RequestEventResponse]
)
def get_request_events(
    request_id: int,
    db: Session = Depends(get_db),
    _current_user: User = Depends(require_manager_or_admin)
):
    _get_request_or_404(request_id, db)

    return db.query(RequestEvent).filter(
        RequestEvent.request_id == request_id
    ).order_by(
        RequestEvent.created_at,
        RequestEvent.id
    ).all()


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
