from enum import Enum


class UserRole(str, Enum):
    ADMIN = "ADMIN"
    TEACHER = "TEACHER"
    SECRETARY = "SECRETARY"


class StudentStatus(str, Enum):
    ACTIVE = "ACTIVE"
    ARCHIVED = "ARCHIVED"


class AttendanceStatus(str, Enum):
    PRESENT = "PRESENT"
    ABSENT = "ABSENT"
    LATE = "LATE"


class SessionStatus(str, Enum):
    SCHEDULED = "SCHEDULED"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


class HomeworkStatus(str, Enum):
    SUBMITTED = "SUBMITTED"
    NOT_SUBMITTED = "NOT_SUBMITTED"
    LATE = "LATE"


class PaymentStatus(str, Enum):
    PAID = "PAID"
    PENDING = "PENDING"
    CANCELLED = "CANCELLED"


class PaymentMethod(str, Enum):
    CASH = "CASH"
    CARD = "CARD"
    TRANSFER = "TRANSFER"


class ExamType(str, Enum):
    QUIZ = "QUIZ"
    MONTHLY = "MONTHLY"
    FINAL = "FINAL"


class FeePolicyType(str, Enum):
    MONTHLY = "MONTHLY"
    PER_SESSION = "PER_SESSION"
    PER_TERM = "PER_TERM"
    ONE_TIME = "ONE_TIME"
