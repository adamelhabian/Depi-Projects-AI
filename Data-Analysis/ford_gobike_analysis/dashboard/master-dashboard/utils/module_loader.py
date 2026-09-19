"""
utils/module_loader.py – Submodule Dynamic Integration Loader
=============================================================
Safely loads Member 5 (Station & Trip Analysis) and Member 4 (Time & User Analysis)
with isolated import namespaces, preventing module name collisions while preserving
zero modifications to either submodule codebase.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Callable, Tuple, Any

from config import STATION_MODULE_DIR, TIME_USER_MODULE_DIR

# Cached references
_STATION_LAYOUT_FN: Callable[[], Any] | None = None
_STATION_CALLBACKS_FN: Callable[[Any], None] | None = None

_TIME_USER_LAYOUT_FN: Callable[[], Any] | None = None
_TIME_USER_CALLBACKS_FN: Callable[[Any], None] | None = None


def _clean_colliding_modules():
    """Removes submodule namespaces from sys.modules before switching module contexts."""
    keys_to_clean = [
        k for k in list(sys.modules.keys())
        if k.startswith(("config", "data_loader", "utils", "charts", "components", "callbacks", "layout"))
        and not k.startswith("utils.module_loader")
    ]
    for k in keys_to_clean:
        sys.modules.pop(k, None)


def get_station_module() -> Tuple[Callable[[], Any], Callable[[Any], None]]:
    """
    Dynamically loads and returns (create_layout, register_callbacks) for Station & Trip Analysis.
    """
    global _STATION_LAYOUT_FN, _STATION_CALLBACKS_FN

    if _STATION_LAYOUT_FN is not None and _STATION_CALLBACKS_FN is not None:
        return _STATION_LAYOUT_FN, _STATION_CALLBACKS_FN

    old_path = list(sys.path)
    _clean_colliding_modules()

    try:
        sys.path.insert(0, str(STATION_MODULE_DIR))
        import layout as st_layout
        from callbacks.dashboard_callbacks import register_callbacks as st_callbacks

        _STATION_LAYOUT_FN = st_layout.create_layout
        _STATION_CALLBACKS_FN = st_callbacks
    finally:
        sys.path = old_path

    return _STATION_LAYOUT_FN, _STATION_CALLBACKS_FN


def get_time_user_module() -> Tuple[Callable[[], Any], Callable[[Any], None]]:
    """
    Dynamically loads and returns (create_layout, register_callbacks) for Time & User Analysis.
    """
    global _TIME_USER_LAYOUT_FN, _TIME_USER_CALLBACKS_FN

    if _TIME_USER_LAYOUT_FN is not None and _TIME_USER_CALLBACKS_FN is not None:
        return _TIME_USER_LAYOUT_FN, _TIME_USER_CALLBACKS_FN

    old_path = list(sys.path)
    _clean_colliding_modules()

    try:
        sys.path.insert(0, str(TIME_USER_MODULE_DIR))
        import layout as tu_layout
        from callbacks.dashboard_callbacks import register_callbacks as tu_callbacks

        _TIME_USER_LAYOUT_FN = tu_layout.create_layout
        _TIME_USER_CALLBACKS_FN = tu_callbacks
    finally:
        sys.path = old_path

    return _TIME_USER_LAYOUT_FN, _TIME_USER_CALLBACKS_FN
