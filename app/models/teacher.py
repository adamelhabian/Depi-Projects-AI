from __future__ import annotations

import uuid

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class Teacher(Base):
    __tablename__ = "teachers"

    # The profile's PK is also an FK to users.id.
    id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
    )

    specialization: Mapped[str | None] = mapped_column(
        String(100), nullable=True
    )

    user: Mapped["User"] = relationship(
        back_populates="teacher_profile",
        uselist=False,
    )

    secretaries: Mapped[list["Secretary"]] = relationship(
        back_populates="teacher",
    )

    students: Mapped[list["Student"]] = relationship(
        secondary="teacher_students",
        back_populates="teachers",
    )

    study_groups: Mapped[list["StudyGroup"]] = relationship(
        back_populates="teacher",
    )

    fee_policies: Mapped[list["FeePolicy"]] = relationship(
        back_populates="teacher",
    )
