"""Model/data contracts, holdout isolation, and saved artifact smoke tests."""

import json

import numpy as np
import pandas as pd
import pytest

from data.generate_academic_data import generate_data
from src.backend.services.academic_risk_service import AcademicRiskService, InvalidStudentData
from src.config.settings import METRICS_PATH, RAW_DATA, TEST_DATA, TRAIN_DATA
from src.machine_learning.evaluation.evaluate_academic_risk import evaluate
from src.machine_learning.models.academic_risk_model import AcademicRiskModel, ModelUnavailableError
from src.machine_learning.preprocessing.academic_risk_preprocessor import (
    FEATURES, QUIZZES, TARGET, build_preprocessor, engineer_features, load_labeled, prepare_splits,
)


@pytest.fixture(scope="module")
def service():
    return AcademicRiskService()


def test_generated_dataset():
    data = generate_data()
    pd.testing.assert_frame_equal(data, generate_data())
    pd.testing.assert_frame_equal(data, pd.read_csv(RAW_DATA), check_dtype=False)
    assert len(data) == data.student_id.nunique() == 3000
    assert data.name.str.contains("[ء-ي]").all()
    assert data.attendance_rate.between(0, 1).all()
    assert data.homework_completion_rate.between(0, 1).all()
    assert data.missed_sessions_count.between(0, 8).all()
    assert data.fee_delayed_days.ge(0).all()
    for key in ("midterm_score", "average_quiz_score", "participation_score", *QUIZZES):
        assert data[key].dropna().between(0, 100).all()
    assert data.groupby(TARGET).midterm_score.mean()[0] > data.groupby(TARGET).midterm_score.mean()[1]


def test_saved_splits(tmp_path):
    train, test = prepare_splits(RAW_DATA, tmp_path / "train.csv", tmp_path / "test.csv")
    assert (len(train), len(test)) == (2400, 600)
    assert set(train.student_id).isdisjoint(test.student_id)
    assert abs(train[TARGET].mean() - test[TARGET].mean()) < 0.005
    assert train.student_id.tolist() == load_labeled(TRAIN_DATA).student_id.tolist()
    assert test.student_id.tolist() == load_labeled(TEST_DATA).student_id.tolist()


def test_duplicate_student_rejected(tmp_path):
    data = generate_data(10)
    data.loc[1, "student_id"] = data.loc[0, "student_id"]
    path = tmp_path / "duplicate.csv"
    data.to_csv(path, index=False)
    with pytest.raises(ValueError, match="one snapshot"):
        load_labeled(path)


def test_trend_and_unseen_group():
    train = load_labeled(TRAIN_DATA).head(50)
    sample = train.head(3).copy()
    sample.loc[:, list(QUIZZES)] = [[20, np.nan, 50], [np.nan, 50, 40], [np.nan, np.nan, 30]]
    trend = engineer_features(sample).quiz_trend
    assert list(trend[:2]) == [15, -10] and np.isnan(trend.iloc[2])
    transformer = build_preprocessor().fit(train)
    sample["group_id"] = "never-seen"
    assert np.isfinite(transformer.transform(sample)).all()


def test_schema_and_exclusions(service):
    row = {"student_id": "S", "group_id": "unseen", "midterm_score": 50}
    result = service.predict(row)
    assert set(result) == {"student_id", "group_id", "risk_probability", "risk_threshold",
                           "is_at_risk", "model_version"}
    assert result["is_at_risk"] == int(result["risk_probability"] >= result["risk_threshold"])
    assert 0 <= result["risk_probability"] <= 1
    assert json.loads(json.dumps(result, allow_nan=False)) == result
    assert not {"student_id", "name", "fee_delayed_days", TARGET}.intersection(FEATURES)
    assert service.predict(dict(row, name="M", fee_delayed_days=77, is_at_risk=1)) == result


@pytest.mark.parametrize("fields", [{}, {"fee_delayed_days": 6}, {"attendance_rate": 80},
                         {"average_quiz_score": -1}, {"participation_score": float("nan")},
                         {"missed_sessions_count": 9}, {"midterm_score": True}])
def test_bad_input(service, fields):
    with pytest.raises(InvalidStudentData):
        service.predict({"student_id": "S", "group_id": "G", **fields})


def test_artifact_round_trip(tmp_path, service):
    path = tmp_path / "copy.joblib"
    service.model.save(path)
    row = {"student_id": "S", "group_id": "G", "attendance_rate": 0}
    assert AcademicRiskService(path).predict(row) == service.predict(row)
    path.write_bytes(b"unreadable")
    with pytest.raises(ModelUnavailableError):
        AcademicRiskModel.load(path)
    with pytest.raises(ModelUnavailableError):
        AcademicRiskModel.load(tmp_path / "missing")


def test_shipped_metrics(tmp_path):
    report = evaluate(output=tmp_path / "metrics.json")
    assert json.loads(METRICS_PATH.read_text()) == report
    assert sum(map(sum, report["confusion_matrix"])) == report["test_count"] == 600
    assert report["class_order"] == [0, 1]
    assert {c["classifier"] for c in report["selection"]["candidates"]} == {
        "LogisticRegression", "RandomForestClassifier", "XGBClassifier"}
    with pytest.raises(ValueError, match="holdout"):
        evaluate(test_path=TRAIN_DATA, output=tmp_path / "other.json")


def test_explainability(service):
    sample = {
        "student_id": "STU-001", "group_id": "G-01",
        "attendance_rate": 0.40, "homework_completion_rate": 0.35,
        "average_quiz_score": 38, "midterm_score": 42, "participation_score": 35,
        "missed_sessions_count": 4, "quiz_oldest": 50, "quiz_middle": 40, "quiz_latest": 30,
    }
    explanation = service.explain(sample)
    assert explanation["student_id"] == "STU-001"
    assert "risk_probability" in explanation
    assert "top_risk_factors" in explanation
    assert "top_protective_factors" in explanation
    assert "recommended_actions" in explanation
    assert len(explanation["recommended_actions"]["ar"]) > 0
    assert len(explanation["recommended_actions"]["en"]) > 0

    # Prediction with explanation flag
    result = service.predict(sample, include_explanation=True)
    assert "explanation" in result
    assert result["explanation"]["student_id"] == "STU-001"


def test_what_if_simulation(service):
    at_risk_sample = {
        "student_id": "STU-002", "group_id": "G-01",
        "attendance_rate": 0.40, "homework_completion_rate": 0.35,
        "average_quiz_score": 35, "midterm_score": 40, "participation_score": 30,
        "missed_sessions_count": 4, "quiz_oldest": 45, "quiz_middle": 35, "quiz_latest": 30,
    }
    improvements = {
        "attendance_rate": 0.90,
        "homework_completion_rate": 0.85,
        "quiz_latest": 80,
        "missed_sessions_count": 0,
    }
    sim = service.simulate_what_if(at_risk_sample, improvements)
    assert sim["baseline_probability"] > sim["simulated_probability"]
    assert sim["risk_reduction"] > 0
    assert sim["simulated_is_at_risk"] == 0
    assert sim["rescued_from_risk"] is True

