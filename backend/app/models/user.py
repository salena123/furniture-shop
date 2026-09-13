from datetime import datetime
from sqlalchemy import String, Text, TIMESTAMP, Enum, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base
class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    login: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    password_hash: Mapped[str] = mapped_column(Text, nullable=False)
    role: Mapped[str] = mapped_column(Enum('admin', 'manager', name='user_role'), nullable=False)
    last_login_at: Mapped[datetime | None] = mapped_column(
        TIMESTAMP(timezone=True),
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
    requests: Mapped[list["FurnitureRequest"]] = relationship(
        "FurnitureRequest",
        back_populates="assigned_manager"
    )
    request_events: Mapped[list["RequestEvent"]] = relationship(
        "RequestEvent",
        back_populates="user"
    )
    comments: Mapped[list["FurnitureComment"]] = relationship(
        "FurnitureComment",
        back_populates="user"
    )