from sqlalchemy import Boolean, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Category(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(primary_key=True)

    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    parent_id: Mapped[int | None] = mapped_column(
        ForeignKey("categories.id"),
        nullable=True
    )

    slug: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        unique=True
    )

    image_url: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    meta_title: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True
    )

    meta_description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    sort_order: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        server_default="0"
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default="TRUE"
    )

    parent: Mapped["Category | None"] = relationship(
        "Category",
        back_populates="children",
        remote_side=[id]
    )

    children: Mapped[list["Category"]] = relationship(
        "Category",
        back_populates="parent"
    )

    products: Mapped[list["Product"]] = relationship(
        "Product",
        back_populates="category"
    )