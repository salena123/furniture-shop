from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
import secrets
from datetime import datetime, timedelta, timezone
from typing import Any, Callable

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User


TOKEN_SECRET = os.getenv("SECRET_KEY") or os.getenv("JWT_SECRET_KEY") or "dev-secret-key"
TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))
PASSWORD_HASH_ITERATIONS = 120_000

bearer_scheme = HTTPBearer(auto_error=False)


def _base64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode("utf-8").rstrip("=")


def _base64url_decode(data: str) -> bytes:
    padding = "=" * (-len(data) % 4)
    return base64.urlsafe_b64decode(data + padding)


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


def create_access_token(user: User) -> str:
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=TOKEN_EXPIRE_MINUTES)
    payload = {
        "sub": str(user.id),
        "role": user.role,
        "exp": int(expires_at.timestamp()),
    }
    payload_data = _base64url_encode(
        json.dumps(payload, separators=(",", ":")).encode("utf-8")
    )
    signature = hmac.new(
        TOKEN_SECRET.encode("utf-8"),
        payload_data.encode("utf-8"),
        hashlib.sha256,
    ).digest()
    return f"{payload_data}.{_base64url_encode(signature)}"


def decode_access_token(token: str) -> dict[str, Any]:
    try:
        payload_data, signature = token.split(".", 1)
    except ValueError as exc:
        raise ValueError("Некорректный токен") from exc

    expected_signature = hmac.new(
        TOKEN_SECRET.encode("utf-8"),
        payload_data.encode("utf-8"),
        hashlib.sha256,
    ).digest()

    if not secrets.compare_digest(_base64url_encode(expected_signature), signature):
        raise ValueError("Некорректная подпись токена")

    payload = json.loads(_base64url_decode(payload_data))
    expires_at = payload.get("exp")
    if not expires_at or int(expires_at) < int(datetime.now(timezone.utc).timestamp()):
        raise ValueError("Срок действия токена истёк")

    return payload


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Нужна авторизация",
        )

    try:
        payload = decode_access_token(credentials.credentials)
        user_id = int(payload["sub"])
    except (KeyError, TypeError, ValueError, json.JSONDecodeError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный или просроченный токен",
        )

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Пользователь не найден",
        )

    return user


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
