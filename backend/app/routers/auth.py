from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas.user import TokenResponse, UserLogin, UserResponse
from app.security import (
    create_access_token,
    get_access_token_expires_at,
    get_access_token_expires_in,
    get_current_user,
    verify_password,
)


router = APIRouter(
    prefix="/api/auth",
    tags=["Авторизация"]
)


@router.post(
    "/login",
    response_model=TokenResponse
)
def login(
    credentials: UserLogin,
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(
        User.login == credentials.login
    ).first()

    if not user or not verify_password(credentials.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный логин или пароль"
        )

    user.last_login_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(user)

    expires_at = get_access_token_expires_at()

    return {
        "access_token": create_access_token(user, expires_at=expires_at),
        "token_type": "bearer",
        "expires_in": get_access_token_expires_in(expires_at),
        "expires_at": expires_at,
        "user": user
    }


@router.get(
    "/me",
    response_model=UserResponse
)
def get_me(
    current_user: User = Depends(get_current_user)
):
    return current_user
