from pathlib import Path

import pytest

from prgx_ag.agents.prgx1_sentry import PRGX1Sentry
from prgx_ag.core.aetherbus import AetherBus


@pytest.mark.asyncio
async def test_prgx1_does_not_write_files(tmp_path: Path) -> None:
    (tmp_path / "README.md").write_text("x", encoding="utf-8")
    (tmp_path / "src" / "prgx_ag").mkdir(parents=True)
    (tmp_path / "src" / "prgx_ag" / "__init__.py").write_text("", encoding="utf-8")
    (tmp_path / "tests").mkdir()

    bus = AetherBus()
    sentry = PRGX1Sentry(bus=bus, root=tmp_path)
    before = set(p.name for p in tmp_path.glob("**/*") if p.is_file())
    await sentry.publish_issue_report()
    after = set(p.name for p in tmp_path.glob("**/*") if p.is_file())
    assert before == after
