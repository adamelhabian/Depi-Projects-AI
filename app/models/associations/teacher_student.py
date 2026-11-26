from sqlalchemy import Column, ForeignKey, Table

from app.database.base import Base


teacher_student = Table(
    "teacher_students",
    Base.metadata,
    Column(
        "teacher_id",
        ForeignKey("teachers.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "student_id",
        ForeignKey("students.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)
