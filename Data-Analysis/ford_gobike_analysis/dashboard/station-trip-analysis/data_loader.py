"""
data_loader.py – High-Performance Data Ingestion Layer (Supabase + Smart Fallback)
==================================================================================
Directly loads Member 5 analytical fields from Supabase (gold.trip_analytics).
Optimized to fetch only needed transit & station columns in ~2-3 seconds,
with graceful local CSV fallback if offline.
"""

from __future__ import annotations

import functools
import logging
import os
from pathlib import Path
import pandas as pd
from dotenv import load_dotenv

from config import DATA_PATH, REQUIRED_COLUMNS, COORDINATE_COLUMNS
from utils.data_processing import normalize_station_name, generate_routes

logger = logging.getLogger(__name__)

# Load environment variables from .env
load_dotenv()

# Columns specifically needed for Member 5 Station & Trip Analytics
_M5_COLUMNS = [
    "start_station_name",
    "end_station_name",
    "start_latitude",
    "start_longitude",
    "end_latitude",
    "end_longitude",
    "user_type",
]


def _standardize_column_names(df: pd.DataFrame) -> pd.DataFrame:
    """Normalize coordinate column names to internal standard."""
    rename_map = {
        "start_latitude": "start_station_latitude",
        "start_longitude": "start_station_longitude",
        "end_latitude": "end_station_latitude",
        "end_longitude": "end_station_longitude",
    }
    rename_actual = {k: v for k, v in rename_map.items() if k in df.columns and v not in df.columns}
    if rename_actual:
        df = df.rename(columns=rename_actual)
    return df


def validate_dataset(df: pd.DataFrame) -> None:
    """Validate that required station and coordinate columns exist."""
    missing_required = REQUIRED_COLUMNS - set(df.columns)
    if missing_required:
        raise ValueError(
            f"[Member 5 Validation Error] Missing required columns: {sorted(missing_required)}. "
            f"Available columns: {sorted(df.columns.tolist())}"
        )


def _load_from_supabase() -> pd.DataFrame | None:
    """Query essential columns from Supabase gold.trip_analytics view with connection pooling."""
    db_url = os.getenv("DATABASE_URL")
    if not db_url or "XXXX" in db_url:
        return None

    try:
        from sqlalchemy import create_engine
        engine = create_engine(
            db_url,
            pool_pre_ping=True,
            connect_args={"connect_timeout": 15},
        )

        cols_str = ", ".join(_M5_COLUMNS)
        query = f"SELECT {cols_str} FROM gold.trip_analytics"
        
        print("\n" + "=" * 65, flush=True)
        print(">> [SUPABASE LIVE CONNECTION] Querying 'gold.trip_analytics'...", flush=True)
        df = pd.read_sql(query, engine)
        if not df.empty:
            print(f">> [SUCCESS] Loaded {len(df):,} trips directly from Supabase Cloud Database!", flush=True)
            print("=" * 65 + "\n", flush=True)
            return _standardize_column_names(df)

    except Exception as err:
        print(f">> [WARNING] Supabase query failed: {err}. Using local fallback.", flush=True)
        logger.warning("[Member 5] Supabase query failed: %s. Using local fallback.", err)

    return None


@functools.lru_cache(maxsize=1)
def load_clean_data(csv_path: Path | str | None = None) -> pd.DataFrame:
    """
    Single-load, high-performance cached loader.
    Prioritizes Supabase Cloud Database; falls back to local CSV if unavailable.
    """
    df = None

    # 1. Attempt Supabase fetch
    if csv_path is None:
        df = _load_from_supabase()

    # 2. Local fallback if Supabase unavailable
    if df is None:
        resolved_path = Path(csv_path) if csv_path else DATA_PATH
        if not resolved_path.exists():
            # Try preprocessing folder from team repo
            repo_csv = Path(__file__).resolve().parent.parent.parent / "preprocessing" / "cleaned_fordgobike_master.csv"
            if repo_csv.exists():
                resolved_path = repo_csv
            else:
                raise FileNotFoundError(f"Dataset not found at {resolved_path} and Supabase unavailable.")

        logger.info("[Member 5] Loading from local CSV: %s", resolved_path)
        sample = pd.read_csv(resolved_path, nrows=1)
        dtype_dict = {"user_type": "category"} if "user_type" in sample.columns else {}
        df = pd.read_csv(resolved_path, dtype=dtype_dict, low_memory=False)
        df = _standardize_column_names(df)

    # 3. Validation
    validate_dataset(df)

    # 4. Clean normalization
    df["start_station_name"] = normalize_station_name(df["start_station_name"])
    df["end_station_name"] = normalize_station_name(df["end_station_name"])

    # 5. Route generation
    if "route" not in df.columns:
        df["route"] = generate_routes(df)
    else:
        if df["route"].astype(str).str.contains(r"\bnan\b", case=False, regex=True).any():
            df["route"] = generate_routes(df)

    # 6. Filter empty stations
    df = df[df["start_station_name"].notna() | df["end_station_name"].notna()].copy()

    if "user_type" in df.columns and df["user_type"].dtype != "category":
        df["user_type"] = df["user_type"].astype("category")

    logger.info("[Member 5] Ready with %d valid trips.", len(df))
    return df
