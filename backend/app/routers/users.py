from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.furniture_comment import FurnitureComment
from app.models.furniture_request import FurnitureRequest
from app.models.request_event import RequestEvent
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse, UserUpdate
from app.security import hash_password, require_admin, require_manager_or_admin


router = APIRouter(
    prefix="/api/users",
    tags=["Пользователи"]
)


def _get_user_or_404(user_id: int, db: Session) -> User:
    user = db.query(User).filter(
        User.id == user_id
    ).first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="Пользователь не найден"
        )

    return user


def _ensure_login_is_free(
    login: str,
    db: Session,
    current_user_id: int | None = None
) -> None:
    existing_user = db.query(User).filter(
        User.login == login
    ).first()

    if existing_user and existing_user.id != current_user_id:
        raise HTTPException(
            status_code=400,
            detail="Пользователь с таким логином уже существует"
        )


@router.post(
    "/bootstrap-admin",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED
)
def create_first_admin(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    existing_user = db.query(User).first()
    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Первый администратор уже создан"
        )

    _ensure_login_is_free(user_data.login, db)

    user = User(
        login=user_data.login,
        name=user_data.name,
        email=user_data.email,
        password_hash=hash_password(user_data.password),
        role="admin"
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


@router.post(
    "/",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED
)
def create_user(
    user_data: UserCreate,
    db: Session = Depends(get_db),
    _current_user: User = Depends(require_admin)
):
    _ensure_login_is_free(user_data.login, db)

    user = User(
        login=user_data.login,
        name=user_data.name,
        email=user_data.email,
        password_hash=hash_password(user_data.password),
        role=user_data.role
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


@router.get(
    "/",
    response_model=list[UserResponse]
)
def get_users(
    db: Session = Depends(get_db),
    _current_user: User = Depends(require_admin)
):
    return db.query(User).order_by(
        User.id
    ).all()


@router.get(
    "/managers",
    response_model=list[UserResponse]
)
def get_managers(
    db: Session = Depends(get_db),
    _current_user: User = Depends(require_manager_or_admin)
):
    return db.query(User).filter(
        User.role.in_(["admin", "manager"])
    ).order_by(
        User.name,
        User.id
    ).all()


@router.get(
    "/{user_id}",
    response_model=UserResponse
)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    _current_user: User = Depends(require_admin)
):
    return _get_user_or_404(user_id, db)


@router.patch(
    "/{user_id}",
    response_model=UserResponse
)
@router.put(
    "/{user_id}",
    response_model=UserResponse
)
def update_user(
    user_id: int,
    user_data: UserUpdate,
    db: Session = Depends(get_db),
    _current_user: User = Depends(require_admin)
):
    user = _get_user_or_404(user_id, db)
    update_data = user_data.model_dump(exclude_unset=True)

    for field in {"login", "name", "role"}:
        if field in update_data and update_data[field] is None:
            raise HTTPException(
                status_code=400,
                detail=f"Поле {field} не может быть пустым"
            )

    if "login" in update_data:
        _ensure_login_is_free(update_data["login"], db, current_user_id=user.id)
        user.login = update_data["login"]
    if "name" in update_data:
        user.name = update_data["name"]
    if "email" in update_data:
        user.email = update_data["email"]
    if "password" in update_data and update_data["password"] is not None:
        user.password_hash = hash_password(update_data["password"])
    if "role" in update_data:
        user.role = update_data["role"]

    db.commit()
    db.refresh(user)

    return user


@router.delete(
    "/{user_id}"
)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    _current_user: User = Depends(require_admin)
):
    user = _get_user_or_404(user_id, db)

    if user.role == "admin":
        admins_count = db.query(User).filter(
            User.role == "admin"
        ).count()
        if admins_count == 1:
            raise HTTPException(
                status_code=400,
                detail="Нельзя удалить последнего администратора"
            )

    comments_count = db.query(FurnitureComment).filter(
        FurnitureComment.user_id == user.id
    ).count()
    events_count = db.query(RequestEvent).filter(
        RequestEvent.user_id == user.id
    ).count()

    if comments_count or events_count:
        raise HTTPException(
            status_code=400,
            detail=(
                "Пользователя нельзя удалить: "
                f"комментариев {comments_count}, событий заявок {events_count}"
            )
        )

    detached_requests = db.query(FurnitureRequest).filter(
        FurnitureRequest.assigned_manager_id == user.id
    ).update(
        {FurnitureRequest.assigned_manager_id: None},
        synchronize_session=False
    )

    db.delete(user)
    db.commit()

    return {
        "message": "Пользователь успешно удалён",
        "detached_requests": detached_requests,
    }
