"""Remove expired technical records; preview by default.

Run from backend: python -m app.maintenance [--apply]
"""
import argparse
from datetime import datetime, timezone

from sqlalchemy import delete, func, select

from app.database import SessionLocal
from app.models.auth_session import AuthRateLimit, AuthSession
from app.models.public_rate_limit import PublicRequestRateLimit


def cleanup_expired(db, *, apply=False, now=None):
    now = now or datetime.now(timezone.utc)
    rules = (
        (AuthSession, AuthSession.expires_at <= now),
        (AuthRateLimit, AuthRateLimit.expires_at <= int(now.timestamp())),
        (PublicRequestRateLimit, PublicRequestRateLimit.expires_at <= int(now.timestamp())),
    )
    counts = {}
    for model, expired in rules:
        if apply:
            counts[model.__tablename__] = db.execute(delete(model).where(expired)).rowcount
        else:
            counts[model.__tablename__] = db.scalar(
                select(func.count()).select_from(model).where(expired)
            )
    if apply:
        db.commit()
    return counts


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--apply', action='store_true', help='Actually delete expired records')
    args = parser.parse_args()
    with SessionLocal() as db:
        counts = cleanup_expired(db, apply=args.apply)
    print('Deleted:' if args.apply else 'Preview (nothing deleted):', counts)


if __name__ == '__main__':
    main()
