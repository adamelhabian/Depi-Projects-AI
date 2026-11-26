from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    DateTime,
    Enum as SQLAlchemyEnum,
    ForeignKey,
    Numeric,
    String,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.models.enums import ExamType


class Exam(Base):
    __tablename__ = "exams"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
    )

    title: Mapped[str] = mapped_column(String(150), nullable=False)

    exam_type: Mapped[ExamType] = mapped_column(
        SQLAlchemyEnum(ExamType, native_enum=False),
        nullable=False,
    )

    exam_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )

    total_marks: Mapped[Decimal] = mapped_column(
        Numeric(10, 2), nullable=False
    )

    study_group_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("study_groups.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    study_group: Mapped["StudyGroup"] = relationship(
        back_populates="exams",
    )

    grade_records: Mapped[list["GradeRecord"]] = relationship(
        back_populates="exam",
        cascade="all, delete-orphan",
    )
