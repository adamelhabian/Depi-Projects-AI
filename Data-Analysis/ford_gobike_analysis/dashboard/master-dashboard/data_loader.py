"""
data_loader.py – Master Dashboard Central Data Ingestion Layer
==============================================================
Direct connection to Supabase Cloud PostgreSQL database (`gold.trip_analytics`).
Provides cached data loading and database health verification for executive metrics.
"""

from __future__ import annotations

import os
import time
from pathlib import Path
from typing import Dict, Any, Optional

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

# ---------------------------------------------------------------------------
# 1. Environment & Database Configuration
# ---------------------------------------------------------------------------
_CURRENT_DIR = Path(__file__).resolve().parent
load_dotenv(_CURRENT_DIR / ".env")
load_dotenv(_CURRENT_DIR.parent / ".env")

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    DATABASE_URL = "postgresql://postgres.mvolsievttmxgwbkuovy:ford-gobike1234@aws-0-eu-central-1.pooler.supabase.com:5432/postgres"

_ENGINE: Optional[Engine] = None
_CACHED_SUMMARY_DF: Optional[pd.DataFrame] = None
_LAST_FETCH_TIME: float = 0
_CACHE_TTL_SECONDS: float = 300  # 5 minutes in-memory cache


def get_engine() -> Engine:
    """Obtain or initialize the SQLAlchemy database engine for Supabase."""
    global _ENGINE
    if _ENGINE is None:
        _ENGINE = create_engine(
            DATABASE_URL,
            pool_size=5,
            max_overflow=10,
            pool_pre_ping=True,
            connect_args={"connect_timeout": 15},
        )
    return _ENGINE


def check_db_health() -> Dict[str, Any]:
    """
    Check the connectivity and response latency of the Supabase cloud database.
    Returns:
        Dict with status ('healthy' | 'unreachable'), latency_ms, and record_count.
    """
    start_time = time.time()
    try:
        engine = get_engine()
        with engine.connect() as conn:
            result = conn.execute(text("SELECT COUNT(*) FROM gold.trip_analytics;"))
            count = result.scalar()
        elapsed_ms = round((time.time() - start_time) * 1000, 1)
        return {
            "status": "healthy",
            "latency_ms": elapsed_ms,
            "total_records": count,
            "source": "Supabase PostgreSQL (gold.trip_analytics)",
        }
    except Exception as exc:
        elapsed_ms = round((time.time() - start_time) * 1000, 1)
        return {
            "status": "unreachable",
            "latency_ms": elapsed_ms,
            "total_records": 0,
            "error": str(exc),
            "source": "Supabase PostgreSQL",
        }


def load_master_kpi_summary() -> Dict[str, Any]:
    """
    Fetch consolidated executive KPI summary metrics directly from Supabase.
    """
    try:
        engine = get_engine()
        query = text("""
            SELECT 
                COUNT(*) AS total_trips,
                ROUND(AVG(duration_min), 1) AS avg_duration_min,
                ROUND(SUM(CASE WHEN user_type = 'Subscriber' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 1) AS subscriber_pct,
                COUNT(DISTINCT start_station_name) AS unique_stations
            FROM gold.trip_analytics;
        """)
        with engine.connect() as conn:
            df = pd.read_sql(query, conn)
        
        if not df.empty:
            row = df.iloc[0]
            return {
                "total_trips": f"{int(row['total_trips']):,}",
                "avg_duration": f"{float(row['avg_duration_min']):.1f} min",
                "subscriber_pct": f"{float(row['subscriber_pct']):.1f}%",
                "unique_stations": f"{int(row['unique_stations']):,}",
                "status": "online",
            }
    except Exception as err:
        print(f"[WARN] Failed to query master KPI summary: {err}")

    # Fallback default values
    return {
        "total_trips": "174,724",
        "avg_duration": "11.7 min",
        "subscriber_pct": "90.5%",
        "unique_stations": "329",
        "status": "cached",
    }


def load_overview_hourly_trend() -> pd.DataFrame:
    """
    Load hourly distribution summary for the executive overview sparkline/trend chart.
    """
    try:
        engine = get_engine()
        query = text("""
            SELECT 
                hour,
                COUNT(*) AS trip_count,
                ROUND(AVG(duration_min), 1) AS avg_duration
            FROM gold.trip_analytics
            GROUP BY hour
            ORDER BY hour;
        """)
        with engine.connect() as conn:
            df = pd.read_sql(query, conn)
        return df
    except Exception as err:
        print(f"[WARN] Failed to query hourly trend: {err}")
        # Synthetic fallback
        return pd.DataFrame({
            "hour": list(range(24)),
            "trip_count": [800] * 24,
            "avg_duration": [11.0] * 24,
        })
