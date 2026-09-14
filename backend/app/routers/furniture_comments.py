from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.furniture_request import FurnitureRequest
from app.models.furniture_comment import FurnitureComment
from app.models.request_event import RequestEvent
from app.models.user import User
from app.schemas.furniture_comment import (
    FurnitureCommentCreate,
    FurnitureCommentResponse,
    FurnitureCommentUpdate
)
from app.security import require_manager_or_admin

router = APIRouter(
    prefix="/api/requests",
    tags=["Комментарии к заявкам"]
)


@router.post(
    "/{request_id}/comments",
    response_model=FurnitureCommentResponse
)
def create_comment(
    request_id: int,
    comment: FurnitureCommentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_manager_or_admin)
):
    request = db.query(FurnitureRequest).filter(
        FurnitureRequest.id == request_id
    ).first()

    if not request:
        raise HTTPException(
            status_code=404,
            detail="Заявка не найдена"
        )

    new_comment = FurnitureComment(
        request_id=request_id,
        user_id=current_user.id,
        comment_text=comment.comment_text
    )

    db.add(new_comment)
    db.flush()

    event = RequestEvent(
        request_id=request_id,
        user_id=current_user.id,
        event_type="comment_added",
        message=f"Добавлен комментарий #{new_comment.id}"
    )
    db.add(event)
    db.commit()
    db.refresh(new_comment)

    return new_comment


@router.get(
    "/{request_id}/comments",
    response_model=list[FurnitureCommentResponse]
)
def get_comments(
    request_id: int,
    db: Session = Depends(get_db),
    _current_user: User = Depends(require_manager_or_admin)
):
    request = db.query(FurnitureRequest).filter(
        FurnitureRequest.id == request_id
    ).first()

    if not request:
        raise HTTPException(
            status_code=404,
            detail="Заявка не найдена"
        )

    comments = db.query(FurnitureComment).filter(
        FurnitureComment.request_id == request_id
    ).order_by(
        FurnitureComment.created_at
    ).all()

    return comments


@router.get(
    "/{request_id}/comments/{comment_id}",
    response_model=FurnitureCommentResponse
)
def get_comment(
    request_id: int,
    comment_id: int,
    db: Session = Depends(get_db),
    _current_user: User = Depends(require_manager_or_admin)
):
    comment = db.query(FurnitureComment).filter(
        FurnitureComment.id == comment_id,
        FurnitureComment.request_id == request_id
    ).first()

    if not comment:
        raise HTTPException(
            status_code=404,
            detail="Комментарий не найден"
        )

    return comment


@router.put(
    "/{request_id}/comments/{comment_id}",
    response_model=FurnitureCommentResponse
)
def update_comment(
    request_id: int,
    comment_id: int,
    comment_data: FurnitureCommentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_manager_or_admin)
):
    comment = db.query(FurnitureComment).filter(
        FurnitureComment.id == comment_id,
        FurnitureComment.request_id == request_id
    ).first()

    if not comment:
        raise HTTPException(
            status_code=404,
            detail="Комментарий не найден"
        )

    if current_user.role != "admin" and comment.user_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Можно редактировать только свои комментарии"
        )

    comment.comment_text = comment_data.comment_text
    db.commit()
    db.refresh(comment)

    return comment


@router.delete(
    "/{request_id}/comments/{comment_id}"
)
def delete_comment(
    request_id: int,
    comment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_manager_or_admin)
):
    comment = db.query(FurnitureComment).filter(
        FurnitureComment.id == comment_id,
        FurnitureComment.request_id == request_id
    ).first()

    if not comment:
        raise HTTPException(
            status_code=404,
            detail="Комментарий не найден"
        )

    if current_user.role != "admin" and comment.user_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Можно удалить только свои комментарии"
        )

    db.delete(comment)
    db.commit()

    return {
        "message": "Комментарий успешно удалён"
    }
