"""Build provisional grades using authoritative rubric weights and solutions."""

from decimal import Decimal, ROUND_HALF_UP
from typing import Annotated, Literal

from pydantic import Field, StringConstraints, model_validator

from src.ai_automation.automation_config import Assignment, AssignmentCode, Contract, Identifier, TelegramID

ArabicFeedback = Annotated[str, StringConstraints(strip_whitespace=True, max_length=700)]


class HomeworkSource(Contract):
    telegram_user_id: TelegramID
    message_id: int = Field(gt=0, le=2**31 - 1, strict=True)
    assignment_code: AssignmentCode

    @property
    def submission_id(self) -> str:
        return f"telegram:{self.telegram_user_id}:{self.message_id}"


class QuestionEvaluation(Contract):
    question_id: Identifier
    status: Literal["scored", "unanswered", "unreadable"]
    earned_score: float = Field(ge=0, le=100, strict=True)
    student_answer: ArabicFeedback
    explanation_ar: ArabicFeedback

    @model_validator(mode="after")
    def validate_evidence(self):
        if self.status != "scored" and self.earned_score:
            raise ValueError("Only scored answers can earn points")
        if self.status == "scored" and not self.student_answer:
            raise ValueError("A scored answer requires readable evidence")
        return self


class HomeworkResult(Contract):
    questions: list[QuestionEvaluation] = Field(min_length=1, max_length=20)
    feedback_ar: ArabicFeedback


class HomeworkSubmission(HomeworkSource):
    rubric_version: Identifier
    model: Identifier
    result: HomeworkResult


def validate_homework_payload(submission: HomeworkSubmission, student_id: str, rubric: Assignment) -> dict:
    if submission.rubric_version != rubric.version:
        raise ValueError("Rubric changed while the submission was being graded")
    evaluations = {item.question_id: item for item in submission.result.questions}
    if len(evaluations) != len(submission.result.questions) or evaluations.keys() != {
        question.question_id for question in rubric.questions
    }:
        raise ValueError("Grading output must cover each rubric question exactly once")

    questions = []
    points = Decimal(0)
    maximum = Decimal(0)
    needs_review = False
    for question in rubric.questions:
        evaluation = evaluations[question.question_id]
        if evaluation.earned_score > question.max_score:
            raise ValueError(f"Earned score exceeds the rubric limit for {question.question_id}")
        unreadable = evaluation.status == "unreadable"
        needs_review |= unreadable
        points += Decimal(str(evaluation.earned_score))
        maximum += Decimal(str(question.max_score))
        detail = evaluation.model_dump()
        detail.update(max_score=question.max_score, correct_solution_ar=question.correct_solution_ar)
        if unreadable:
            detail["earned_score"] = None
        questions.append(detail)

    percentage = (points / maximum * 100).quantize(Decimal("0.1"), rounding=ROUND_HALF_UP)
    return {
        "submission_id": submission.submission_id,
        "student_id": student_id,
        "assignment_code": submission.assignment_code,
        "rubric_version": rubric.version,
        "model": submission.model,
        "status": "needs_review" if needs_review else "provisional",
        "score": None if needs_review else float(points),
        "max_score": float(maximum),
        "percentage": None if needs_review else float(percentage),
        "passed": None if needs_review else points * 100 >= maximum * Decimal(str(rubric.pass_percentage)),
        "questions": questions,
        "feedback_ar": submission.result.feedback_ar,
    }


def format_telegram_feedback(grade: dict) -> list[str]:
    title = f"تصحيح {grade['assignment_code']}"
    if grade["status"] == "needs_review":
        unreadable = "، ".join(q["question_id"] for q in grade["questions"] if q["status"] == "unreadable")
        return [f"{title}\nتعذّر قراءة بعض الإجابات ({unreadable}). أرسل صورة أوضح للورقة كاملة بنفس كود التكليف."]

    sections = [
        f"{title}\nالدرجة المبدئية: {grade['score']:g} من {grade['max_score']:g} ({grade['percentage']:g}%)"
        "\nالتصحيح آلي ويمكن للمعلم مراجعته."
    ]
    for question in grade["questions"]:
        lines = [f"السؤال {question['question_id']} — {question['earned_score']:g} من {question['max_score']:g}"]
        if question["student_answer"]:
            lines.append(f"إجابتك: {question['student_answer']}")
        if question["explanation_ar"]:
            lines.append(f"الملاحظة: {question['explanation_ar']}")
        lines.append(f"الحل النموذجي:\n{question['correct_solution_ar']}")
        sections.append("\n".join(lines))
    if grade["feedback_ar"]:
        sections.append(f"للمراجعة:\n{grade['feedback_ar']}")

    messages = [sections[0]]
    for section in sections[1:]:
        candidate = f"{messages[-1]}\n\n{section}"
        if len(candidate.encode("utf-16-le", errors="replace")) <= 7600:
            messages[-1] = candidate
        else:
            prefix = f"{title} (متابعة)\n\n"
            # A Unicode scalar uses at most two UTF-16 units.
            if len((prefix + section).encode("utf-16-le", errors="replace")) > 7600:
                for index in range(0, len(section), 1800):
                    messages.append(prefix + section[index:index + 1800])
            else:
                messages.append(prefix + section)
    return messages
