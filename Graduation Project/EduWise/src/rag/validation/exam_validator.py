# Validate generated questions
from dataclasses import dataclass


QUESTION_STARTERS_FOR_TF = (
    "which of the following",
    "what is",
    "what are",
    "how does",
    "how do",
    "why is",
    "why are",
    "who is",
    "describe",
    "explain",
    "identify",
)


@dataclass
class ValidationResult:
    valid_questions: list[dict]
    dropped_reasons: list[str]


def validate_questions(
    questions: list[dict],
    q_type: str,
) -> ValidationResult:
    valid: list[dict] = []
    dropped: list[str] = []

    for q in questions:
        if not isinstance(q, dict):
            dropped.append("Question must be a dictionary.")
            continue

        question_text = str(q.get("question", "")).strip()
        answer_text = str(q.get("answer", "")).strip()

        if not question_text or not answer_text:
            dropped.append("Empty question or answer field.")
            continue

        if q_type == "MCQ":
            options = q.get("options")
            required_keys = ("A", "B", "C", "D")

            if not isinstance(options, dict):
                dropped.append("Malformed MCQ: invalid options.")
                continue

            if not all(
                isinstance(options.get(key), str)
                and options[key].strip()
                for key in required_keys
            ):
                dropped.append("Malformed MCQ: missing or empty options.")
                continue

            if not any(
                answer_text.startswith(f"{key} -")
                for key in required_keys
            ):
                dropped.append("Malformed MCQ: invalid answer format.")
                continue

            valid.append(q)

        elif q_type == "True/False":
            lower_ans = answer_text.lower()
            is_valid_answer = (
                lower_ans.startswith("true")
                or lower_ans.startswith("false")
            )

            lower_q = question_text.lower()
            is_question_form = any(
                phrase in lower_q
                for phrase in QUESTION_STARTERS_FOR_TF
            )

            if is_valid_answer and not is_question_form:
                valid.append(q)
            else:
                dropped.append(
                    f"Malformed True/False question: {question_text[:60]}"
                )

        elif q_type == "Fill in the Blanks":
            if "______" in question_text:
                valid.append(q)
            else:
                dropped.append(
                    f"Malformed Fill-in-the-Blank: {question_text[:60]}"
                )

        else:
            valid.append(q)

    return ValidationResult(
        valid_questions=valid,
        dropped_reasons=dropped,
    )