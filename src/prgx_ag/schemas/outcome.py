from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class ProcessingOutcome(BaseModel):
    model_config = ConfigDict(extra="forbid")

    agent_name: str
    envelope_id: str
    success: bool
    execution_time: float
    revenue_generated: float
    message: str
    details: dict[str, Any] = Field(default_factory=dict)
