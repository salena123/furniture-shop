from sqlalchemy import CheckConstraint, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class SiteContacts(Base):
    __tablename__ = "site_contacts"
    __table_args__ = (CheckConstraint("id = 1", name="single_site_contacts"),)

    id: Mapped[int] = mapped_column(primary_key=True, default=1)
    phone: Mapped[str | None] = mapped_column(String(50), nullable=True)
    address: Mapped[str | None] = mapped_column(String(500), nullable=True)
    hours: Mapped[str | None] = mapped_column(String(300), nullable=True)
    email: Mapped[str | None] = mapped_column(String(254), nullable=True)
