from pathlib import Path

import pytest

from prgx_ag.agents.prgx2_mechanic import PRGX2Mechanic
from prgx_ag.core.aetherbus import AetherBus
from prgx_ag.policy import PatimokkhaChecker
from prgx_ag.schemas import AuditStatus, Intent


@pytest.mark.asyncio
async def test_prgx2_requires_approved_intent(tmp_path: Path) -> None:
    mech = PRGX2Mechanic(bus=AetherBus(), root=tmp_path, checker=PatimokkhaChecker())
    payload = {
        "envelope_id": "e1",
        "intent": Intent(id="1", source_agent="a", description="safe fix", target_firma="repo"),
        "audit_status": AuditStatus.REJECTED,
    }
    out = await mech.apply_shadow_fix("repo", payload)
    assert out.success is False
    assert "not approved" in out.message
