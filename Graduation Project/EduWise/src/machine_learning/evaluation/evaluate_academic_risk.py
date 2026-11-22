"""Evaluate a saved model against the exact holdout reserved during training."""

import json
import logging
from pathlib import Path

from sklearn.metrics import (
    accuracy_score, confusion_matrix, f1_score, precision_score, recall_score, roc_auc_score,
)

from src.config.settings import METRICS_PATH, MODEL_PATH, TEST_DATA
from src.machine_learning.models.academic_risk_model import AcademicRiskModel, file_digest
from src.machine_learning.preprocessing.academic_risk_preprocessor import TARGET, load_labeled


def evaluate(model_path: Path = MODEL_PATH, test_path: Path = TEST_DATA,
             output: Path = METRICS_PATH) -> dict:
    model = AcademicRiskModel.load(model_path)
    if file_digest(test_path) != model.holdout_sha256:
        raise ValueError("test data differs from the holdout recorded during training")
    data = load_labeled(test_path)
    labels = data[TARGET]
    probabilities = model.probabilities(data)
    predicted = probabilities >= model.threshold
    report = {
        "model_version": model.model_version, "classifier": model.selection["winner"]["classifier"],
        "provenance": "Synthetic Egyptian education-center cohort; target is simulated future assessment < 57/100.",
        "test_count": len(data), "at_risk_count": int(labels.sum()),
        "at_risk_prevalence": float(labels.mean()), "threshold": model.threshold,
        "accuracy": accuracy_score(labels, predicted),
        "precision": precision_score(labels, predicted, zero_division=0),
        "recall": recall_score(labels, predicted, zero_division=0),
        "f1": f1_score(labels, predicted, zero_division=0), "roc_auc": roc_auc_score(labels, probabilities),
        "class_order": [0, 1], "matrix_axes": ["actual", "predicted"],
        "confusion_matrix": confusion_matrix(labels, predicted, labels=[0, 1]).tolist(),
        "selection": model.selection, "versions": model.versions, "test_sha256": model.holdout_sha256,
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    return report


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    logging.info("Holdout F1: %.4f", evaluate()["f1"])
