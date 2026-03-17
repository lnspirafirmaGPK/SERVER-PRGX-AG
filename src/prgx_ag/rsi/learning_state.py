from dataclasses import dataclass, field

from prgx_ag.rsi.gems import GemOfWisdom


@dataclass
class LearningState:
    parameters: dict[str, float] = field(default_factory=lambda: {"stability": 1.0, "efficiency": 1.0})

    def apply_gem(self, gem: GemOfWisdom) -> bool:
        if not gem.safe_to_apply:
            return False
        for key, delta in gem.param_update.items():
            current = self.parameters.get(key, 1.0)
            self.parameters[key] = max(0.1, min(10.0, current + delta))
        return True
