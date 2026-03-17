from __future__ import annotations

from typing import Any


def build_fix_plan(findings: dict[str, Any]) -> list[dict[str, str]]:
    """Create explicit and minimal fix operations from PRGX1 findings."""

    fix_plan: list[dict[str, str]] = []
    for issue in findings.get('structural_issues', []):
        if not isinstance(issue, str):
            continue
        if issue.startswith('Missing __init__.py in '):
            folder = issue.replace('Missing __init__.py in ', '', 1)
            fix_plan.append({'path': f'{folder}/__init__.py', 'content': ''})
    return fix_plan
