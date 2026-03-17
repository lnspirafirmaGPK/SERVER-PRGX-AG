from prgx_ag.schemas.outcome import ProcessingOutcome


def build_commit_style_narrative(outcome: ProcessingOutcome) -> str:
    status = "feat" if outcome.success else "fix"
    return f"{status}(prgx-ag): {outcome.message} [agent={outcome.agent_name}]"
