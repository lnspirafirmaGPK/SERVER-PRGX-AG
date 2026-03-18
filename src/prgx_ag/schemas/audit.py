from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from prgx_ag.schemas.enums import EthicalStatus


class AuditResult(BaseModel):
    model_config = ConfigDict(extra="forbid", validate_assignment=True)

    is_allowed: bool
    status: EthicalStatus
    reason: str | None = None
    suggested_action: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
