from fastapi import Depends, APIRouter, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.furniture_request import FurnitureRequest
from app.schemas.furniture_request import FurnitureRequestCreate, FurnitureRequestResponse

router = APIRouter(
    prefix="/api/requests",
    tags=["Заявки"]
)

@router.post(
    "/",
    response_model=FurnitureRequestResponse,
)
def create_request(
    request: FurnitureRequestCreate,
    db: Session = Depends(get_db)
):
    new_request = FurnitureRequest(
        product_id=request.product_id,
        product_name=request.product_name,
        color_name=request.color_name,
        needs_measurements=request.needs_measurements,
        dimensions=request.dimensions,
        client_name=request.client_name,
        phone=request.phone,
        status="new"
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
    db: Session = Depends(get_db)
):
    requests = db.query(FurnitureRequest).all()
    return requests

@router.get(
    "/{request_id}",
    response_model=FurnitureRequestResponse
)
def get_request(
    request_id: int,
    db: Session = Depends(get_db)
):
    request = db.query(FurnitureRequest).filter(
        FurnitureRequest.id == request_id).first()
    if not request:
        raise HTTPException(status_code=404, detail="Заявка не найдена")
    return request