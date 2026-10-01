from sqlalchemy import CheckConstraint, JSON, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class SiteAbout(Base):
    __tablename__ = "site_about"
    __table_args__ = (CheckConstraint("id = 1", name="single_site_about"),)

    id: Mapped[int] = mapped_column(primary_key=True, default=1)
    title: Mapped[str] = mapped_column(String(200))
    blocks: Mapped[list] = mapped_column(JSON)
