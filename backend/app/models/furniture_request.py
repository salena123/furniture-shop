from datetime import datetime

from sqlalchemy import Boolean, Enum, Integer, String, Text, TIMESTAMP, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class FurnitureRequest(Base):
    __tablename__ = "furniture_requests"

    id: Mapped[int] = mapped_column(primary_key=True)

    product_id: Mapped[int | None] = mapped_column(
        ForeignKey("products.id"),
        nullable=True
    )

    product_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    color_name: Mapped[str | None] = mapped_column(
        String(150),
        nullable=True
    )

    needs_measurements: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False
    )

    dimensions: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True
    )

    client_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    phone: Mapped[str] = mapped_column(
        String(30),
        nullable=False
    )

    status: Mapped[str] = mapped_column(
        Enum(
            "new",
            "in_progress",
            "contacted",
            "measurement_scheduled",
            "quote_prepared",
            "completed",
            "cancelled",
            name="request_status",
            native_enum=True
        ),
        nullable=False,
        server_default="new"
    )

    assigned_manager_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id"),
        nullable=True
    )

    comment: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=func.now()
    )

    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    contacted_at: Mapped[datetime | None] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=True
    )

    completed_at: Mapped[datetime | None] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=True
    )
    product: Mapped["Product | None"] = relationship(
        "Product",
        back_populates="furniture_requests"
    )
    assigned_manager: Mapped["User | None"] = relationship(
        "User",
        back_populates="requests"
    )
    events: Mapped[list["RequestEvent"]] = relationship(
        "RequestEvent",
        back_populates="request",
        cascade="all, delete-orphan"
    )
    comments: Mapped[list["FurnitureComment"]] = relationship(
        "FurnitureComment",
        back_populates="request",
        cascade="all, delete-orphan"
    )