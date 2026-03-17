from prgx_ag.rsi.gems import GemOfWisdom
from prgx_ag.schemas.outcome import ProcessingOutcome


class RSIEngine:
    def analyze(self, outcome: ProcessingOutcome) -> GemOfWisdom | None:
        if outcome.success and outcome.revenue_generated > 0:
            return GemOfWisdom(
                lesson="Successful healing improved value delivery.",
                param_update={"efficiency": 0.2, "stability": 0.1},
                scope="runtime",
            )
        if outcome.success and outcome.execution_time > 2.0:
            return GemOfWisdom(
                lesson="Fix succeeded but was slow; optimize path.",
                param_update={"efficiency": 0.1},
                scope="runtime",
            )
        if not outcome.success:
            return GemOfWisdom(
                lesson="Failure indicates need for safer fallback.",
                param_update={"stability": 0.1},
                scope="safety",
            )
        return None
