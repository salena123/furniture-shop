from datetime import datetime

from sqlalchemy import Boolean, Integer, String, Text, TIMESTAMP, ForeignKey, Index, func   
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class ProductImage(Base):
    __tablename__ = "product_images"

    id: Mapped[int] = mapped_column(primary_key=True)

    product_id: Mapped[int] = mapped_column(
        ForeignKey("products.id", ondelete="CASCADE"),
        nullable=False
    )

    image_url: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    alt_text: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True
    )

    sort_order: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        server_default="0"
    )

    is_main: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default="FALSE"
    )

    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=func.now()
    )
    product: Mapped["Product"] = relationship(
        "Product",
        back_populates="images"
    )

    __table_args__ = (
        Index(
            "one_main_image_per_product",
            "product_id",
            unique=True,
            postgresql_where=(is_main.is_(True))
        ),
    )