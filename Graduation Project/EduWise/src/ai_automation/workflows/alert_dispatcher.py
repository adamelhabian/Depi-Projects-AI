"""Build parent messages from verified attendance and explainability evidence."""

from typing import Any

from src.ai_automation.integrations.n8n_client import N8nClient


def format_parent_alert(
    student: dict[str, Any],
    risk: dict[str, Any],
    missed_sessions: int,
    weak_topics: list[str],
) -> str:
    lines = [
        f"مرحباً {student['guardian_name']}،",
        f"نتواصل معكم لمتابعة تقدّم {student['student_name']} الدراسي.",
    ]
    if missed_sessions >= 3:
        lines.append(f"سجّلنا غياب {missed_sessions} حصص.")
    if risk.get("is_at_risk"):
        lines.append("تشير مؤشرات الأداء الحالية إلى أن الطالب قد يحتاج إلى دعم إضافي.")
        explanation = risk.get("explanation") or {}
        factors = explanation.get("top_risk_factors", [])
        if factors and factors[0].get("label_ar"):
            lines.append(f"من المؤشرات التي تستحق المتابعة: {factors[0]['label_ar']}.")
    if weak_topics:
        lines.append(f"موضوعات مقترحة للمراجعة: {'، '.join(weak_topics[:5])}.")
    actions = (risk.get("explanation") or {}).get("recommended_actions", {}).get("ar", [])
    if risk.get("is_at_risk") and actions:
        lines.append(f"خطوة مقترحة: {actions[0]}")
    if student.get("materials_url"):
        lines.append(f"مواد المراجعة: {student['materials_url']}")
    if slots := student.get("makeup_slots_ar"):
        lines.append(f"مواعيد التعويض المتاحة: {'، '.join(slots)}.")
    lines.append("يمكنكم التواصل مع المركز للاتفاق على خطوة دعم مناسبة.")
    return "\n".join(lines)


def dispatch_student_alert(event_id: str, client: N8nClient | None = None) -> dict[str, Any]:
    return (client or N8nClient()).send_alert({"event_id": event_id})
