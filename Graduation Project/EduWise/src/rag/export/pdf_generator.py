# Generate exam PDFs

from pathlib import Path
from xml.sax.saxutils import escape
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import HRFlowable, PageBreak, Paragraph, SimpleDocTemplate, Spacer

from rag.generation.prompt import DEFAULT_MARKS_PER_TYPE


def format_exam_paper(
    sections: dict[str, list[dict]],
    difficulty: str,
    subject: str = "Study Material",
    source_file: str = "",
    marks_per_type: dict[str, int] | None = None,
    model_name: str = "llama-3.1-8b-instant",
) -> str:
    """
    Formats generated exam sections and a detached answer key into plain text.
    """
    marks_map = marks_per_type or DEFAULT_MARKS_PER_TYPE
    lines: list[str] = []
    answer_key: list[str] = []

    lines.append("=" * 65)
    lines.append("                      EXAM PAPER")
    lines.append(f"  Subject     : {subject}")
    if source_file:
        lines.append(f"  Source File : {Path(source_file).name}")
    lines.append(f"  Difficulty  : {difficulty}")
    lines.append(f"  Generator   : AI Exam Paper Generator (RAG + Groq {model_name})")
    lines.append("  Note        : All questions are grounded in the uploaded document.")
    lines.append("=" * 65)

    answer_key.append("\n" + "=" * 65)
    answer_key.append("                       ANSWER KEY")
    answer_key.append("=" * 65)

    q_num = 1
    section_num = 1
    total_marks = 0

    for section_name, questions in sections.items():
        if not questions:
            lines.append(f"\n[Section {section_name}: No questions generated]")
            continue

        section_marks = sum(q.get("marks", marks_map.get(section_name, 2)) for q in questions)
        total_marks += section_marks

        lines.append(f"\n\nSection {section_num}: {section_name}")
        lines.append(
            "('1 mark each')"
            if section_marks == len(questions)
            else f"({section_marks} marks total)"
        )
        lines.append("-" * 65)

        answer_key.append(f"\nSection {section_num}: {section_name}")
        answer_key.append("-" * 40)

        for q in questions:
            marks = q.get("marks", marks_map.get(section_name, 2))
            lines.append(f"\nQ{q_num}. [{marks} mark{'s' if marks > 1 else ''}]")
            lines.append(f"    {q.get('question', 'Question text missing')}")

            options = q.get("options")
            if isinstance(options, dict):
                lines.append("")
                for opt_label, opt_text in options.items():
                    lines.append(f"      {opt_label})  {opt_text}")

            answer_key.append(f"Q{q_num}: {q.get('answer', 'N/A')}")
            q_num += 1

        section_num += 1

    lines.append("\n\n" + "=" * 65)
    lines.append(f"  TOTAL MARKS: {total_marks}")
    lines.append(f"  TOTAL QUESTIONS: {q_num - 1}")
    lines.append("=" * 65)

    lines.extend(answer_key)
    lines.append("\n" + "=" * 65)

    return "\n".join(lines)


def generate_pdf_exam(
    sections: dict[str, list[dict]],
    difficulty: str,
    subject: str,
    source_file: str,
    output_path: str | Path,
    marks_per_type: dict[str, int] | None = None,
) -> Path:
    """
    Generates a formatted A4 PDF exam paper with a detached answer key on the final page.
    """
    marks_map = marks_per_type or DEFAULT_MARKS_PER_TYPE
    out_file = Path(output_path)
    out_file.parent.mkdir(parents=True, exist_ok=True)

    doc = SimpleDocTemplate(
        str(out_file),
        pagesize=A4,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
        leftMargin=2 * cm,
        rightMargin=2 * cm,
    )

    styles = getSampleStyleSheet()

    style_title = ParagraphStyle(
        "ExamTitle",
        parent=styles["Normal"],
        fontSize=18,
        fontName="Helvetica-Bold",
        alignment=TA_CENTER,
        spaceAfter=6,
        textColor=colors.HexColor("#1a1a2e"),
    )
    style_subtitle = ParagraphStyle(
        "Subtitle",
        parent=styles["Normal"],
        fontSize=11,
        fontName="Helvetica",
        alignment=TA_CENTER,
        spaceAfter=4,
        textColor=colors.HexColor("#444444"),
    )
    style_section = ParagraphStyle(
        "SectionHead",
        parent=styles["Normal"],
        fontSize=13,
        fontName="Helvetica-Bold",
        spaceBefore=16,
        spaceAfter=6,
        textColor=colors.HexColor("#ffffff"),
        backColor=colors.HexColor("#1a1a2e"),
        leftIndent=-6,
        rightIndent=-6,
        borderPadding=(4, 6, 4, 6),
    )
    style_question = ParagraphStyle(
        "Question",
        parent=styles["Normal"],
        fontSize=10,
        fontName="Helvetica-Bold",
        spaceBefore=10,
        spaceAfter=3,
        textColor=colors.HexColor("#1a1a2e"),
        leading=14,
    )
    style_option = ParagraphStyle(
        "Option",
        parent=styles["Normal"],
        fontSize=10,
        fontName="Helvetica",
        leftIndent=20,
        spaceAfter=2,
        textColor=colors.HexColor("#333333"),
        leading=13,
    )
    style_answer_head = ParagraphStyle(
        "AnswerHead",
        parent=styles["Normal"],
        fontSize=13,
        fontName="Helvetica-Bold",
        spaceBefore=10,
        spaceAfter=6,
        textColor=colors.HexColor("#ffffff"),
        backColor=colors.HexColor("#c0392b"),
        leftIndent=-6,
        rightIndent=-6,
        borderPadding=(4, 6, 4, 6),
    )
    style_answer = ParagraphStyle(
        "AnswerText",
        parent=styles["Normal"],
        fontSize=10,
        fontName="Helvetica",
        spaceAfter=4,
        textColor=colors.HexColor("#1a1a2e"),
        leading=14,
    )
    badge_color = {
        "Normal": colors.HexColor("#27ae60"),
        "Difficult": colors.HexColor("#e67e22"),
        "Nightmare": colors.HexColor("#c0392b"),
    }.get(difficulty, colors.HexColor("#333333"))
    style_difficulty_badge = ParagraphStyle(
        "Badge",
        parent=styles["Normal"],
        fontSize=10,
        fontName="Helvetica-Bold",
        alignment=TA_CENTER,
        textColor=colors.HexColor("#ffffff"),
        backColor=badge_color,
        borderPadding=(3, 8, 3, 8),
        spaceAfter=10,
    )
    style_footer = ParagraphStyle(
        "Footer",
        parent=styles["Normal"],
        fontSize=11,
        fontName="Helvetica-Bold",
        alignment=TA_CENTER,
        textColor=colors.HexColor("#1a1a2e"),
    )

    story: list = []
    story.append(Spacer(1, 0.3 * cm))
    story.append(Paragraph("EXAM PAPER", style_title))
    story.append(Paragraph(escape(subject), style_subtitle))
    if source_file:
        story.append(Paragraph(f"Source: {escape(Path(source_file).name)}", style_subtitle))
    story.append(Spacer(1, 0.2 * cm))
    story.append(Paragraph(f"Difficulty Level: {escape(difficulty.upper())}", style_difficulty_badge))
    story.append(
        Paragraph("Generated by: AI Exam Paper Generator (RAG)", style_subtitle)
    )
    story.append(
        HRFlowable(width="100%", thickness=2, color=colors.HexColor("#1a1a2e"), spaceAfter=10)
    )

    answer_key_entries: list[tuple] = []
    q_num = 1
    section_num = 1
    total_marks = 0

    for section_name, questions in sections.items():
        if not questions:
            continue

        section_marks = sum(q.get("marks", marks_map.get(section_name, 2)) for q in questions)
        total_marks += section_marks

        story.append(
            Paragraph(
                f"  Section {section_num}: {escape(section_name)}  |  {section_marks} marks",
                style_section,
            )
        )
        answer_key_entries.append(("section", section_name, section_num))

        for q in questions:
            marks = q.get("marks", marks_map.get(section_name, 2))
            question_text = str(q.get("question", ""))
            mark_label = f"{marks} mark{'s' if marks > 1 else ''}"

            story.append(
                Paragraph(
                    f"Q{q_num}.  [{mark_label}]  {escape(question_text)}",
                    style_question,
                )
            )

            options = q.get("options")
            if isinstance(options, dict):
                for label, text in options.items():
                    story.append(
                        Paragraph(f"{escape(str(label))})  {escape(str(text))}", style_option)
                    )

            if section_name in ("Short Answer", "Descriptive", "Fill in the Blanks"):
                story.append(Spacer(1, 0.6 * cm))
                story.append(
                    HRFlowable(
                        width="100%",
                        thickness=0.5,
                        color=colors.HexColor("#cccccc"),
                        spaceAfter=4,
                    )
                )

            answer_key_entries.append(("answer", q_num, str(q.get("answer", "N/A")), marks))
            q_num += 1

        section_num += 1

    story.append(Spacer(1, 0.5 * cm))
    story.append(
        HRFlowable(width="100%", thickness=2, color=colors.HexColor("#1a1a2e"), spaceAfter=6)
    )
    story.append(
        Paragraph(f"TOTAL MARKS: {total_marks}  |  TOTAL QUESTIONS: {q_num - 1}", style_footer)
    )

    story.append(PageBreak())
    story.append(Paragraph("ANSWER KEY", style_title))
    story.append(
        HRFlowable(width="100%", thickness=2, color=colors.HexColor("#c0392b"), spaceAfter=10)
    )

    for entry in answer_key_entries:
        if entry[0] == "section":
            _, sec_title, sec_idx = entry
            story.append(
                Paragraph(f"  Section {sec_idx}: {escape(str(sec_title))}", style_answer_head)
            )
        else:
            _, num, ans, marks = entry
            mark_label = f"{marks} mark{'s' if marks > 1 else ''}"
            story.append(
                Paragraph(
                    f"<b>Q{num}.</b>  {escape(ans)}  "
                    f"<font color='#888888'>({mark_label})</font>",
                    style_answer,
                )
            )

    doc.build(story)
    return out_file