import hashlib
import hmac
import time

from fastapi import HTTPException
from sqlalchemy import case
from sqlalchemy.dialects.postgresql import insert as postgres_insert
from sqlalchemy.dialects.sqlite import insert as sqlite_insert

from app.models.auth_session import AuthRateLimit
from app.settings import TOKEN_SECRET

WINDOW_SECONDS = 900
ACCOUNT_LIMIT = 10
IP_LIMIT = 30


def check_login_limits(db, login: str, ip: str):
    """Atomic database counters work across processes; no trust in client IP headers."""
    now = int(time.time())
    db.query(AuthRateLimit).filter(AuthRateLimit.expires_at <= now).delete(synchronize_session=False)
    insert = postgres_insert if db.bind.dialect.name == 'postgresql' else sqlite_insert
    for scope, identity, limit in [('ip', ip, IP_LIMIT), ('account', login, ACCOUNT_LIMIT)]:
        digest = hmac.new(TOKEN_SECRET.encode(), f'{scope}:{identity}'.encode(), hashlib.sha256).hexdigest()
        key = f'{scope}:{digest}'
        stmt = insert(AuthRateLimit).values(key=key, attempts=1, expires_at=now + WINDOW_SECONDS)
        # The expired branch also handles competing cleanup/insert transactions.
        expired = AuthRateLimit.expires_at <= now
        stmt = stmt.on_conflict_do_update(index_elements=['key'], set_={
            'attempts': case((expired, 1), else_=AuthRateLimit.attempts + 1),
            'expires_at': case((expired, now + WINDOW_SECONDS), else_=AuthRateLimit.expires_at),
        }).returning(AuthRateLimit.attempts, AuthRateLimit.expires_at)
        attempts, expires = db.execute(stmt).one()
        db.commit()
        if attempts > limit:
            raise HTTPException(429, 'Слишком много попыток входа. Попробуйте позже.', headers={'Retry-After': str(max(1, expires - now))})
