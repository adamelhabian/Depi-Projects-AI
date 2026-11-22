"""Validate student snapshots and build fold-local feature transformations."""

from pathlib import Path
from typing import Annotated, Self

import numpy as np
import pandas as pd
from pydantic import BaseModel, ConfigDict, Field, StringConstraints, model_validator
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import FunctionTransformer, OneHotEncoder, StandardScaler

from src.config.settings import RAW_DATA, TEST_DATA, TRAIN_DATA

Identifier = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=128)]
Rate = Annotated[float, Field(strict=True, ge=0, le=1, allow_inf_nan=False)]
Score = Annotated[float, Field(strict=True, ge=0, le=100, allow_inf_nan=False)]
AbsenceCount = Annotated[int, Field(strict=True, ge=0, le=8)]
RATES = ("attendance_rate", "homework_completion_rate")
SCORES = ("average_quiz_score", "midterm_score", "participation_score")
QUIZZES = ("quiz_oldest", "quiz_middle", "quiz_latest")
EVIDENCE = (*RATES, *SCORES, "missed_sessions_count", *QUIZZES)
FEATURES = ("group_id", *EVIDENCE)
TARGET = "is_at_risk"


class StudentSnapshot(BaseModel):
    """One student's measurements available at prediction time."""

    model_config = ConfigDict(extra="ignore")
    student_id: Identifier
    group_id: Identifier
    attendance_rate: Rate | None = None
    homework_completion_rate: Rate | None = None
    average_quiz_score: Score | None = None
    midterm_score: Score | None = None
    participation_score: Score | None = None
    missed_sessions_count: AbsenceCount | None = None
    quiz_oldest: Score | None = None
    quiz_middle: Score | None = None
    quiz_latest: Score | None = None

    @model_validator(mode="after")
    def require_evidence(self) -> Self:
        if all(getattr(self, field) is None for field in EVIDENCE):
            raise ValueError("provide at least one observed attendance or academic measurement")
        return self


def load_labeled(path: Path) -> pd.DataFrame:
    """Load labeled data, stripping identity metadata other than the split audit ID."""
    data = pd.read_csv(path, dtype={"student_id": "string", "group_id": "string"})
    required = {"student_id", "group_id", *RATES, *SCORES, "missed_sessions_count", TARGET}
    if missing := required.difference(data.columns):
        raise ValueError(f"missing dataset columns: {sorted(missing)}")
    if data.empty or not data[TARGET].isin([0, 1]).all():
        raise ValueError("expected nonempty dataset with binary is_at_risk")
    # Nullable integer counts must reach the same strict API validator as Python ints.
    data["missed_sessions_count"] = data["missed_sessions_count"].astype("Int64")
    records = data.astype(object).where(data.notna(), None).to_dict("records")
    clean = pd.DataFrame([StudentSnapshot.model_validate(row).model_dump() for row in records])
    if clean.student_id.duplicated().any():
        raise ValueError("one snapshot per student is required for a disjoint split")
    clean[TARGET] = data[TARGET].astype(int)
    return clean


def engineer_features(frame: pd.DataFrame) -> pd.DataFrame:
    """Compute change per quiz interval from observed, chronologically ordered slots."""
    features = frame.loc[:, FEATURES].copy()
    scores = features.loc[:, QUIZZES].to_numpy(dtype=float)
    present = np.isfinite(scores)
    first = present.argmax(axis=1)
    last = len(QUIZZES) - 1 - present[:, ::-1].argmax(axis=1)
    rows = np.arange(len(features))
    span = last - first
    features["quiz_trend"] = np.divide(
        scores[rows, last] - scores[rows, first], span,
        out=np.full(len(features), np.nan), where=span > 0,
    )
    return features


def build_preprocessor() -> Pipeline:
    """Build an unfitted transformer safe to fit on each training fold."""
    numeric = Pipeline([
        ("impute", SimpleImputer(strategy="median", add_indicator=True, keep_empty_features=True)),
        ("scale", StandardScaler()),
    ])
    columns = ColumnTransformer([
        ("numeric", numeric, [*EVIDENCE, "quiz_trend"]),
        ("group", OneHotEncoder(handle_unknown="ignore", sparse_output=False), ["group_id"]),
    ])
    return Pipeline([("engineer", FunctionTransformer(engineer_features)), ("columns", columns)])


def prepare_splits(raw: Path = RAW_DATA, train_path: Path = TRAIN_DATA,
                   test_path: Path = TEST_DATA, seed: int = 42) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Persist validated, unscaled splits so fitted statistics stay inside CV."""
    data = load_labeled(raw)
    train, test = train_test_split(data, test_size=0.2, stratify=data[TARGET], random_state=seed)
    for subset, path in ((train, train_path), (test, test_path)):
        path.parent.mkdir(parents=True, exist_ok=True)
        subset.to_csv(path, index=False, encoding="utf-8", lineterminator="\n")
    return train, test
