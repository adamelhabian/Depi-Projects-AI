from sqlalchemy import Column, ForeignKey, Table

from app.database.base import Base


group_student = Table(
    "group_students",
    Base.metadata,
    Column(
        "group_id",
        ForeignKey("study_groups.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "student_id",
        ForeignKey("students.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)
