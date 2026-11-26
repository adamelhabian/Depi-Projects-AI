from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class StudyGroup(Base):
    __tablename__ = "study_groups"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
    )

    name: Mapped[str] = mapped_column(String(100), nullable=False)

    description: Mapped[str | None] = mapped_column(
        String(500), nullable=True
    )

    grade_level: Mapped[str] = mapped_column(
        String(100), nullable=False
    )

    subject: Mapped[str] = mapped_column(
        String(100), nullable=False
    )

    max_students: Mapped[int] = mapped_column(
        Integer, nullable=False
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean, default=True, nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    teacher_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("teachers.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    teacher: Mapped["Teacher"] = relationship(
        back_populates="study_groups",
    )

    students: Mapped[list["Student"]] = relationship(
        secondary="group_students",
        back_populates="study_groups",
    )

    lesson_sessions: Mapped[list["LessonSession"]] = relationship(
        back_populates="study_group",
        cascade="all, delete-orphan",
    )

    homework_assignments: Mapped[list["HomeworkAssignment"]] = relationship(
        back_populates="study_group",
        cascade="all, delete-orphan",
    )

    exams: Mapped[list["Exam"]] = relationship(
        back_populates="study_group",
        cascade="all, delete-orphan",
    )
