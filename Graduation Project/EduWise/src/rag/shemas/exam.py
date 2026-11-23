# Exam and question models

from dataclasses import dataclass, field
from typing import Optional

@dataclass
class QuestionItem:
    question: str
    answer: str
    marks: int
    # answers options if it mcq
    options: Optional[dict[str, str]] = None

# group of same type questions
@dataclass
class ExamSection:
    q_type: str
    questions: list[QuestionItem] = field(default_factory=list)

@dataclass
class ExamPaperResult:
    subject: str
    source_file: str
    difficulty: str
    sections: dict[str, list[QuestionItem]] = field(default_factory=dict)