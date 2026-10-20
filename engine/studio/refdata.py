"""Read-only access to the Saracen Bridge reference database (data/studio_reference.db)."""
from __future__ import annotations

import os
import sqlite3
import threading
import sys
from functools import lru_cache
from pathlib import Path


def app_root() -> Path:
    """Repository root in development; the unpacked bundle when frozen by PyInstaller."""
    if getattr(sys, "frozen", False):
        return Path(getattr(sys, "_MEIPASS", Path(sys.executable).parent))
    return Path(__file__).resolve().parents[2]


DB_PATH = Path(os.environ.get("STUDIO_REFERENCE_DB", app_root() / "data" / "studio_reference.db"))


_LOCAL = threading.local()


def _conn() -> sqlite3.Connection:
    """One read-only connection per thread. A single shared one (to 1.1.1) failed when two threads read at once:
    Tim's log, 20 Oct, the Sales warm-up thread got "sqlite3.InterfaceError: bad parameter or other API misuse"."""
    conn = getattr(_LOCAL, "conn", None)
    if conn is None:
        conn = sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        _LOCAL.conn = conn
    return conn


def rows(sql: str, *args) -> list[dict]:
    return [dict(r) for r in _conn().execute(sql, args)]


def programme_rule(programme_id: str) -> dict:
    found = rows("SELECT * FROM inc_programme_rules WHERE programme_id = ?", programme_id)
    if not found:
        raise KeyError(f"No programme rule for {programme_id}")
    return found[0]


def has_programme(programme_id) -> bool:
    return bool(programme_id) and bool(rows("SELECT 1 FROM inc_programme_rules WHERE programme_id = ?", programme_id))


def all_programme_rules() -> list[dict]:
    return rows("SELECT * FROM inc_programme_rules")


def fx_usd_per_unit(currency: str) -> float:
    """USD per one unit of `currency`, derived from the dated ECB units-per-EUR table."""
    usd = rows("SELECT ecb_units_per_eur FROM inc_fx_financing WHERE currency = 'USD'")[0]["ecb_units_per_eur"]
    cur = rows("SELECT ecb_units_per_eur FROM inc_fx_financing WHERE currency = ?", currency)
    if not cur:
        raise KeyError(f"No controlled FX rate for {currency}")
    return usd / cur[0]["ecb_units_per_eur"]


def vocab(name: str) -> list[str]:
    return [r["value"] for r in rows("SELECT value FROM vocab WHERE vocab = ? ORDER BY ordinal", name)]
