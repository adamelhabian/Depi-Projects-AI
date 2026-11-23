# Generation evaluation

import textstat





def _extract_sections(results: dict) -> dict[str, list[dict]]:
    """
    Normalizes either {"sections": {"MCQ": [...]}} or {"MCQ": {"questions": [...]}}
    into {"MCQ": [...]}.
    """
    if "sections" in results and isinstance(results["sections"], dict):
        return results["sections"]

    normalized: dict[str, list[dict]] = {}
    for sec_name, data in results.items():
        if isinstance(data, dict) and isinstance(data.get("questions"), list):
            normalized[sec_name] = data["questions"]
        elif isinstance(data, list):
            normalized[sec_name] = data
    return normalized




def measure_complexity(results: dict) -> dict[str, float | int]:
    """
    Computes Flesch-Kincaid Grade Level and Flesch Reading Ease across
    all generated questions.
    """
    sections = _extract_sections(results)
    all_questions: list[str] = []

    for questions in sections.values():
        for q in questions:
            q_text = str(q.get("question", "")).strip()
            if q_text:
                all_questions.append(q_text)

    if not all_questions:
        return {
            "flesch_kincaid_grade": 0.0,
            "flesch_reading_ease": 0.0,
            "questions_analyzed": 0,
        }

    combined_text = " ".join(all_questions)
    return {
        "flesch_kincaid_grade": round(float(textstat.flesch_kincaid_grade(combined_text)), 2),
        "flesch_reading_ease": round(float(textstat.flesch_reading_ease(combined_text)), 2),
        "questions_analyzed": len(all_questions),
    }