"""Authenticated automation routes for EduWise staff and n8n."""

import hashlib
import json
import logging
import os
from functools import lru_cache
from secrets import compare_digest
from typing import Annotated, Literal
from uuid import uuid4

from fastapi import APIRouter, Depends, Header, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import Field, StrictBool, ValidationError

from src.ai_automation.automation_config import (
    AutomationConfig,
    Contract,
    Identifier,
    ShortText,
    TelegramID,
    load_automation_config,
)
from src.ai_automation.integrations.n8n_client import N8nDispatchError
from src.ai_automation.storage import (
    AutomationConflict,
    claim_alert,
    finish_alert,
    finish_homework_feedback,
    get_alert,
    get_homework,
    reserve_alert,
    save_homework,
)
from src.ai_automation.workflows.alert_dispatcher import dispatch_student_alert, format_parent_alert
from src.ai_automation.workflows.homework_grader import (
    HomeworkSource,
    HomeworkSubmission,
    format_telegram_feedback,
    validate_homework_payload,
)
from src.backend.services.academic_risk_service import AcademicRiskService, InvalidStudentData

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1", tags=["automation"])
bearer = HTTPBearer(auto_error=False)


def _require_token(variable: str, credentials: HTTPAuthorizationCredentials | None) -> None:
    expected = os.getenv(variable)
    if not expected:
        raise HTTPException(503, "Automation credentials are not configured")
    if not credentials or not compare_digest(credentials.credentials.encode(), expected.encode()):
        raise HTTPException(401, "Invalid automation credentials", headers={"WWW-Authenticate": "Bearer"})


def require_operator(credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer)]) -> None:
    _require_token("EDUWISE_AUTOMATION_OPERATOR_TOKEN", credentials)


def require_workflow(credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer)]) -> None:
    _require_token("EDUWISE_AUTOMATION_CALLBACK_TOKEN", credentials)


def get_config() -> AutomationConfig:
    try:
        return load_automation_config()
    except (OSError, ValidationError, UnicodeError):
        logger.error("Automation roster or rubrics could not be loaded")
        raise HTTPException(503, "Automation roster or rubrics are unavailable") from None


@lru_cache(maxsize=1)
def get_risk_service() -> AcademicRiskService:
    return AcademicRiskService()


class RiskFactor(Contract):
    model_config = {"extra": "ignore"}
    label_ar: ShortText


class RiskExplanation(Contract):
    model_config = {"extra": "ignore"}
    top_risk_factors: list[RiskFactor] = Field(default_factory=list, max_length=10)
    recommended_actions: dict[str, list[ShortText]] = Field(default_factory=dict)


class DirectRiskResult(Contract):
    model_config = {"extra": "ignore"}
    is_at_risk: StrictBool | Literal[0, 1]
    risk_probability: float = Field(ge=0, le=1, strict=True)
    explanation: RiskExplanation | None = None


class TriggerRiskEvalRequest(Contract):
    student_id: Identifier
    telegram_chat_id: TelegramID | None = None
    student_name: ShortText | None = None
    guardian_name: ShortText | None = None
    missed_sessions_count: int = Field(default=0, ge=0, le=1000, strict=True)
    weak_topics: list[ShortText] = Field(default_factory=list, max_length=8)
    student_features: dict | None = None
    direct_risk_result: DirectRiskResult | None = None


class AlertClaimRequest(Contract):
    event_id: Identifier


class AlertAuditCallbackRequest(AlertClaimRequest):
    student_id: Identifier
    status: Literal["telegram_accepted", "delivery_unknown"]
    telegram_message_id: int | None = Field(default=None, gt=0, strict=True)


class HomeworkFeedbackCallback(HomeworkSource):
    status: Literal["telegram_accepted", "delivery_unknown"]


def evaluate_risk(request: TriggerRiskEvalRequest) -> dict:
    if request.student_features is not None:
        features = {**request.student_features, "student_id": request.student_id}
        if (
            "missed_sessions_count" in request.model_fields_set
            and request.missed_sessions_count <= 8
            and "missed_sessions_count" not in features
        ):
            features["missed_sessions_count"] = request.missed_sessions_count
        try:
            return get_risk_service().predict(features, include_explanation=True)
        except InvalidStudentData:
            raise HTTPException(422, "Invalid student features for academic risk evaluation") from None
        except Exception:
            logger.error("Academic risk inference is unavailable")
            raise HTTPException(503, "Academic risk inference is unavailable") from None
    if request.direct_risk_result:
        return request.direct_risk_result.model_dump()
    return {"is_at_risk": None, "risk_probability": None}


@router.post("/alerts/trigger-risk-eval", dependencies=[Depends(require_operator)])
def trigger_student_risk_eval(
    request: TriggerRiskEvalRequest,
    idempotency_key: Annotated[Identifier | None, Header()] = None,
) -> dict:
    if request.student_features is not None and request.direct_risk_result is not None:
        raise HTTPException(422, "Provide features or a precomputed risk result")
    if request.student_features and "student_id" in request.student_features:
        if request.student_features["student_id"] != request.student_id:
            raise HTTPException(422, "Student ID does not match the feature snapshot")

    risk = evaluate_risk(request)
    missed_sessions = request.missed_sessions_count
    if "missed_sessions_count" not in request.model_fields_set and request.student_features:
        missed_sessions = request.student_features.get("missed_sessions_count") or 0
    should_alert = bool(risk["is_at_risk"]) or missed_sessions >= 3
    result = {
        "student_id": request.student_id,
        "should_alert": should_alert,
        "is_at_risk": None if risk["is_at_risk"] is None else bool(risk["is_at_risk"]),
        "missed_sessions_count": missed_sessions,
        "risk_result": risk,
        "dispatch_result": None,
    }
    if not should_alert:
        return result

    student = get_config().students.get(request.student_id)
    if not student or not student.guardian_chat_id:
        result["dispatch_result"] = {"status": "no_guardian_link"}
        return result
    if request.telegram_chat_id is not None and request.telegram_chat_id != student.guardian_chat_id:
        raise HTTPException(422, "Chat ID does not match the verified guardian link")

    event_id = idempotency_key or f"evt-{uuid4().hex}"
    canonical = request.model_dump_json(exclude_unset=True)
    fingerprint = hashlib.sha256(json.dumps(json.loads(canonical), sort_keys=True).encode()).hexdigest()
    payload = {
        "event_id": event_id,
        "student_id": request.student_id,
        "telegram_chat_id": student.guardian_chat_id,
        "support_topic": (
            "both" if risk["is_at_risk"] and missed_sessions >= 3
            else "academic" if risk["is_at_risk"] else "attendance"
        ),
        "message": format_parent_alert(student.model_dump(mode="json"), risk, missed_sessions, request.weak_topics),
    }
    try:
        delivery_status = reserve_alert(event_id, fingerprint, request.student_id, payload)
    except AutomationConflict as exc:
        raise HTTPException(409, str(exc)) from None
    if delivery_status != "pending":
        result["dispatch_result"] = {"event_id": event_id, "status": delivery_status}
        return result
    try:
        result["dispatch_result"] = dispatch_student_alert(event_id)
    except N8nDispatchError:
        logger.warning("n8n did not acknowledge alert %s", event_id)
        result["dispatch_result"] = {"event_id": event_id, "status": "dispatch_unconfirmed"}
    return result


@router.get("/alerts/events/{event_id}", dependencies=[Depends(require_operator)])
def get_alert_status(event_id: Identifier) -> dict:
    event = get_alert(event_id)
    if not event:
        raise HTTPException(404, "Alert event not found")
    return {key: value for key, value in event.items() if key != "payload"}


@router.post("/alerts/claim", dependencies=[Depends(require_workflow)])
def claim_parent_alert(request: AlertClaimRequest) -> dict:
    event = get_alert(request.event_id)
    if not event:
        raise HTTPException(404, "Alert event not found")
    student = get_config().students.get(event["student_id"])
    payload = claim_alert(request.event_id, student.guardian_chat_id if student else None)
    return {"send": bool(payload), **(payload or {})}


@router.post("/alerts/audit-callback", dependencies=[Depends(require_workflow)])
def receive_alert_audit_callback(request: AlertAuditCallbackRequest) -> dict:
    if (request.status == "telegram_accepted") != (request.telegram_message_id is not None):
        raise HTTPException(422, "Telegram acceptance requires a message ID")
    try:
        finish_alert(request.event_id, request.student_id, request.status, request.telegram_message_id)
    except KeyError:
        raise HTTPException(404, "Alert event not found") from None
    except AutomationConflict as exc:
        raise HTTPException(409, str(exc)) from None
    return {"status": "received", "event_id": request.event_id}


def homework_context(source: HomeworkSource):
    config = get_config()
    for student_id, student in config.students.items():
        if student.student_telegram_id == source.telegram_user_id and source.assignment_code in student.assignments:
            return student_id, config.assignments[source.assignment_code]
    raise HTTPException(403, "Student account or assignment is not authorized")


@router.post("/homework/context", dependencies=[Depends(require_workflow)])
def get_homework_context(source: HomeworkSource) -> dict:
    _, rubric = homework_context(source)
    if existing := get_homework(source.submission_id):
        if existing["assignment_code"] != source.assignment_code:
            raise HTTPException(409, "Submission ID already belongs to another assignment")
        return {"process": False}
    return {"process": True, "rubric": rubric.model_dump()}


@router.post("/homework/submissions", dependencies=[Depends(require_workflow)])
def receive_homework_submission(submission: HomeworkSubmission) -> dict:
    student_id, rubric = homework_context(submission)
    try:
        record = validate_homework_payload(submission, student_id, rubric)
        stored, created = save_homework(submission.submission_id, record)
    except AutomationConflict as exc:
        raise HTTPException(409, str(exc)) from None
    except ValueError as exc:
        raise HTTPException(422, str(exc)) from None
    return {
        "status": "success",
        "data": {"record": stored},
        "created": created,
        "messages": format_telegram_feedback(stored) if created else [],
    }


@router.post("/homework/feedback-callback", dependencies=[Depends(require_workflow)])
def receive_homework_feedback(request: HomeworkFeedbackCallback) -> dict:
    stored = get_homework(request.submission_id)
    if not stored or stored["assignment_code"] != request.assignment_code:
        raise HTTPException(404, "Homework submission not found")
    try:
        finish_homework_feedback(request.submission_id, request.status)
    except AutomationConflict as exc:
        raise HTTPException(409, str(exc)) from None
    return {"status": "received", "submission_id": request.submission_id}


@router.get("/homework/submissions/{submission_id}", dependencies=[Depends(require_operator)])
def get_homework_submission(submission_id: Identifier) -> dict:
    stored = get_homework(submission_id)
    if not stored:
        raise HTTPException(404, "Homework submission not found")
    return stored
