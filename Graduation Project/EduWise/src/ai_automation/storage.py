"""SQLite persistence for alert state and provisional homework submissions."""

import json
import os
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Any

from src.config.settings import PROJECT_ROOT

_SCHEMA = """
CREATE TABLE IF NOT EXISTS automation_alerts (
    event_id TEXT PRIMARY KEY,
    fingerprint TEXT NOT NULL,
    student_id TEXT NOT NULL,
    payload TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending',
    telegram_message_id INTEGER,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS automation_homework (
    submission_id TEXT PRIMARY KEY,
    record TEXT NOT NULL,
    feedback_status TEXT NOT NULL DEFAULT 'pending',
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
"""


class AutomationConflict(ValueError):
    """An existing event is bound to different data or a different state."""


def _encode(value: dict[str, Any]) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, allow_nan=False)


@contextmanager
def _connection():
    configured = os.getenv("EDUWISE_AUTOMATION_DB") or os.getenv("EDUWISE_ALERT_DB")
    path = Path(configured) if configured else PROJECT_ROOT / "var" / "academic_alerts.sqlite3"
    path.parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(path, timeout=5)
    db.row_factory = sqlite3.Row
    try:
        db.executescript(_SCHEMA)
        with db:
            yield db
    finally:
        db.close()


def reserve_alert(event_id: str, fingerprint: str, student_id: str, payload: dict) -> str:
    with _connection() as db:
        db.execute(
            "INSERT INTO automation_alerts (event_id, fingerprint, student_id, payload) VALUES (?, ?, ?, ?) "
            "ON CONFLICT(event_id) DO NOTHING",
            (event_id, fingerprint, student_id, _encode(payload)),
        )
        event = db.execute("SELECT * FROM automation_alerts WHERE event_id = ?", (event_id,)).fetchone()
        if event["fingerprint"] != fingerprint:
            raise AutomationConflict("Idempotency key is already bound to another risk evaluation")
        return event["status"]


def get_alert(event_id: str) -> dict | None:
    with _connection() as db:
        event = db.execute(
            "SELECT event_id, student_id, status, telegram_message_id, updated_at, payload "
            "FROM automation_alerts WHERE event_id = ?", (event_id,)
        ).fetchone()
        return dict(event) if event else None


def claim_alert(event_id: str, guardian_chat_id: str | None) -> dict | None:
    with _connection() as db:
        db.execute("BEGIN IMMEDIATE")
        event = db.execute("SELECT status, payload FROM automation_alerts WHERE event_id = ?", (event_id,)).fetchone()
        if not event or event["status"] != "pending":
            return None
        payload = json.loads(event["payload"])
        if not guardian_chat_id or payload["telegram_chat_id"] != guardian_chat_id:
            db.execute(
                "UPDATE automation_alerts SET status = 'cancelled', updated_at = CURRENT_TIMESTAMP WHERE event_id = ?",
                (event_id,),
            )
            return None
        db.execute(
            "UPDATE automation_alerts SET status = 'sending', updated_at = CURRENT_TIMESTAMP WHERE event_id = ?",
            (event_id,),
        )
        return payload


def finish_alert(event_id: str, student_id: str, status: str, message_id: int | None) -> None:
    with _connection() as db:
        changed = db.execute(
            "UPDATE automation_alerts SET status = ?, telegram_message_id = ?, updated_at = CURRENT_TIMESTAMP "
            "WHERE event_id = ? AND student_id = ? AND status = 'sending'",
            (status, message_id, event_id, student_id),
        ).rowcount
        if not changed:
            event = db.execute("SELECT * FROM automation_alerts WHERE event_id = ?", (event_id,)).fetchone()
            if not event:
                raise KeyError(event_id)
            if (event["student_id"], event["status"], event["telegram_message_id"]) != (student_id, status, message_id):
                raise AutomationConflict("Alert callback does not match the reserved delivery")


def get_homework(submission_id: str) -> dict | None:
    with _connection() as db:
        row = db.execute(
            "SELECT record, feedback_status FROM automation_homework WHERE submission_id = ?", (submission_id,)
        ).fetchone()
        return {**json.loads(row["record"]), "feedback_status": row["feedback_status"]} if row else None


def save_homework(submission_id: str, record: dict) -> tuple[dict, bool]:
    with _connection() as db:
        created = db.execute(
            "INSERT INTO automation_homework (submission_id, record) VALUES (?, ?) "
            "ON CONFLICT(submission_id) DO NOTHING", (submission_id, _encode(record))
        ).rowcount == 1
        stored = db.execute(
            "SELECT record FROM automation_homework WHERE submission_id = ?", (submission_id,)
        ).fetchone()
        immutable = json.loads(stored["record"])
        fields = ("student_id", "assignment_code", "rubric_version")
        if any(immutable[key] != record[key] for key in fields):
            raise AutomationConflict("Submission ID is already bound to another assignment")
        return immutable, created


def finish_homework_feedback(submission_id: str, status: str) -> None:
    with _connection() as db:
        changed = db.execute(
            "UPDATE automation_homework SET feedback_status = ? WHERE submission_id = ? AND feedback_status = 'pending'",
            (status, submission_id),
        ).rowcount
        if not changed:
            row = db.execute(
                "SELECT feedback_status FROM automation_homework WHERE submission_id = ?", (submission_id,)
            ).fetchone()
            if not row:
                raise KeyError(submission_id)
            if row["feedback_status"] != status:
                raise AutomationConflict("Homework feedback already has a different delivery outcome")
