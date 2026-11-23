"""Regression coverage for the FastAPI, n8n and SQLite automation contracts."""

import json
from concurrent.futures import ThreadPoolExecutor
from unittest.mock import Mock, patch

import pytest
import requests
from fastapi.testclient import TestClient

from src.ai_automation.integrations.n8n_client import N8nClient, N8nDispatchError
from src.ai_automation.storage import get_homework
from src.ai_automation.workflows.homework_grader import format_telegram_feedback
from src.main import app

ALERTS = "/api/v1/alerts"
HOMEWORK = "/api/v1/homework"
OPERATOR = {"Authorization": "Bearer test-operator"}
WORKFLOW = {"Authorization": "Bearer test-workflow"}
SOURCE = {"telegram_user_id": "222", "message_id": 15, "assignment_code": "HW-01"}


@pytest.fixture
def client(tmp_path, monkeypatch):
    config_path = tmp_path / "automation.json"
    config_path.write_text(json.dumps({
        "students": {
            "EG-800": {
                "student_name": "سارة",
                "guardian_chat_id": "123",
                "student_telegram_id": "222",
                "assignments": ["HW-01"],
                "materials_url": "https://materials.example.org/math.pdf",
            },
            "EG-900": {"student_name": "علي"},
        },
        "assignments": {
            "HW-01": {
                "version": "v1",
                "questions": [
                    {"question_id": "1", "max_score": 1, "grading_criteria": "Award one point for 2.",
                     "correct_solution_ar": "نجمع ١ و١، والناتج ٢."},
                    {"question_id": "2", "max_score": 4, "grading_criteria": "Award up to four points.",
                     "correct_solution_ar": "الحل المعتمد من المعلم."},
                ],
            },
        },
    }), encoding="utf-8")
    monkeypatch.setenv("EDUWISE_AUTOMATION_CONFIG", str(config_path))
    monkeypatch.setenv("EDUWISE_AUTOMATION_DB", str(tmp_path / "automation.sqlite3"))
    monkeypatch.setenv("EDUWISE_AUTOMATION_OPERATOR_TOKEN", "test-operator")
    monkeypatch.setenv("EDUWISE_AUTOMATION_CALLBACK_TOKEN", "test-workflow")
    monkeypatch.setenv("N8N_WEBHOOK_URL", "https://n8n.example.org/webhook/student-eval")
    monkeypatch.setenv("N8N_WEBHOOK_TOKEN", "test-n8n")
    return TestClient(app)


def webhook_response(event_id="session-12"):
    response = Mock(status_code=202)
    response.json.return_value = {"status": "accepted", "event_id": event_id}
    return response


def trigger_alert(client, **kwargs):
    with patch("requests.post", return_value=webhook_response()) as dispatch:
        response = client.post(
            f"{ALERTS}/trigger-risk-eval",
            headers={**OPERATOR, "Idempotency-Key": "session-12"},
            json={"student_id": "EG-800", "missed_sessions_count": 3, **kwargs},
        )
    return response, dispatch


def grade_payload(first_status="scored", second_status="scored", second_score=2):
    return {
        **SOURCE, "rubric_version": "v1", "model": "gemini-3.6-flash",
        "result": {
            "questions": [
                {"question_id": "1", "status": first_status, "earned_score": int(first_status == "scored"),
                 "student_answer": "2" if first_status == "scored" else "", "explanation_ar": ""},
                {"question_id": "2", "status": second_status, "earned_score": second_score,
                 "student_answer": "إجابة مرصودة", "explanation_ar": "راجع الخطوة الأخيرة."},
            ],
            "feedback_ar": "راجع ترتيب الخطوات.",
        },
    }


def test_health_is_public_and_tokens_are_scoped(client):
    assert client.get("/health").json()["status"] == "ok"
    calls = [
        (f"{ALERTS}/trigger-risk-eval", {"student_id": "EG-800"}, WORKFLOW),
        (f"{ALERTS}/claim", {"event_id": "event"}, OPERATOR),
        (f"{HOMEWORK}/context", SOURCE, OPERATOR),
        (f"{HOMEWORK}/submissions", grade_payload(), OPERATOR),
    ]
    for route, body, wrong in calls:
        assert client.post(route, json=body).status_code == 401
        assert client.post(route, headers=wrong, json=body).status_code == 401


def test_automation_fails_closed_without_credentials(client, monkeypatch):
    monkeypatch.delenv("EDUWISE_AUTOMATION_CALLBACK_TOKEN")
    assert client.post(f"{HOMEWORK}/context", headers=WORKFLOW, json=SOURCE).status_code == 503


def test_webhook_auth_acknowledgement_and_no_redirect(client):
    response, dispatch = trigger_alert(client)
    assert response.json()["dispatch_result"]["status"] == "accepted"
    assert response.json()["risk_result"]["risk_probability"] is None
    assert dispatch.call_args.kwargs == {
        "json": {"event_id": "session-12"},
        "headers": {"Authorization": "Bearer test-n8n"},
        "timeout": 8.0,
        "allow_redirects": False,
    }


@pytest.mark.parametrize("response", [Mock(status_code=302), webhook_response("wrong-event")])
def test_webhook_rejects_redirect_and_mismatched_event(client, response):
    with patch("requests.post", return_value=response), pytest.raises(N8nDispatchError):
        N8nClient().send_alert({"event_id": "session-12"})


def test_transport_failure_is_sanitized_and_retryable(client):
    with patch("requests.post", side_effect=requests.ConnectTimeout("internal address")):
        response = client.post(
            f"{ALERTS}/trigger-risk-eval", headers={**OPERATOR, "Idempotency-Key": "session-12"},
            json={"student_id": "EG-800", "missed_sessions_count": 3},
        )
    assert response.json()["dispatch_result"] == {"event_id": "session-12", "status": "dispatch_unconfirmed"}
    assert "internal address" not in response.text
    assert client.get(f"{ALERTS}/events/session-12", headers=OPERATOR).json()["status"] == "pending"
    assert trigger_alert(client)[0].json()["dispatch_result"]["status"] == "accepted"


def test_real_ml_inference_dispatches_with_shap(client):
    response, dispatch = trigger_alert(client, student_features={
        "student_id": "EG-800", "group_id": "G-01", "missed_sessions_count": 4,
        "attendance_rate": 0.45, "midterm_score": 35,
    })
    assert response.status_code == 200
    risk = response.json()["risk_result"]
    assert 0 <= risk["risk_probability"] <= 1
    assert risk["explanation"]["student_id"] == "EG-800"
    assert risk["explanation"]["top_risk_factors"]
    dispatch.assert_called_once()


def test_attendance_uses_threshold_without_fabricating_probability(client):
    response, dispatch = trigger_alert(client, missed_sessions_count=2)
    assert response.json()["should_alert"] is False
    assert response.json()["is_at_risk"] is None
    dispatch.assert_not_called()


def test_alert_requires_verified_guardian_and_matching_chat(client):
    missing, dispatch = trigger_alert(client, student_id="EG-900", telegram_chat_id="123")
    assert missing.json()["dispatch_result"]["status"] == "no_guardian_link"
    dispatch.assert_not_called()
    mismatch, dispatch = trigger_alert(client, telegram_chat_id="999")
    assert mismatch.status_code == 422
    dispatch.assert_not_called()


@pytest.mark.parametrize("risk", ["false", 2, 0.5])
def test_risk_uses_strict_boolean_or_binary_indicator(client, risk):
    response, dispatch = trigger_alert(client, direct_risk_result={
        "is_at_risk": risk, "risk_probability": 0.5,
    })
    assert response.status_code == 422
    dispatch.assert_not_called()


def test_alert_can_only_be_claimed_once_and_only_confirmed_after_telegram(client):
    assert trigger_alert(client)[0].status_code == 200
    audit = {"event_id": "session-12", "student_id": "EG-800", "status": "telegram_accepted",
             "telegram_message_id": 42}
    assert client.post(f"{ALERTS}/audit-callback", headers=WORKFLOW, json=audit).status_code == 409

    def claim(_):
        response = client.post(f"{ALERTS}/claim", headers=WORKFLOW, json={"event_id": "session-12"})
        assert response.status_code == 200
        return response.json()

    with ThreadPoolExecutor(max_workers=4) as pool:
        outcomes = list(pool.map(claim, range(4)))
    [claimed] = [outcome for outcome in outcomes if outcome["send"]]
    assert claimed["telegram_chat_id"] == "123"
    assert claimed["support_topic"] == "attendance"
    assert "غياب 3 حصص" in claimed["message"]
    assert "https://materials.example.org/math.pdf" in claimed["message"]

    first = client.post(f"{ALERTS}/audit-callback", headers=WORKFLOW, json=audit)
    duplicate = client.post(f"{ALERTS}/audit-callback", headers=WORKFLOW, json=audit)
    assert first.status_code == duplicate.status_code == 200
    assert client.get(f"{ALERTS}/events/session-12", headers=OPERATOR).json()["telegram_message_id"] == 42
    repeated, dispatch = trigger_alert(client)
    assert repeated.json()["dispatch_result"]["status"] == "telegram_accepted"
    dispatch.assert_not_called()


def test_alert_failure_and_changed_request_are_not_silently_overwritten(client):
    assert trigger_alert(client)[0].status_code == 200
    assert trigger_alert(client, weak_topics=["موضوع آخر"])[0].status_code == 409
    client.post(f"{ALERTS}/claim", headers=WORKFLOW, json={"event_id": "session-12"})
    body = {"event_id": "session-12", "student_id": "EG-800", "status": "delivery_unknown"}
    assert client.post(f"{ALERTS}/audit-callback", headers=WORKFLOW, json=body).status_code == 200
    assert trigger_alert(client)[0].json()["dispatch_result"]["status"] == "delivery_unknown"


def test_revoked_guardian_link_cancels_pending_alert(client, monkeypatch):
    import os
    from pathlib import Path

    assert trigger_alert(client)[0].status_code == 200
    config = Path(os.environ["EDUWISE_AUTOMATION_CONFIG"])
    data = json.loads(config.read_text(encoding="utf-8"))
    data["students"]["EG-800"]["guardian_chat_id"] = "999"
    config.write_text(json.dumps(data), encoding="utf-8")
    claim = client.post(f"{ALERTS}/claim", headers=WORKFLOW, json={"event_id": "session-12"})
    assert claim.json() == {"send": False}
    assert client.get(f"{ALERTS}/events/session-12", headers=OPERATOR).json()["status"] == "cancelled"


def test_only_linked_student_can_load_assigned_rubric(client):
    allowed = client.post(f"{HOMEWORK}/context", headers=WORKFLOW, json=SOURCE)
    assert allowed.json()["rubric"]["questions"][1]["max_score"] == 4
    for params in [{"telegram_user_id": "555"}, {"assignment_code": "HW-02"}]:
        denied = client.post(f"{HOMEWORK}/context", headers=WORKFLOW, json={**SOURCE, **params})
        assert denied.status_code == 403


def test_grade_uses_rubric_totals_and_survives_separate_connections(client):
    result = client.post(f"{HOMEWORK}/submissions", headers=WORKFLOW, json=grade_payload())
    assert result.status_code == 200
    saved = result.json()
    assert saved["created"]
    record = saved["data"]["record"]
    assert (record["score"], record["max_score"], record["percentage"], record["passed"]) == (3, 5, 60, True)
    assert record["status"] == "provisional"
    assert record["student_id"] == "EG-800"
    assert record["questions"][0]["correct_solution_ar"] in saved["messages"][0]
    assert get_homework("telegram:222:15")["feedback_status"] == "pending"

    duplicate = client.post(f"{HOMEWORK}/submissions", headers=WORKFLOW, json=grade_payload(second_score=3)).json()
    assert (duplicate["created"], duplicate["messages"], duplicate["data"]["record"]["score"]) == (False, [], 3)
    assert client.post(f"{HOMEWORK}/context", headers=WORKFLOW, json=SOURCE).json() == {"process": False}
    callback = {**SOURCE, "status": "telegram_accepted"}
    for _ in range(2):
        assert client.post(f"{HOMEWORK}/feedback-callback", headers=WORKFLOW, json=callback).status_code == 200
    stored = client.get(f"{HOMEWORK}/submissions/telegram:222:15", headers=OPERATOR).json()
    assert stored["feedback_status"] == "telegram_accepted"


def test_grading_rejects_scores_beyond_rubric_and_stale_versions(client):
    bad = grade_payload(second_score=5)
    assert client.post(f"{HOMEWORK}/submissions", headers=WORKFLOW, json=bad).status_code == 422
    bad = {**grade_payload(), "rubric_version": "stale"}
    assert client.post(f"{HOMEWORK}/submissions", headers=WORKFLOW, json=bad).status_code == 422
    bad = grade_payload()
    bad["result"]["questions"][1]["question_id"] = "1"
    assert client.post(f"{HOMEWORK}/submissions", headers=WORKFLOW, json=bad).status_code == 422
    assert get_homework("telegram:222:15") is None


def test_unreadable_answer_has_no_score_and_no_false_praise(client):
    response = client.post(
        f"{HOMEWORK}/submissions", headers=WORKFLOW,
        json=grade_payload(second_status="unreadable", second_score=0),
    )
    record = response.json()["data"]["record"]
    assert (record["status"], record["score"], record["passed"]) == ("needs_review", None, None)
    assert "أوضح" in response.json()["messages"][0]


def test_telegram_feedback_keeps_unicode_within_length_limit(client):
    response = client.post(f"{HOMEWORK}/submissions", headers=WORKFLOW, json=grade_payload())
    record = response.json()["data"]["record"]
    question = record["questions"][0]
    question.update(student_answer="🧮" * 700, explanation_ar="💡" * 700, correct_solution_ar="🧾" * 1400)
    messages = format_telegram_feedback(record)
    assert len(messages) > 1
    assert all(len(message.encode("utf-16-le")) // 2 <= 3800 for message in messages)
    assert sum(message.count("🧾") for message in messages) == 1400
