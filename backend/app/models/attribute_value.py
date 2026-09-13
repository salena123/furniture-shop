from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class AttributeValue(Base):
    __tablename__ = "attribute_values"

    id: Mapped[int] = mapped_column(primary_key=True)

    attribute_id: Mapped[int] = mapped_column(
        ForeignKey("attributes.id", ondelete="CASCADE"),
        nullable=False
    )

    value: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    sort_order: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        server_default="0"
    )

    attribute: Mapped["Attribute"] = relationship(
        "Attribute",
        back_populates="values"
    )

    product_attributes: Mapped[list["ProductAttribute"]] = relationship(
        "ProductAttribute",
        back_populates="attribute_value",
        cascade="all, delete-orphan"
    )