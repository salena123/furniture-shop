from __future__ import annotations

import hashlib
import os
import secrets
from datetime import datetime, timedelta, timezone
from typing import Any, Callable

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User


TOKEN_SECRET = (
    os.getenv("SECRET_KEY")
    or os.getenv("JWT_SECRET_KEY")
    or "dev-secret-key-change-me-32-bytes-minimum"
)
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))
TOKEN_EXPIRE_SECONDS = TOKEN_EXPIRE_MINUTES * 60
PASSWORD_HASH_ITERATIONS = 120_000

bearer_scheme = HTTPBearer(auto_error=False)


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        PASSWORD_HASH_ITERATIONS,
    ).hex()
    return f"pbkdf2_sha256${PASSWORD_HASH_ITERATIONS}${salt}${digest}"


def verify_password(password: str, password_hash: str) -> bool:
    try:
        algorithm, iterations, salt, expected_digest = password_hash.split("$", 3)
    except ValueError:
        return False

    if algorithm != "pbkdf2_sha256":
        return False

    digest = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        int(iterations),
    ).hex()
    return secrets.compare_digest(digest, expected_digest)


def get_access_token_expires_at(now: datetime | None = None) -> datetime:
    now = now or _utc_now()
    return now + timedelta(seconds=TOKEN_EXPIRE_SECONDS)


def get_access_token_expires_in(
    expires_at: datetime,
    now: datetime | None = None,
) -> int:
    now = now or _utc_now()
    return max(0, int((expires_at - now).total_seconds()))


def create_access_token(
    user: User,
    expires_at: datetime | None = None,
) -> str:
    issued_at = _utc_now()
    expires_at = expires_at or get_access_token_expires_at(issued_at)
    payload = {
        "sub": str(user.id),
        "role": user.role,
        "type": "access",
        "iat": issued_at,
        "exp": expires_at,
    }

    return jwt.encode(payload, TOKEN_SECRET, algorithm=JWT_ALGORITHM)


def decode_access_token(token: str) -> dict[str, Any]:
    try:
        payload = jwt.decode(
            token,
            TOKEN_SECRET,
            algorithms=[JWT_ALGORITHM],
        )
    except jwt.ExpiredSignatureError as exc:
        raise ValueError("Срок действия токена истёк") from exc
    except jwt.InvalidTokenError as exc:
        raise ValueError("Некорректный токен") from exc

    if payload.get("type") != "access":
        raise ValueError("Некорректный тип токена")

    return payload


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Нужна авторизация",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        payload = decode_access_token(credentials.credentials)
        user_id = int(payload["sub"])
    except (KeyError, TypeError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный или просроченный токен",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Пользователь не найден",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


def get_optional_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User | None:
    if credentials is None:
        return None

    return get_current_user(credentials, db)


def require_roles(*roles: str) -> Callable[[User], User]:
    def dependency(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Недостаточно прав",
            )
        return current_user

    return dependency


def require_admin(current_user: User = Depends(require_roles("admin"))) -> User:
    return current_user


def require_manager_or_admin(
    current_user: User = Depends(require_roles("admin", "manager")),
) -> User:
    return current_user
