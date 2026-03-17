from pydantic import BaseModel, ConfigDict


class Settings(BaseModel):
    model_config = ConfigDict(extra="forbid")

    log_level: str = "INFO"
    event_history_size: int = 100
