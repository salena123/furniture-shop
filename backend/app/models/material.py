from datetime import datetime

from sqlalchemy import String, Text, TIMESTAMP, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Material(Base):
    __tablename__ = "materials"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
        unique=True
    )
    description: Mapped[str | None] = mapped_column(
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
        server_default=func.now()
    )

    products: Mapped[list["Product"]] = relationship(
        "Product",
        back_populates="material_ref"
    )
    furniture_requests: Mapped[list["FurnitureRequest"]] = relationship(
        "FurnitureRequest",
        back_populates="material"
    )
