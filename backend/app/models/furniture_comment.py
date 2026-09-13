from datetime import datetime

from sqlalchemy import ForeignKey, Text, TIMESTAMP, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class FurnitureComment(Base):
    __tablename__ = "furniture_comments"

    id: Mapped[int] = mapped_column(primary_key=True)

    request_id: Mapped[int] = mapped_column(
    ForeignKey("furniture_requests.id", ondelete="CASCADE"),
    nullable=False
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False
    )

    comment_text: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=func.now()
    )
    request: Mapped["FurnitureRequest"] = relationship(
        "FurnitureRequest",
        back_populates="comments"
    )
    user: Mapped["User"] = relationship(
        "User",
        back_populates="comments"
    )