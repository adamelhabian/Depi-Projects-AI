# Exam generation prompts

DIFFICULTY_INSTRUCTIONS: dict[str, str] = {
    "Normal": (
        "Generate RECALL-LEVEL questions (Bloom's Taxonomy Level 1-2). "
        "Focus on direct facts, definitions, and basic comprehension from the text. "
        "A student who read the material once should answer correctly."
    ),
    "Difficult": (
        "Generate APPLICATION and ANALYSIS questions (Bloom's Taxonomy Level 3-4). "
        "Ask students to apply concepts, compare mechanisms, explain processes, "
        "and reason about cause-effect relationships. Requires thorough understanding."
    ),
    "Nightmare": (
        "Generate SYNTHESIS and EVALUATION questions (Bloom's Taxonomy Level 5-6). "
        "Require multi-step reasoning, cross-concept connections, critical judgment, "
        "and the ability to construct new arguments from the material. "
        "Only top-performing students should answer correctly."
    ),
}

QUESTION_TYPE_FORMATS: dict[str, str] = {
    "MCQ": (
    "Generate {n} multiple choice questions. "
    "Each question MUST have exactly 4 options labeled A, B, C, D. "
    "Only one option is correct. Make distractors plausible but clearly wrong. "
    "EVERY question must include the options field. "
    "The answer field MUST contain the correct option letter and its full text, "
    "formatted exactly as 'A - Correct answer text'."
    ),
    "True/False": (
        "Generate {n} True/False questions. "
        "Each question MUST be a statement that is clearly either True or False. "
        "Do NOT generate open-ended questions. "
        "The answer field MUST start with either 'True' or 'False'. "
        "Include a one-sentence justification after True/False in the answer field."
    ),
    "Short Answer": (
        "Generate {n} short answer questions requiring 2-3 sentence responses. "
        "Questions should start with: What, How, Why, Describe, or Identify."
    ),
    "Fill in the Blanks": (
        "Generate {n} fill-in-the-blank sentences from the context material. "
        "Use exactly one blank per sentence represented by '______'. "
        "The blank should replace a key term, concept, or value. "
        "The question MUST be a sentence with a blank, NOT an open-ended question."
    ),
    "Descriptive": (
        "Generate {n} descriptive questions requiring a full paragraph answer. "
        "Questions must start with: Explain, Discuss, Analyze, Evaluate, or Compare."
    ),
}

DEFAULT_MARKS_PER_TYPE: dict[str, int] = {
    "MCQ": 1,
    "True/False": 1,
    "Short Answer": 3,
    "Fill in the Blanks": 1,
    "Descriptive": 5,
}


def build_generation_prompts(
    context: str,
    q_type: str,
    difficulty: str,
    count: int,
    marks: int,
) -> tuple[str, str]:
    if difficulty not in DIFFICULTY_INSTRUCTIONS:
        raise ValueError(f"Unsupported difficulty '{difficulty}'. Choose from {list(DIFFICULTY_INSTRUCTIONS)}")
    if q_type not in QUESTION_TYPE_FORMATS:
        raise ValueError(f"Unsupported question type '{q_type}'. Choose from {list(QUESTION_TYPE_FORMATS)}")

    difficulty_instr = DIFFICULTY_INSTRUCTIONS[difficulty]
    type_instr = QUESTION_TYPE_FORMATS[q_type].format(n=count)

    options_note = (
        '"options": {"A": "...", "B": "...", "C": "...", "D": "..."},'
        if q_type == "MCQ"
        else ""
    )

    system_prompt = f"""You are an expert university exam paper designer with 20 years of experience.

DIFFICULTY REQUIREMENT:
{difficulty_instr}

QUESTION TYPE REQUIREMENT:
{type_instr}

CRITICAL OUTPUT RULE:
Return ONLY a valid JSON object. No markdown formatting, no explanation, no preamble.
Exactly this structure:
{{
  "questions": [
    {{
      "question": "the question text here",
      {options_note}
      "answer": "the correct answer here",
      "marks": {marks}
    }}
  ]
}}

For non-MCQ types, do NOT include the options field.
Generate exactly {count} questions. All questions must be directly answerable from the context.
The marks field must always be {marks}. Do not change it."""

    user_prompt = f"Generate questions based ONLY on the following context:\n\n{context}"
    return system_prompt, user_prompt