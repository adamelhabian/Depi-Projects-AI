from __future__ import annotations

import uuid

from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class Student(Base):
    __tablename__ = "students"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
    )

    full_name: Mapped[str] = mapped_column(String(150), nullable=False)

    phone: Mapped[str | None] = mapped_column(String(20), nullable=True)

    school_grade: Mapped[str | None] = mapped_column(
        String(150), nullable=True
    )

    parent_name: Mapped[str | None] = mapped_column(
        String(150), nullable=True
    )

    parent_phone: Mapped[str | None] = mapped_column(
        String(20), nullable=True
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean, default=True, nullable=False
    )

    # No fee_policy_id here: Student <-> FeePolicy is many-to-many
    # through StudentFeePolicy.

    teachers: Mapped[list["Teacher"]] = relationship(
        secondary="teacher_students",
        back_populates="students",
    )

    study_groups: Mapped[list["StudyGroup"]] = relationship(
        secondary="group_students",
        back_populates="students",
    )

    attendance_records: Mapped[list["AttendanceRecord"]] = relationship(
        back_populates="student",
        cascade="all, delete-orphan",
    )

    grade_records: Mapped[list["GradeRecord"]] = relationship(
        back_populates="student",
        cascade="all, delete-orphan",
    )

    payment_transactions: Mapped[list["PaymentTransaction"]] = relationship(
        back_populates="student",
    )

    fee_policy_assignments: Mapped[list["StudentFeePolicy"]] = relationship(
        back_populates="student",
        cascade="all, delete-orphan",
    )
