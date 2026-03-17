from pathlib import Path

import pytest

from prgx_ag.orchestrator import PRGXAGNexus


@pytest.mark.asyncio
async def test_full_nexus_cycle(tmp_path: Path) -> None:
    (tmp_path / "README.md").write_text("x", encoding="utf-8")
    (tmp_path / "src" / "prgx_ag").mkdir(parents=True)
    (tmp_path / "src" / "prgx_ag" / "__init__.py").write_text("", encoding="utf-8")
    (tmp_path / "tests").mkdir()

    nexus = PRGXAGNexus(root=tmp_path)
    await nexus.run_once()

    topics = [topic for topic, _ in nexus.bus.history]
    assert "porisjem.issue_reported" in topics
    assert "porisjem.execute_fix" in topics
    assert "porisjem.fix_completed" in topics
