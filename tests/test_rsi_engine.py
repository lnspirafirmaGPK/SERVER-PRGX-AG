from prgx_ag.rsi import LearningState, RSIEngine
from prgx_ag.schemas.outcome import ProcessingOutcome


def test_rsi_generates_and_applies_safe_gem() -> None:
    engine = RSIEngine()
    state = LearningState()
    outcome = ProcessingOutcome(
        agent_name="PRGX2",
        envelope_id="e",
        success=True,
        execution_time=1.0,
        revenue_generated=3.0,
        message="ok",
    )
    gem = engine.analyze(outcome)
    assert gem is not None
    assert state.apply_gem(gem) is True
    assert state.parameters["efficiency"] > 1.0
