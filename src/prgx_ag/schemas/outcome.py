from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ProcessingOutcome(BaseModel):
    model_config = ConfigDict(extra="forbid", validate_assignment=True)

    agent_name: str
    envelope_id: str
    success: bool
    execution_time: float = Field(ge=0.0)
    revenue_generated: float = 0.0
    message: str
    details: dict[str, Any] = Field(default_factory=dict)

    @field_validator("agent_name", "envelope_id", "message")
    @classmethod
    def _normalize_non_empty_text(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("must not be blank")
        return value
