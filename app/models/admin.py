
# app/models/admin.py

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.user import User
from app.models.enums import UserRole


class Admin(User):

    __tablename__ = "admins"

    role: Mapped[str] = mapped_column(
        String(20),
        default=UserRole.ADMIN.value,
        nullable=False
    )
