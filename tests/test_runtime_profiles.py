from prgx_ag.config import RUNTIME_PROFILES, Settings


def test_runtime_profiles_have_distinct_controls() -> None:
    development = RUNTIME_PROFILES['development']
    staging = RUNTIME_PROFILES['staging']
    production = RUNTIME_PROFILES['production']

    assert development.max_auto_fix_items > staging.max_auto_fix_items > production.max_auto_fix_items
    assert development.max_issue_count_for_auto_fix > staging.max_issue_count_for_auto_fix > production.max_issue_count_for_auto_fix
    assert production.audit_verbosity == 'forensic'


def test_settings_exposes_profile() -> None:
    settings = Settings(PRGX_RUNTIME_PROFILE='staging')
    assert settings.profile.name == 'staging'
    assert settings.profile.evidence_signature_required is True
