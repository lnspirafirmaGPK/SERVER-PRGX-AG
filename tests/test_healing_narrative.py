from prgx_ag.schemas import ProcessingOutcome
from prgx_ag.services.github_bridge import format_pr_body, format_pr_title
from prgx_ag.services.healing_intent_builder import build_fix_plan
from prgx_ag.services.narrative_builder import build_commit_style_narrative


def test_healing_intent_generation_for_missing_init() -> None:
    findings = {'structural_issues': ['Missing __init__.py in src/prgx_ag/new_pkg']}
    plan = build_fix_plan(findings)
    assert plan == [
        {
            'path': 'src/prgx_ag/new_pkg/__init__.py',
            'content': '',
            'fix_class': 'structural.package_marker',
            'rationale': 'Restore the missing Python package marker required by the expected source tree.',
            'verification_commands': ['compileall', 'pytest', 'ruff', 'mypy'],
            'rollback_hint': 'Delete src/prgx_ag/new_pkg/__init__.py only if the directory should stop behaving as a Python package.',
            'source_issue': 'Missing __init__.py in src/prgx_ag/new_pkg',
        }
    ]


def test_commit_narrative_generation() -> None:
    outcome = ProcessingOutcome(
        agent_name='PRGX2',
        envelope_id='abc123',
        success=True,
        execution_time=0.2,
        message='Safe fixes applied',
        details={
            'fix_classes': ['structural.package_marker'],
            'verification_status': 'passed',
        },
    )
    narrative = build_commit_style_narrative(outcome)
    assert 'fix:' in narrative
    assert 'abc123' in narrative
    assert 'fix_classes=structural.package_marker' in narrative
    assert 'verification=passed' in narrative


def test_pr_body_generation_contains_governance_sections() -> None:
    title = format_pr_title(
        findings_summary={'summary': 'Missing package markers', 'target': 'repository', 'issue_count': 1},
        audit_result='approved',
        verification_result='passed',
        fix_classes=['structural.package_marker'],
    )
    body = format_pr_body(
        findings_summary={'summary': 'Missing package markers', 'target': 'repository', 'issue_count': 1},
        audit_result='approved',
        changed_files=['src/prgx_ag/new_pkg/__init__.py'],
        verification_result='passed',
        rollback_instructions=['Delete src/prgx_ag/new_pkg/__init__.py if the package marker is not needed.'],
        fix_classes=['structural.package_marker'],
        verification_commands=['compileall', 'pytest'],
    )
    assert 'approved' in title
    assert '### Findings summary' in body
    assert '### Audit result' in body
    assert '### Changed files' in body
    assert '### Verification result' in body
    assert '### Rollback instructions' in body
