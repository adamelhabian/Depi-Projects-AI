"""Project-relative paths shared by training, evaluation, and inference."""

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA = DATA_DIR / "raw" / "student_academic_risk.csv"
TRAIN_DATA = DATA_DIR / "processed" / "academic_risk_train.csv"
TEST_DATA = DATA_DIR / "processed" / "academic_risk_test.csv"
ML_DIR = PROJECT_ROOT / "src" / "machine_learning"
MODEL_PATH = ML_DIR / "models" / "saved_models" / "academic_risk_pipeline.joblib"
METRICS_PATH = ML_DIR / "evaluation" / "metrics.json"
ALERT_DB = PROJECT_ROOT / "var" / "academic_alerts.sqlite3"
