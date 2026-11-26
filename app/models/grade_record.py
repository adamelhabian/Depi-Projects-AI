from __future__ import annotations

import uuid
from decimal import Decimal

from sqlalchemy import (
    CheckConstraint,
    ForeignKey,
    Numeric,
    String,
    UniqueConstraint,
    Enum as SQLAlchemyEnum,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.models.enums import HomeworkStatus


class GradeRecord(Base):
    __tablename__ = "grade_records"

    __table_args__ = (
        UniqueConstraint(
            "student_id", "exam_id",
            name="uq_student_exam_grade",
        ),
        UniqueConstraint(
            "student_id", "homework_id",
            name="uq_student_homework_grade",
        ),
        CheckConstraint(
            "(exam_id IS NOT NULL AND homework_id IS NULL) OR "
            "(exam_id IS NULL AND homework_id IS NOT NULL)",
            name="ck_grade_record_exactly_one_assessment",
        ),
        CheckConstraint(
            "marks_obtained >= 0",
            name="ck_grade_record_nonnegative_marks",
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

    exam_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("exams.id", ondelete="CASCADE"),
        nullable=True,
    )

    homework_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("homework_assignments.id", ondelete="CASCADE"),
        nullable=True,
    )

    marks_obtained: Mapped[Decimal] = mapped_column(
        Numeric(10, 2), nullable=False
    )

    homework_status: Mapped[HomeworkStatus | None] = mapped_column(
        SQLAlchemyEnum(HomeworkStatus, native_enum=False),
        nullable=True,
    )

    note: Mapped[str | None] = mapped_column(
        String(500), nullable=True
    )

    student: Mapped["Student"] = relationship(
        back_populates="grade_records",
    )

    exam: Mapped["Exam | None"] = relationship(
        back_populates="grade_records",
    )

    homework: Mapped["HomeworkAssignment | None"] = relationship(
        back_populates="grade_records",
    )
