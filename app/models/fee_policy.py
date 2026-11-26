from __future__ import annotations

import uuid
from decimal import Decimal

from sqlalchemy import Enum as SQLAlchemyEnum, ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.models.enums import FeePolicyType


class FeePolicy(Base):
    __tablename__ = "fee_policies"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
    )

    name: Mapped[str] = mapped_column(String(100), nullable=False)

    policy_type: Mapped[FeePolicyType] = mapped_column(
        SQLAlchemyEnum(FeePolicyType, native_enum=False),
        nullable=False,
    )

    amount: Mapped[Decimal] = mapped_column(
        Numeric(10, 2), nullable=False
    )

    description: Mapped[str | None] = mapped_column(
        String(500), nullable=True
    )

    teacher_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("teachers.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    teacher: Mapped["Teacher"] = relationship(
        back_populates="fee_policies",
    )

    student_assignments: Mapped[list["StudentFeePolicy"]] = relationship(
        back_populates="fee_policy",
        cascade="all, delete-orphan",
    )
