from prgx_ag.schemas import ProcessingOutcome
from prgx_ag.services.healing_intent_builder import build_fix_plan
from prgx_ag.services.narrative_builder import build_commit_style_narrative


def test_healing_intent_generation_for_missing_init() -> None:
    findings = {'structural_issues': ['Missing __init__.py in src/prgx_ag/new_pkg']}
    plan = build_fix_plan(findings)
    assert plan == [{'path': 'src/prgx_ag/new_pkg/__init__.py', 'content': ''}]


def test_commit_narrative_generation() -> None:
    outcome = ProcessingOutcome(
        agent_name='PRGX2',
        envelope_id='abc123',
        success=True,
        execution_time=0.2,
        message='Safe fixes applied',
    )
    narrative = build_commit_style_narrative(outcome)
    assert 'fix:' in narrative
    assert 'abc123' in narrative
