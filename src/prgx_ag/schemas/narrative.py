from __future__ import annotations

from pydantic import BaseModel, ConfigDict, field_validator


class RepairNarrative(BaseModel):
    model_config = ConfigDict(extra="forbid", validate_assignment=True)

    title: str
    detected: str
    repaired: str
    learned: str

    @field_validator("title", "detected", "repaired", "learned")
    @classmethod
    def _normalize_text(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("must not be blank")
        return value
