from datetime import datetime
from sqlalchemy import String, Text, TIMESTAMP, Integer, Boolean, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base

class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True)
    product_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    slug: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        unique=True,
    )
    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )
    short_description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )
    article: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True
    )
    category_id: Mapped[int] = mapped_column(
        ForeignKey("categories.id"),
        nullable=False,
        index=True,
    )
    material_id: Mapped[int | None] = mapped_column(
        ForeignKey("materials.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    price: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
    material: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True
    )
    is_custom: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default="TRUE",
        index=True
    )
    sort_order: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        server_default="0"
    )
    dimensions: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True
    )
    color: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True
    )
    meta_title: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True
    )
    meta_description: Mapped[str | None] = mapped_column(
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
    category: Mapped["Category"] = relationship(
        "Category",
        back_populates="products"
    )
    material_ref: Mapped["Material | None"] = relationship(
        "Material",
        back_populates="products"
    )
    images: Mapped[list["ProductImage"]] = relationship(
        "ProductImage",
        back_populates="product",
        cascade="all, delete-orphan"
    )
    product_attributes: Mapped[list["ProductAttribute"]] = relationship(
        "ProductAttribute",
        back_populates="product",
        cascade="all, delete-orphan"
    )
    furniture_requests: Mapped[list["FurnitureRequest"]] = relationship(
        "FurnitureRequest",
        back_populates="product"
    )
