from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class ProductAttribute(Base):
    __tablename__ = "product_attributes"

    product_id: Mapped[int] = mapped_column(
        ForeignKey("products.id", ondelete="CASCADE"),
        primary_key=True
    )

    attribute_value_id: Mapped[int] = mapped_column(
        ForeignKey("attribute_values.id", ondelete="CASCADE"),
        primary_key=True
    )
    attribute_value: Mapped["AttributeValue"] = relationship(
        "AttributeValue",
        back_populates="product_attributes"
    )
    product: Mapped["Product"] = relationship(
        "Product",
        back_populates="product_attributes"
    )