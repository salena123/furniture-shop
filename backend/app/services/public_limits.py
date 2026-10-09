import hashlib
import hmac
import time

from fastapi import HTTPException
from sqlalchemy import case
from sqlalchemy.dialects.postgresql import insert as postgres_insert
from sqlalchemy.dialects.sqlite import insert as sqlite_insert

from app.models.public_rate_limit import PublicRequestRateLimit
from app.settings import TOKEN_SECRET

WINDOW_SECONDS = 900
REQUEST_LIMIT = 10


def check_public_request_limit(db, ip: str) -> None:
    now = int(time.time())
    db.query(PublicRequestRateLimit).filter(
        PublicRequestRateLimit.expires_at <= now
    ).delete(synchronize_session=False)
    insert = postgres_insert if db.bind.dialect.name == 'postgresql' else sqlite_insert
    key = 'request:' + hmac.new(
        TOKEN_SECRET.encode(), ip.encode(), hashlib.sha256
    ).hexdigest()
    statement = insert(PublicRequestRateLimit).values(
        key=key, attempts=1, expires_at=now + WINDOW_SECONDS
    )
    expired = PublicRequestRateLimit.expires_at <= now
    statement = statement.on_conflict_do_update(
        index_elements=['key'],
        set_={
            'attempts': case((expired, 1), else_=PublicRequestRateLimit.attempts + 1),
            'expires_at': case((expired, now + WINDOW_SECONDS), else_=PublicRequestRateLimit.expires_at),
        },
    ).returning(PublicRequestRateLimit.attempts, PublicRequestRateLimit.expires_at)
    attempts, expires_at = db.execute(statement).one()
    db.commit()
    if attempts > REQUEST_LIMIT:
        retry_after = max(1, expires_at - now)
        raise HTTPException(
            status_code=429,
            detail='Слишком много заявок. Попробуйте отправить заявку позже.',
            headers={'Retry-After': str(retry_after)},
        )
