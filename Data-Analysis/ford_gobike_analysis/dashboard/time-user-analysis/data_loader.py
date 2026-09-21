"""
data_loader.py – Cloud Ingestion Layer (Supabase Exclusively)
=============================================================
Exclusively loads Member 4 Time & User analytical fields directly
from Supabase Cloud PostgreSQL database (`gold.trip_analytics`).

Zero reliance on local CSV files.
"""

from __future__ import annotations

import functools
import logging
import os
from pathlib import Path
import pandas as pd
from dotenv import load_dotenv

from config import REQUIRED_COLUMNS

logger = logging.getLogger(__name__)

# Ensure .env is loaded from module directory
_CURRENT_DIR = Path(__file__).resolve().parent
_ENV_PATH = _CURRENT_DIR / ".env"
if _ENV_PATH.exists():
    load_dotenv(dotenv_path=_ENV_PATH)
else:
    load_dotenv()

# Columns specifically needed for Member 4 Time & User Analytics
_QUERY_COLUMNS = [
    "user_type",
    "start_hour AS hour",
    "day_name AS day_of_week",
    "weekend_flag",
    "duration_min",
    "member_age",
    "member_gender",
    "age_group",
    """CASE 
        WHEN start_latitude > 37.7 AND start_longitude < -122.35 THEN 'San Francisco'
        WHEN start_latitude > 37.75 AND start_longitude >= -122.35 THEN 'East Bay (Oakland/Berkeley)'
        WHEN start_latitude < 37.45 THEN 'San Jose'
        ELSE 'San Francisco'
    END AS region""",
]


def validate_dataset(df: pd.DataFrame) -> None:
    """Validate that required analytical columns exist."""
    missing_required = set(REQUIRED_COLUMNS) - set(df.columns)
    if missing_required:
        raise ValueError(
            f"[Validation Error] Missing required columns: {sorted(missing_required)}. "
            f"Available columns: {sorted(df.columns.tolist())}"
        )


def _load_from_supabase() -> pd.DataFrame:
    """
    Directly query Supabase gold.trip_analytics view.
    Raises RuntimeError if connection fails (no CSV fallback).
    """
    db_url = os.getenv("DATABASE_URL")
    if not db_url or "XXXX" in db_url:
        db_url = "postgresql://postgres.mvolsievttmxgwbkuovy:ford-gobike1234@aws-0-eu-central-1.pooler.supabase.com:5432/postgres"

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

        return df

    except Exception as err:
        logger.error("[Supabase Error] Direct cloud database query failed: %s", err)
        raise RuntimeError(
            f"Failed to fetch data from Supabase Cloud Database: {err}. "
            f"This dashboard strictly relies on Supabase (CSV disabled)."
        ) from err


_CACHE_DIR = _CURRENT_DIR.parent / ".cache"
_PARQUET_PATH = _CACHE_DIR / "time_user_cleaned.parquet"


@functools.lru_cache(maxsize=1)
def load_clean_data() -> pd.DataFrame:
    """
    Single-load, ultra-high-performance cached loader.
    Exclusively loads from local Parquet disk cache if available (<0.5s),
    or fetches directly from Supabase Cloud Database and creates the cache.
    """
    # 0. Check local Parquet cache for instant cold start
    if _PARQUET_PATH.exists():
        try:
            logger.info("[Member 4] Loading from instant Parquet cache: %s", _PARQUET_PATH)
            df = pd.read_parquet(_PARQUET_PATH)
            if not df.empty and len(df) > 100000:
                print(f">> [PARQUET CACHE HIT] Loaded {len(df):,} time-user trips in <0.6s from {_PARQUET_PATH.name}", flush=True)
                return df
        except Exception as cache_err:
            logger.warning("[Member 4] Parquet cache read failed (%s); re-fetching from Supabase.", cache_err)

    df = _load_from_supabase()

    validate_dataset(df)

    # Cast categoricals and clean types for ultra-fast filtering & plotting
    if "user_type" in df.columns and df["user_type"].dtype != "category":
        df["user_type"] = df["user_type"].astype("category")

    if "member_gender" in df.columns and df["member_gender"].dtype != "category":
        df["member_gender"] = df["member_gender"].astype("category")

    if "age_group" in df.columns and df["age_group"].dtype != "category":
        df["age_group"] = df["age_group"].astype("category")

    if "region" in df.columns and df["region"].dtype != "category":
        df["region"] = df["region"].astype("category")

    # Persist to Parquet disk cache for instant subsequent runs
    try:
        _CACHE_DIR.mkdir(parents=True, exist_ok=True)
        df.to_parquet(_PARQUET_PATH, engine="pyarrow", compression="snappy")
        logger.info("[Member 4] Saved instant Parquet cache: %s", _PARQUET_PATH)
    except Exception as save_err:
        logger.warning("[Member 4] Failed to save Parquet cache: %s", save_err)

    logger.info("[Member 4] Ready with %d valid trips loaded from Supabase.", len(df))
    return df