from __future__ import annotations

from datetime import UTC, datetime, timedelta


def build_cutoff_timestamp(retention_days: int) -> str:
    return (datetime.now(UTC) - timedelta(days=retention_days)).isoformat()
