from datetime import datetime, timedelta, timezone

from sqlalchemy import select

from app.maintenance import cleanup_expired
from app.models.auth_session import AuthRateLimit, AuthSession
from app.models.public_rate_limit import PublicRequestRateLimit


def test_cleanup_preview_and_apply_keep_live_records(db_session):
    now = datetime.now(timezone.utc)
    for name, delta in (('old', -1), ('boundary', 0), ('live', 3600)):
        db_session.add(AuthSession(id=name, user_id=1, expires_at=now + timedelta(seconds=delta)))
        for model in (AuthRateLimit, PublicRequestRateLimit):
            db_session.add(model(key=name, attempts=4, expires_at=int(now.timestamp()) + delta))
    db_session.commit()
    expected = {'auth_sessions': 2, 'auth_rate_limits': 2, 'public_request_rate_limits': 2}
    assert cleanup_expired(db_session, now=now) == expected
    for model in (AuthSession, AuthRateLimit, PublicRequestRateLimit):
        assert len(db_session.scalars(select(model)).all()) == 3
    assert cleanup_expired(db_session, apply=True, now=now) == expected
    for model in (AuthSession, AuthRateLimit, PublicRequestRateLimit):
        remaining = db_session.scalars(select(model)).all()
        assert len(remaining) == 1
        assert remaining[0].expires_at is not None
    assert cleanup_expired(db_session, apply=True, now=now) == dict.fromkeys(expected, 0)
