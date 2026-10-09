from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class PublicRequestRateLimit(Base):
    __tablename__ = 'public_request_rate_limits'

    key: Mapped[str] = mapped_column(String(80), primary_key=True)
    attempts: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    expires_at: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
