# Generate exam questions
import json
import logging
import re

from rag.generation.llm_client import GroqLLMClient
from rag.generation.prompt import (
    DEFAULT_MARKS_PER_TYPE,
    build_generation_prompts,
)
from rag.validation.exam_validator import validate_questions


logger = logging.getLogger(__name__)


def _strip_markdown_fences(raw_text: str) -> str:
    cleaned = raw_text.strip()

    if cleaned.startswith("```"):
        lines = cleaned.splitlines()
        lines = lines[1:]

        if lines and lines[-1].strip().startswith("```"):
            lines = lines[:-1]

        cleaned = "\n".join(lines)

    return cleaned.strip()


def _normalize_question(question: str) -> str:
    return re.sub(r"\s+", " ", question.strip().lower())


class ExamGenerator:
    def __init__(
        self,
        llm_client: GroqLLMClient,
        marks_per_type: dict[str, int] | None = None,
        max_retries: int = 2,
    ) -> None:
        if max_retries < 0:
            raise ValueError("max_retries cannot be negative.")

        self.llm_client = llm_client
        self.marks_per_type = (
            marks_per_type
            if marks_per_type is not None
            else DEFAULT_MARKS_PER_TYPE.copy()
        )
        self.max_retries = max_retries

    def generate_for_type(
        self,
        context: str,
        q_type: str,
        difficulty: str,
        count: int,
    ) -> dict[str, list[dict]]:

        if not context or not context.strip():
            raise ValueError("Context cannot be empty.")

        if count <= 0:
            raise ValueError("Question count must be positive.")

        correct_marks = self.marks_per_type.get(q_type, 2)

        all_valid: list[dict] = []
        seen_questions: set[str] = set()

        for attempt in range(self.max_retries + 1):

            if len(all_valid) >= count:
                break

            needed = count - len(all_valid)

            system_prompt, user_prompt = build_generation_prompts(
                context=context,
                q_type=q_type,
                difficulty=difficulty,
                count=needed,
                marks=correct_marks,
            )

            try:
                raw_response = self.llm_client.generate_json_response(
                    system_prompt=system_prompt,
                    user_prompt=user_prompt,
                )

                parsed = json.loads(
                    _strip_markdown_fences(raw_response)
                )

                if not isinstance(parsed, dict):
                    raise ValueError("LLM response must be a JSON object.")

                batch = parsed.get("questions", [])

                if not isinstance(batch, list):
                    raise ValueError("'questions' must be a JSON array.")

                prepared_batch = []

                for item in batch:
                    if not isinstance(item, dict):
                        continue

                    item = item.copy()
                    item["marks"] = correct_marks

                    if q_type != "MCQ":
                        item.pop("options", None)

                    prepared_batch.append(item)

                validation = validate_questions(
                    prepared_batch,
                    q_type=q_type,
                )

                for question in validation.valid_questions:
                    normalized = _normalize_question(
                        question.get("question", "")
                    )

                    if not normalized or normalized in seen_questions:
                        continue

                    seen_questions.add(normalized)
                    all_valid.append(question)

                    if len(all_valid) >= count:
                        break

                if validation.dropped_reasons:
                    logger.warning(
                        "Attempt %s: %s questions rejected.",
                        attempt + 1,
                        len(validation.dropped_reasons),
                    )

            except (json.JSONDecodeError, ValueError):
                logger.exception(
                    "Invalid LLM response on attempt %s.",
                    attempt + 1,
                )

            except Exception:
                logger.exception(
                    "Exam generation failed on attempt %s.",
                    attempt + 1,
                )

        if len(all_valid) < count:
            logger.warning(
                "Generated %s out of %s requested questions.",
                len(all_valid),
                count,
            )

        return {"questions": all_valid[:count]}