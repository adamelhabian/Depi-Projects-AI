from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy import ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class Secretary(Base):
    __tablename__ = "secretaries"

    # The profile's PK is also an FK to users.id.
    id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
    )

    teacher_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("teachers.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    permissions: Mapped[dict[str, Any]] = mapped_column(
        JSON, default=dict, nullable=False
    )

    user: Mapped["User"] = relationship(
        back_populates="secretary_profile",
        uselist=False,
    )

    teacher: Mapped["Teacher"] = relationship(
        back_populates="secretaries",
    )
