from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    Enum as SQLAlchemyEnum,
    ForeignKey,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.models.enums import SessionStatus


class LessonSession(Base):
    __tablename__ = "lesson_sessions"

    __table_args__ = (
        CheckConstraint(
            "end_time > start_time",
            name="ck_lesson_session_end_after_start",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
    )

    title: Mapped[str] = mapped_column(String(150), nullable=False)

    # start_time and end_time include both date and time;
    # a separate session_date would duplicate this information.
    start_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )

    end_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )

    topic: Mapped[str | None] = mapped_column(Text, nullable=True)

    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    status: Mapped[SessionStatus] = mapped_column(
        SQLAlchemyEnum(SessionStatus, native_enum=False),
        default=SessionStatus.SCHEDULED,
        nullable=False,
    )

    study_group_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("study_groups.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    study_group: Mapped["StudyGroup"] = relationship(
        back_populates="lesson_sessions",
    )

    attendance_records: Mapped[list["AttendanceRecord"]] = relationship(
        back_populates="lesson_session",
        cascade="all, delete-orphan",
    )
