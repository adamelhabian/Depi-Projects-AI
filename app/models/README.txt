# Revised SQLAlchemy Models

Copy the `models/` package into `app/models/`.

Important:
1. This package expects `Base` at `app.database.base`.
2. Remove the old `app/models/admin.py`; Admin is represented by `User(role=UserRole.ADMIN)`.
3. The `User`, `Teacher`, and `Secretary` design uses profile tables (composition), not ORM inheritance.
4. `LessonSession.start_time` and `end_time` are timezone-aware DateTime columns. The redundant `session_date` column was removed.
5. `GradeRecord` now supports either an Exam OR a HomeworkAssignment. Exactly one FK must be set.
6. `StudentFeePolicy` has no unique(student_id, fee_policy_id) constraint so historical re-assignments can be recorded. Prevent duplicate active assignments in the service layer.
7. Update Alembic `target_metadata` to `Base.metadata`, and import `app.models` before autogeneration.
8. Review deletion policies against your retention requirements before production.
