from prgx_ag.agents.prgx3_diplomat import PRGX3Diplomat
from prgx_ag.core.aetherbus import AetherBus
from prgx_ag.schemas.enums import EthicalStatus
from prgx_ag.services.translation_matrix import translate_internal_term


def test_translation_matrix_and_diplomat() -> None:
    diplomat = PRGX3Diplomat(agent_id="PRGX3", role="Diplomat", bus=AetherBus())
    assert translate_internal_term("Parajika") == "SYSTEM_HALT_IMMEDIATE"
    assert "stable" in diplomat.translate_to_world(EthicalStatus.CLEAN).lower()
