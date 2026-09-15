from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.furniture_request import FurnitureRequest
from app.models.material import Material
from app.models.product import Product
from app.models.user import User
from app.schemas.dashboard import DashboardStatsResponse
from app.security import require_manager_or_admin


router = APIRouter(
    prefix="/api/dashboard",
    tags=["Дашборд"]
)


def _count_requests(db: Session, *filters) -> int:
    query = db.query(
        func.count(FurnitureRequest.id)
    )

    if filters:
        query = query.filter(*filters)

    return query.scalar() or 0


def _count_products(db: Session, *filters) -> int:
    query = db.query(
        func.count(Product.id)
    )

    if filters:
        query = query.filter(*filters)

    return query.scalar() or 0


def _count_materials(db: Session, *filters) -> int:
    query = db.query(
        func.count(Material.id)
    )

    if filters:
        query = query.filter(*filters)

    return query.scalar() or 0


@router.get(
    "/stats",
    response_model=DashboardStatsResponse
)
def get_dashboard_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_manager_or_admin)
):
    today_start = datetime.now(timezone.utc).replace(
        hour=0,
        minute=0,
        second=0,
        microsecond=0,
    )

    return {
        "total_requests": _count_requests(db),
        "new_requests": _count_requests(db, FurnitureRequest.status == "new"),
        "in_progress_requests": _count_requests(
            db,
            FurnitureRequest.status == "in_progress",
        ),
        "contacted_requests": _count_requests(
            db,
            FurnitureRequest.status == "contacted",
        ),
        "measurement_scheduled_requests": _count_requests(
            db,
            FurnitureRequest.status == "measurement_scheduled",
        ),
        "quote_prepared_requests": _count_requests(
            db,
            FurnitureRequest.status == "quote_prepared",
        ),
        "completed_requests": _count_requests(
            db,
            FurnitureRequest.status == "completed",
        ),
        "cancelled_requests": _count_requests(
            db,
            FurnitureRequest.status == "cancelled",
        ),
        "requests_today": _count_requests(
            db,
            FurnitureRequest.created_at >= today_start,
        ),
        "unassigned_requests": _count_requests(
            db,
            FurnitureRequest.assigned_manager_id.is_(None),
        ),
        "assigned_to_me": _count_requests(
            db,
            FurnitureRequest.assigned_manager_id == current_user.id,
        ),
        "total_products": _count_products(db),
        "active_products": _count_products(db, Product.is_active == True),
        "total_materials": _count_materials(db),
    }
