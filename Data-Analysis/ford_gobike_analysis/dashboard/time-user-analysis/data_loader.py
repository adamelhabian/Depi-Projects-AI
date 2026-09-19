"""
data_loader.py – Direct Cloud Ingestion Layer (Supabase Exclusively)
====================================================================
Exclusively loads analytical dataset directly from the Supabase Cloud
PostgreSQL database (`gold.trip_analytics`).

Zero reliance on local CSV files: All metrics, demographic distributions,
and temporal trends are computed in-memory directly from the cloud data.
"""

from __future__ import annotations

import functools
import logging
import os
from pathlib import Path
import pandas as pd
from dotenv import load_dotenv

from config import REQUIRED_COLUMNS, COORDINATE_COLUMNS
from utils.data_processing import (
    normalize_station_name,
    generate_routes,
)

logger = logging.getLogger(__name__)

# Ensure .env is loaded from module directory
_ENV_PATH = Path(__file__).resolve().parent / ".env"
if _ENV_PATH.exists():
    load_dotenv(dotenv_path=_ENV_PATH)
else:
    load_dotenv()

# Essential columns queried directly from Supabase gold.trip_analytics
_QUERY_COLUMNS = [
    "start_station_name",
    "end_station_name",
    "start_latitude",
    "start_longitude",
    "end_latitude",
    "end_longitude",
    "user_type",
    "start_hour AS hour",
    "day_name AS day_of_week",
    "weekend_flag",
    "duration_min",
    "member_age",
    "member_gender",
    "age_group",
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
    """Validate that required station and analytical columns exist."""
    missing_required = set(REQUIRED_COLUMNS) - set(df.columns)
    if missing_required:
        raise ValueError(
            f"[Supabase Validation Error] Missing required columns: {sorted(missing_required)}. "
            f"Available columns: {sorted(df.columns.tolist())}"
        )


def _load_from_supabase() -> pd.DataFrame:
    """
    Directly query Supabase gold.trip_analytics view with connection pooling.
    Raises RuntimeError if connection fails (no CSV fallback).
    """
    db_url = os.getenv("DATABASE_URL")
    if not db_url or "XXXX" in db_url:
        raise RuntimeError(
            "DATABASE_URL is not configured in .env. Supabase connection is strictly required."
        )

    try:
        from sqlalchemy import create_engine
        engine = create_engine(
            db_url,
            pool_pre_ping=True,
            connect_args={"connect_timeout": 30},
        )

        cols_str = ", ".join(_QUERY_COLUMNS)
        query = f"SELECT {cols_str} FROM gold.trip_analytics"

        print("\n" + "=" * 65, flush=True)
        print(">> [SUPABASE LIVE CONNECTION] Querying 'gold.trip_analytics'...", flush=True)
        df = pd.read_sql(query, engine)

        if df.empty:
            raise RuntimeError("Supabase returned an empty dataset from gold.trip_analytics.")

        print(f">> [SUCCESS] Loaded {len(df):,} trips directly from Supabase Cloud Database!", flush=True)
        print("=" * 65 + "\n", flush=True)

        return _standardize_column_names(df)

    except Exception as err:
        logger.error("[Supabase Error] Direct cloud database query failed: %s", err)
        raise RuntimeError(
            f"Failed to fetch data from Supabase Cloud Database: {err}. "
            f"This dashboard strictly relies on Supabase (CSV disabled)."
        ) from err


@functools.lru_cache(maxsize=1)
def load_clean_data() -> pd.DataFrame:
    """
    Single-load, high-performance cached loader.
    Exclusively loads from Supabase Cloud Database and caches in memory.
    """
    # 1. Fetch live data from Supabase
    df = _load_from_supabase()

    # 2. Validation
    validate_dataset(df)

    # 3. Clean normalization
    df["start_station_name"] = normalize_station_name(df["start_station_name"])
    df["end_station_name"] = normalize_station_name(df["end_station_name"])

    # 4. Route generation
    if "route" not in df.columns:
        df["route"] = generate_routes(df)
    else:
        if df["route"].astype(str).str.contains(r"\bnan\b", case=False, regex=True).any():
            df["route"] = generate_routes(df)

    # 5. Filter empty stations
    df = df[df["start_station_name"].notna() | df["end_station_name"].notna()].copy()

    # 6. Optimize data types for fast filtering and plotting
    if "user_type" in df.columns and df["user_type"].dtype != "category":
        df["user_type"] = df["user_type"].astype("category")

    if "member_gender" in df.columns and df["member_gender"].dtype != "category":
        df["member_gender"] = df["member_gender"].astype("category")

    if "age_group" in df.columns and df["age_group"].dtype != "category":
        df["age_group"] = df["age_group"].astype("category")

    logger.info("[Member 4] Ready with %d valid trips loaded from Supabase.", len(df))
    return df