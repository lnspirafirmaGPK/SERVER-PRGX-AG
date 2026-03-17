from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

from prgx_ag.schemas import GemOfWisdom

_DEFAULT_PARAMETERS: dict[str, float] = {
    "stability": 1.0,
    "efficiency": 1.0,
}


def _clamp_parameter(value: float) -> float:
    return max(0.1, min(10.0, float(value)))


def _coerce_parameters(raw: object) -> dict[str, float]:
    parameters = dict(_DEFAULT_PARAMETERS)

    if not isinstance(raw, dict):
        return parameters

    for key, value in raw.items():
        if isinstance(key, str) and isinstance(value, (int, float)):
            parameters[key] = _clamp_parameter(value)

    return parameters


@dataclass(slots=True)
class LearningState:
    parameters: dict[str, float] = field(
        default_factory=lambda: dict(_DEFAULT_PARAMETERS)
    )

    @classmethod
    def load(cls, path: Path) -> "LearningState":
        if not path.exists():
            return cls()

        try:
            raw = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return cls()

        return cls(parameters=_coerce_parameters(raw))

    def apply_gem(self, gem: GemOfWisdom) -> bool:
        if not gem.safe_to_apply:
            return False

        for key, delta in gem.param_update.items():
            if not isinstance(delta, (int, float)):
                return False

            current = self.parameters.get(key, 1.0)
            self.parameters[key] = _clamp_parameter(current + float(delta))

        return True

    def to_dict(self) -> dict[str, float]:
        return dict(self.parameters)

    def save(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps(self.to_dict(), indent=2, sort_keys=True),
            encoding="utf-8",
        )
