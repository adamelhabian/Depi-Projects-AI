"""
data_loader.py – Data Ingestion and Validation Layer
====================================================
Loads Member 2's processed dataset as the single source of truth.
Validates required columns, normalizes station names, and generates routes cleanly.

Contract:
  - Preserves shared columns without unexpected mutations or renames.
  - Generates 'route' only for valid non-null origin & destination pairs.
  - Removes unused Member 5 derived fields (e.g. is_round_trip) to respect Member 4's scope.
  - Uses functools.lru_cache for high-performance single-load caching.
"""

from __future__ import annotations

import functools
import logging
from pathlib import Path
import pandas as pd

from config import DATA_PATH, REQUIRED_COLUMNS, COORDINATE_COLUMNS
from utils.data_processing import normalize_station_name, generate_routes

logger = logging.getLogger(__name__)


def validate_dataset(df: pd.DataFrame) -> None:
    """
    Validate that the incoming dataframe meets Member 5 requirements.

    Parameters
    ----------
    df : pd.DataFrame
        Dataset produced by Member 2.

    Raises
    ------
    ValueError
        If any required column is missing.
    """
    missing_required = REQUIRED_COLUMNS - set(df.columns)
    if missing_required:
        raise ValueError(
            f"[Member 5 Validation Error] Missing required columns: {sorted(missing_required)}. "
            f"Available columns: {sorted(df.columns.tolist())}"
        )

    missing_coords = COORDINATE_COLUMNS - set(df.columns)
    if missing_coords:
        logger.warning(
            "[Member 5 Warning] Missing coordinate columns: %s. "
            "Geospatial map visualization will degrade gracefully.",
            sorted(missing_coords)
        )


@functools.lru_cache(maxsize=1)
def load_clean_data(csv_path: Path | str | None = None) -> pd.DataFrame:
    """
    Load, validate, and normalize Member 2's processed dataset.

    Parameters
    ----------
    csv_path : Path or str, optional
        Custom path to CSV; defaults to DATA_PATH configured in config.py.

    Returns
    -------
    pd.DataFrame
        Cleaned dataframe ready for Station & Trip Analysis.
    """
    resolved_path = Path(csv_path) if csv_path else DATA_PATH

    if not resolved_path.exists():
        raise FileNotFoundError(
            f"[Member 5 Data Error] Dataset not found at: {resolved_path}.\n"
            f"Verify that Member 2's cleaned dataset exists at this location."
        )

    logger.info("[Member 5] Loading dataset from %s ...", resolved_path)

    # Use categorical types on low-cardinality filters to conserve memory
    dtype_dict = {}
    # Only assign dtype if column exists in the file header
    sample = pd.read_csv(resolved_path, nrows=1)
    if "user_type" in sample.columns:
        dtype_dict["user_type"] = "category"

    df = pd.read_csv(
        resolved_path,
        dtype=dtype_dict,
        low_memory=False,
    )

    # 1. Validation layer
    validate_dataset(df)

    # 2. Station normalization (strip, remove empty strings/fake nan)
    df["start_station_name"] = normalize_station_name(df["start_station_name"])
    df["end_station_name"] = normalize_station_name(df["end_station_name"])

    # 3. Clean route generation (only when both origin and destination are valid)
    if "route" not in df.columns:
        df["route"] = generate_routes(df)
    else:
        # Validate existing route column or regenerate if it contains 'nan'
        if df["route"].astype(str).str.contains(r"\bnan\b", case=False, regex=True).any():
            df["route"] = generate_routes(df)

    # 4. Filter out uninformative rows where both stations are missing
    df = df[df["start_station_name"].notna() | df["end_station_name"].notna()].copy()

    logger.info(
        "[Member 5] Loaded %d valid trips across %d columns.",
        len(df), len(df.columns)
    )
    return df
