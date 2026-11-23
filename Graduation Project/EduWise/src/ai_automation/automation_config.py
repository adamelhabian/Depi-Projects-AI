"""Trusted roster and rubric snapshot managed by EduWise staff."""

import os
from pathlib import Path
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, StringConstraints, field_validator, model_validator

from src.config.settings import PROJECT_ROOT

Identifier = Annotated[str, StringConstraints(pattern=r"^[A-Za-z0-9][A-Za-z0-9_.:-]{0,79}$")]
AssignmentCode = Annotated[str, StringConstraints(pattern=r"^[A-Z][A-Z0-9]*(?:-[A-Z0-9]+)+$", max_length=48)]
TelegramID = Annotated[str, StringConstraints(pattern=r"^[1-9][0-9]{0,15}$")]
ShortText = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=150)]
Solution = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=1400)]


class Contract(BaseModel):
    model_config = ConfigDict(extra="forbid", allow_inf_nan=False)


class Student(Contract):
    student_name: ShortText
    guardian_name: ShortText = "ولي الأمر"
    guardian_chat_id: TelegramID | None = None
    student_telegram_id: TelegramID | None = None
    assignments: set[AssignmentCode] = Field(default_factory=set)
    materials_url: HttpUrl | None = None
    makeup_slots_ar: list[ShortText] = Field(default_factory=list, max_length=3)

    @field_validator("materials_url")
    @classmethod
    def validate_materials_url(cls, url):
        if url and (url.scheme != "https" or url.username or url.password or len(str(url)) > 350):
            raise ValueError("Use a short HTTPS materials URL without embedded credentials")
        return url


class Question(Contract):
    question_id: Identifier
    max_score: float = Field(ge=0.01, le=100, strict=True)
    grading_criteria: Solution
    correct_solution_ar: Solution


class Assignment(Contract):
    version: Identifier
    pass_percentage: float = Field(default=60, ge=0, le=100, strict=True)
    questions: list[Question] = Field(min_length=1, max_length=20)

    @model_validator(mode="after")
    def validate_questions(self):
        if len({question.question_id for question in self.questions}) != len(self.questions):
            raise ValueError("Question IDs must be unique")
        return self


class AutomationConfig(Contract):
    students: dict[Identifier, Student]
    assignments: dict[AssignmentCode, Assignment]

    @model_validator(mode="after")
    def validate_roster(self):
        linked = [student.student_telegram_id for student in self.students.values() if student.student_telegram_id]
        if len(linked) != len(set(linked)):
            raise ValueError("A student Telegram account may be linked to only one student")
        if any(student.assignments - self.assignments.keys() for student in self.students.values()):
            raise ValueError("Each assigned code must have a rubric")
        return self


def load_automation_config() -> AutomationConfig:
    path = Path(os.getenv("EDUWISE_AUTOMATION_CONFIG") or PROJECT_ROOT / "var" / "automation.json")
    return AutomationConfig.model_validate_json(path.read_text(encoding="utf-8-sig"))
