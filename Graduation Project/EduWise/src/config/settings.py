# Centralized Configuration Management

import os
from dataclasses import dataclass, field
from pathlib import Path
from dotenv import load_dotenv

# Project root directory
PROJECT_ROOT = Path(__file__).resolve().parents[2]

# Load environment variables
load_dotenv(PROJECT_ROOT / ".env")


@dataclass(frozen=True)
class RAGSettings:

    # API Configuration
    groq_api_key: str = field(
        default_factory=lambda: os.getenv("GROQ_API_KEY", "")
    )
    gemini_api_key: str = field(
        default_factory=lambda: os.getenv("GEMINI_API_KEY", "")
    )

    # Model Configuration
    groq_model: str = field(
        default_factory=lambda: os.getenv(
            "GROQ_MODEL", "openai/gpt-oss-20b"
        )
    )
    embedding_model: str = field(
        default_factory=lambda: os.getenv(
            "EMBEDDING_MODEL", "gemini-embedding-001"
        )
    )
    embedding_dimension: int = field(
        default_factory=lambda: int(
            os.getenv("EMBEDDING_DIMENSION", "3072")
        )
    )

    # RAG Configuration
    chunk_size: int = field(
        default_factory=lambda: int(os.getenv("CHUNK_SIZE", "500"))
    )
    chunk_overlap: int = field(
        default_factory=lambda: int(os.getenv("CHUNK_OVERLAP", "50"))
    )
    top_k_chunks: int = field(
        default_factory=lambda: int(os.getenv("TOP_K_CHUNKS", "5"))
    )

    # Exam Configuration
    questions_per_type: int = field(
        default_factory=lambda: int(os.getenv("QUESTIONS_PER_TYPE", "5"))
    )
    default_difficulty: str = field(
        default_factory=lambda: os.getenv(
            "DEFAULT_DIFFICULTY", "Difficult"
        )
    )

    # Storage Configuration
    documents_dir: Path = field(
        default_factory=lambda: PROJECT_ROOT / "storage" / "documents"
    )
    generated_exams_dir: Path = field(
        default_factory=lambda: PROJECT_ROOT / "storage" / "generated_exams"
    )
    vector_indexes_dir: Path = field(
        default_factory=lambda: PROJECT_ROOT / "storage" / "vector_indexes"
    )

    # Question Types
    question_types: list[str] = field(
        default_factory=lambda: [
            "MCQ",
            "True/False",
            "Short Answer",
            "Fill in the Blanks",
            "Descriptive",
        ]
    )

    marks_per_type: dict[str, int] = field(
        default_factory=lambda: {
            "MCQ": 1,
            "True/False": 1,
            "Short Answer": 3,
            "Fill in the Blanks": 1,
            "Descriptive": 5,
        }
    )

    def create_storage_directories(self) -> None:
        self.documents_dir.mkdir(parents=True, exist_ok=True)
        self.generated_exams_dir.mkdir(parents=True, exist_ok=True)
        self.vector_indexes_dir.mkdir(parents=True, exist_ok=True)

    def validate(self) -> None:
        if not self.groq_api_key:
            raise ValueError("Missing GROQ_API_KEY in .env")

        if not self.gemini_api_key:
            raise ValueError("Missing GEMINI_API_KEY in .env")

        if self.chunk_size <= 0:
            raise ValueError("CHUNK_SIZE must be positive.")

        if not 0 <= self.chunk_overlap < self.chunk_size:
            raise ValueError(
                "CHUNK_OVERLAP must be non-negative and smaller than CHUNK_SIZE."
            )

        if self.top_k_chunks <= 0:
            raise ValueError("TOP_K_CHUNKS must be positive.")

        if self.questions_per_type <= 0:
            raise ValueError("QUESTIONS_PER_TYPE must be positive.")


# Create the global settings instance
settings = RAGSettings()

# Create storage directories
settings.create_storage_directories()
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
