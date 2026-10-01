from datetime import datetime

from sqlalchemy import ForeignKey, String, TIMESTAMP
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class AuthSession(Base):
    __tablename__ = 'auth_sessions'
    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'), index=True)
    expires_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), index=True)


class AuthRateLimit(Base):
    __tablename__ = 'auth_rate_limits'
    key: Mapped[str] = mapped_column(String(80), primary_key=True)
    attempts: Mapped[int] = mapped_column(default=0)
    expires_at: Mapped[int] = mapped_column(index=True)
