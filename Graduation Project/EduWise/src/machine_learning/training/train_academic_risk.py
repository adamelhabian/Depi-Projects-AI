"""Select a classifier and threshold on training folds, then fit the winning pipeline."""

import hashlib
import json
import logging

import numpy as np
from sklearn.base import BaseEstimator
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import precision_recall_curve
from sklearn.model_selection import StratifiedKFold, cross_val_predict
from sklearn.pipeline import Pipeline
from xgboost import XGBClassifier

from src.config.settings import MODEL_PATH, TEST_DATA, TRAIN_DATA
from src.machine_learning.models.academic_risk_model import (
    AcademicRiskModel, file_digest, runtime_versions,
)
from src.machine_learning.preprocessing.academic_risk_preprocessor import (
    FEATURES, TARGET, build_preprocessor, prepare_splits,
)

SEED = 42
LOGGER = logging.getLogger(__name__)


def candidates() -> list[BaseEstimator]:
    """Small CPU-friendly grid for three different classifier families."""
    return [
        *(LogisticRegression(C=c, max_iter=1000, random_state=SEED) for c in (0.1, 1.0, 10.0)),
        *(RandomForestClassifier(n_estimators=120, min_samples_leaf=leaf, max_features=0.8,
                                 n_jobs=2, random_state=SEED) for leaf in (3, 10)),
        *(XGBClassifier(n_estimators=100, max_depth=depth, learning_rate=0.07, tree_method="hist",
                        eval_metric="logloss", n_jobs=2, random_state=SEED) for depth in (2, 4)),
    ]


def best_threshold(labels: np.ndarray, probabilities: np.ndarray) -> tuple[float, float, float]:
    """Maximize positive-class F1, then recall, over observed OOF probabilities."""
    precision, recall, thresholds = precision_recall_curve(labels, probabilities)
    precision, recall = precision[:-1], recall[:-1]
    f1 = np.divide(2 * precision * recall, precision + recall, out=np.zeros_like(recall),
                   where=(precision + recall) > 0)
    index = np.lexsort((recall, f1.round(14)))[-1]
    return float(f1[index]), float(recall[index]), float(thresholds[index])


def train() -> AcademicRiskModel:
    train_data, _ = prepare_splits(seed=SEED)
    features = train_data.loc[:, list(FEATURES)]
    labels = train_data[TARGET].to_numpy()
    folds = StratifiedKFold(n_splits=5, shuffle=True, random_state=SEED)
    best_rank = (-1.0, -1.0)
    results = []
    for classifier in candidates():
        pipeline = Pipeline([("preprocess", build_preprocessor()), ("classifier", classifier)])
        scores = cross_val_predict(pipeline, features, labels, cv=folds, method="predict_proba")[:, 1]
        f1, recall, threshold = best_threshold(labels, scores)
        config = {k: v for k, v in classifier.get_params().items()
                  if k in {"C", "n_estimators", "max_depth", "min_samples_leaf", "learning_rate"}}
        result = {"classifier": type(classifier).__name__, "parameters": config,
                  "oof_f1": f1, "oof_recall": recall, "threshold": threshold}
        results.append(result)
        LOGGER.info("%s %s: OOF F1 %.4f, recall %.4f", result["classifier"], config, f1, recall)
        rank = (round(f1, 14), recall)
        if rank > best_rank:
            best_rank, winner, best_pipeline = rank, result, pipeline

    best_pipeline.fit(features, labels)
    versions = runtime_versions()
    metadata = {"winner": winner, "candidates": results, "folds": 5, "seed": SEED,
                "train_sha256": file_digest(TRAIN_DATA)}
    # Include the fitted estimator to distinguish retrains after code or feature changes.
    from joblib import hash as model_hash
    fingerprint = json.dumps([metadata, versions, model_hash(best_pipeline)], sort_keys=True)
    model_version = "academic-risk-v1-" + hashlib.sha256(fingerprint.encode()).hexdigest()[:12]
    model = AcademicRiskModel(best_pipeline, winner["threshold"], model_version, FEATURES,
                              versions, file_digest(TEST_DATA), metadata)
    model.save()
    LOGGER.info("Saved %s to %s", model_version, MODEL_PATH)
    return model


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    train()
