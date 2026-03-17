from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class Finding(BaseModel):
    """Read-only anomaly emitted by PRGX1."""

    model_config = ConfigDict(extra='forbid', strict=True)

    id: str
    source: str
    category: str
    severity: str
    description: str
    file_paths: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class IssueReport(BaseModel):
    """Bundle of findings published to the AetherBus."""

    model_config = ConfigDict(extra='forbid', strict=True)

    id: str
    source: str
    findings: list[Finding] = Field(default_factory=list)
    summary: str
    target: str
    metadata: dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
