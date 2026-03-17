from __future__ import annotations

from datetime import datetime, timezone

from pydantic import BaseModel, ConfigDict, Field


class RepairNarrative(BaseModel):
    """Human-readable story of one healing cycle."""

    model_config = ConfigDict(extra='forbid', strict=True)

    title: str
    detected: str
    repaired: str
    learned: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
