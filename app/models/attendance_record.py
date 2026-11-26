from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    DateTime,
    Enum as SQLAlchemyEnum,
    Text,
    ForeignKey,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.models.enums import AttendanceStatus


class AttendanceRecord(Base):
    __tablename__ = "attendance_records"

    __table_args__ = (
        UniqueConstraint(
            "student_id",
            "lesson_session_id",
            name="uq_student_session_attendance",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
    )

    student_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("students.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    lesson_session_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("lesson_sessions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    status: Mapped[AttendanceStatus] = mapped_column(
        SQLAlchemyEnum(AttendanceStatus, native_enum=False),
        default=AttendanceStatus.PRESENT,
        nullable=False,
    )

    behavior_note: Mapped[str | None] = mapped_column(
        Text, nullable=True
    )

    recorded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    student: Mapped["Student"] = relationship(
        back_populates="attendance_records",
    )

    lesson_session: Mapped["LessonSession"] = relationship(
        back_populates="attendance_records",
    )
