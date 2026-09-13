from datetime import datetime

from sqlalchemy import Enum, Integer, Text, TIMESTAMP, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class RequestEvent(Base):
    __tablename__ = "request_events"

    id: Mapped[int] = mapped_column(primary_key=True)

    request_id: Mapped[int] = mapped_column(
        ForeignKey("furniture_requests.id", ondelete="CASCADE"),
        nullable=False
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False
    )

    event_type: Mapped[str] = mapped_column(
        Enum(
            "created",
            "status_changed",
            "manager_assigned",
            "comment_added",
            name="request_event_type",
            native_enum=True
        ),
        nullable=False
    )

    old_status: Mapped[str | None] = mapped_column(
        Enum(
            "new",
            "in_progress",
            "contacted",
            "measurement_scheduled",
            "quote_prepared",
            "completed",
            "cancelled",
            name="request_status",
            native_enum=True,
            create_type=False
        ),
        nullable=True
    )

    new_status: Mapped[str | None] = mapped_column(
        Enum(
            "new",
            "in_progress",
            "contacted",
            "measurement_scheduled",
            "quote_prepared",
            "completed",
            "cancelled",
            name="request_status",
            native_enum=True,
            create_type=False
        ),
        nullable=True
    )

    message: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=func.now()
    )
    
    request: Mapped["FurnitureRequest"] = relationship(
        "FurnitureRequest",
        back_populates="events"
    )
    user: Mapped["User"] = relationship(
        "User",
        back_populates="request_events"
    )