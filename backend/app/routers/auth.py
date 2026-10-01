from datetime import datetime, timezone
import hashlib
import secrets

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.auth_session import AuthSession
from app.settings import COOKIE_SECURE, SESSION_COOKIE
from app.services.login_limits import check_login_limits
from app.schemas.user import TokenResponse, UserLogin, UserResponse
from app.security import (
    create_access_token,
    get_access_token_expires_at,
    get_access_token_expires_in,
    get_current_user,
    verify_password,
    hash_password,
    PASSWORD_HASH_ITERATIONS,
)

DUMMY_PASSWORD_HASH = hash_password(secrets.token_urlsafe(32))


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
    request: Request,
    response: Response,
    db: Session = Depends(get_db)
):
    check_login_limits(db, credentials.login, request.client.host if request.client else 'unknown')
    user = db.query(User).filter(
        User.login == credentials.login
    ).with_for_update().first()

    valid = verify_password(credentials.password, user.password_hash if user else DUMMY_PASSWORD_HASH)
    if not user or not valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный логин или пароль"
        )

    user.last_login_at = datetime.now(timezone.utc)
    if int(user.password_hash.split('$')[1]) < PASSWORD_HASH_ITERATIONS:
        user.password_hash = hash_password(credentials.password)
    expires_at = get_access_token_expires_at()
    session_id = secrets.token_hex(32)
    db.query(AuthSession).filter(AuthSession.expires_at <= datetime.now(timezone.utc)).delete(synchronize_session=False)
    db.add(AuthSession(id=hashlib.sha256(session_id.encode()).hexdigest(), user_id=user.id, expires_at=expires_at))
    token = create_access_token(user, expires_at=expires_at, session_id=session_id)
    db.commit()
    db.refresh(user)

    response.set_cookie(SESSION_COOKIE, token, httponly=True, secure=COOKIE_SECURE, samesite='strict', path='/', max_age=get_access_token_expires_in(expires_at))
    response.headers['Cache-Control'] = 'no-store'

    return {
        "expires_in": get_access_token_expires_in(expires_at),
        "expires_at": expires_at,
        "user": user
    }


@router.post('/logout', status_code=204)
def logout(request: Request, response: Response, db: Session = Depends(get_db), _user=Depends(get_current_user)):
    db.query(AuthSession).filter(AuthSession.id == request.state.auth_session_id).delete()
    db.commit()
    response.delete_cookie(SESSION_COOKIE, path='/', secure=COOKIE_SECURE, httponly=True, samesite='strict')


@router.get(
    "/me",
    response_model=UserResponse
)
def get_me(
    current_user: User = Depends(get_current_user)
):
    return current_user
