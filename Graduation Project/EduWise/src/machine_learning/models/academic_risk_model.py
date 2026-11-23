"""Versioned, trusted on-disk academic-risk pipeline."""

import hashlib
import math
import os
import platform
from dataclasses import dataclass
from importlib.metadata import version
from pathlib import Path
from tempfile import NamedTemporaryFile

import joblib
import numpy as np
import pandas as pd
from sklearn.pipeline import Pipeline

from src.config.settings import MODEL_PATH
from src.machine_learning.preprocessing.academic_risk_preprocessor import FEATURES

MODEL_LIBRARIES = ("numpy", "pandas", "scikit-learn", "xgboost", "joblib", "scipy")


class ModelUnavailableError(RuntimeError):
    """The requested trained pipeline cannot be loaded or used."""


def runtime_versions() -> dict[str, str]:
    """Serialization compatibility depends on these Python and library versions."""
    return {"python": ".".join(platform.python_version_tuple()[:2]),
            **{name: version(name) for name in MODEL_LIBRARIES}}


def file_digest(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


@dataclass
class AcademicRiskModel:
    """Keep decision policy and training provenance with the fitted pipeline."""

    pipeline: Pipeline
    threshold: float
    model_version: str
    features: tuple[str, ...]
    versions: dict[str, str]
    holdout_sha256: str
    selection: dict

    def probabilities(self, frame: pd.DataFrame) -> np.ndarray:
        values = self.pipeline.predict_proba(frame.loc[:, list(self.features)])[:, 1]
        if not np.all(np.isfinite(values) & (values >= 0) & (values <= 1)):
            raise ModelUnavailableError("model returned an invalid probability")
        return values

    def save(self, path: Path = MODEL_PATH) -> None:
        """Replace the previous artifact only after successful serialization."""
        path.parent.mkdir(parents=True, exist_ok=True)
        with NamedTemporaryFile(dir=path.parent, delete=False) as stream:
            temporary = Path(stream.name)
        try:
            joblib.dump(self, temporary, compress=3)
            os.replace(temporary, path)
        finally:
            temporary.unlink(missing_ok=True)

    @classmethod
    def load(cls, path: Path = MODEL_PATH) -> "AcademicRiskModel":
        """Load a project-controlled joblib file. Never accept uploaded pickles."""
        try:
            model = joblib.load(path)
            if (not isinstance(model, cls) or model.features != FEATURES
                    or not math.isfinite(model.threshold) or not 0 <= model.threshold <= 1
                    or list(model.pipeline.classes_) != [0, 1] or not model.model_version
                    or model.versions != runtime_versions()):
                raise ValueError("incompatible artifact schema, runtime, or classifier")
        except Exception as exc:
            raise ModelUnavailableError(f"cannot load academic risk model at {path}: {exc}") from exc
        return model
