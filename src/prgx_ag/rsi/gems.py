from pydantic import BaseModel, ConfigDict


class GemOfWisdom(BaseModel):
    model_config = ConfigDict(extra="forbid")

    lesson: str
    param_update: dict[str, float]
    scope: str
    safe_to_apply: bool = True
