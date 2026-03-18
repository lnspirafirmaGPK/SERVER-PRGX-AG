from __future__ import annotations

from typing import Final, Literal

from pydantic import BaseModel, ConfigDict, Field

PRINCIPLES: Final[list[str]] = [
    "Non-Harm",
    "Efficiency",
    "Truthfulness",
    "Transparency",
    "No Infinite Loops",
    "Protected Boundaries",
]

RuleScope = Literal["intent_text", "metadata_operational", "metadata_context"]
RuleSeverity = Literal["review", "reject"]


class PolicyRule(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    rule_id: str
    pattern: str
    scope: RuleScope
    severity: RuleSeverity
    reason: str
    allow_context_hints: tuple[str, ...] = Field(default_factory=tuple)
    recommended_action: str
    match_mode: Literal["substring"] = "substring"


SAFE_AETHEBUD_TERMS: Final[dict[str, str]] = {
    "parajika": "Severity marker for critical ethical violation; not malicious by itself.",
    "nirodha": "Graceful shutdown intent; not malicious by itself.",
    "sati": "Deep monitoring / observability intent; not malicious by itself.",
    "metta": "Helpful UX optimization intent; not malicious by itself.",
    "sanghadisesa": "Suspend-and-audit intent; not malicious by itself.",
}

SAFE_EXPORTED_COMMANDS: Final[dict[str, str]] = {
    "system_halt_immediate": "Legitimate exported safety halt; review by context.",
    "graceful_shutdown": "Legitimate controlled shutdown command.",
    "enable_deep_monitoring": "Legitimate observability command.",
    "optimize_ux_response": "Legitimate helpfulness command.",
    "suspend_and_audit": "Legitimate governance escalation command.",
}

SAFE_CONTEXT_HINTS: Final[tuple[str, ...]] = (
    "prevent ",
    "preventing ",
    "detect ",
    "detecting ",
    "block ",
    "blocking ",
    "guard ",
    "guarding ",
    "mitigate ",
    "mitigating ",
    "scan ",
    "scanning ",
    "audit ",
    "auditing ",
    "review ",
    "reviewing ",
    "reject ",
    "rejecting ",
    "prohibit ",
    "prohibiting ",
    "narrative",
    "defensive",
    "example",
    "documentation",
)

POLICY_RULES: Final[tuple[PolicyRule, ...]] = (
    PolicyRule(
        rule_id="core-delete-core",
        pattern="delete_core",
        scope="metadata_operational",
        severity="reject",
        reason="Attempt to delete core systems is prohibited.",
        recommended_action="Escalate to audit and reject execution.",
    ),
    PolicyRule(
        rule_id="core-shutdown-nexus",
        pattern="shutdown_nexus",
        scope="metadata_operational",
        severity="reject",
        reason="Unauthorized shutdown of the nexus is prohibited.",
        recommended_action="Escalate to audit and reject execution.",
    ),
    PolicyRule(
        rule_id="core-destroy-core",
        pattern="destroy core",
        scope="intent_text",
        severity="reject",
        reason="Core destruction intent is prohibited.",
        recommended_action="Escalate to audit and reject execution.",
    ),
    PolicyRule(
        rule_id="core-wipe-repository",
        pattern="wipe repository",
        scope="intent_text",
        severity="reject",
        reason="Repository wipe intent is prohibited.",
        recommended_action="Escalate to audit and reject execution.",
    ),
    PolicyRule(
        rule_id="core-delete-all-files",
        pattern="delete all files",
        scope="intent_text",
        severity="reject",
        reason="Bulk file destruction is prohibited.",
        recommended_action="Escalate to audit and reject execution.",
    ),
    PolicyRule(
        rule_id="core-mass-delete",
        pattern="mass delete",
        scope="intent_text",
        severity="reject",
        reason="Mass deletion intent is prohibited.",
        recommended_action="Escalate to audit and reject execution.",
    ),
    PolicyRule(
        rule_id="core-mass-deletion",
        pattern="mass deletion",
        scope="intent_text",
        severity="review",
        reason="Mass deletion language requires contextual review.",
        allow_context_hints=SAFE_CONTEXT_HINTS,
        recommended_action="Require governance review before execution.",
    ),
    PolicyRule(
        rule_id="data-rm-root",
        pattern="rm -rf /",
        scope="metadata_operational",
        severity="reject",
        reason="Recursive destructive deletion is prohibited.",
        recommended_action="Escalate to audit and reject execution.",
    ),
    PolicyRule(
        rule_id="data-rm-repo",
        pattern="rm -rf .",
        scope="metadata_operational",
        severity="reject",
        reason="Repository-root destructive deletion is prohibited.",
        recommended_action="Escalate to audit and reject execution.",
    ),
    PolicyRule(
        rule_id="data-drop-table",
        pattern="drop table ",
        scope="metadata_operational",
        severity="reject",
        reason="Destructive database schema deletion is prohibited.",
        recommended_action="Escalate to audit and reject execution.",
    ),
    PolicyRule(
        rule_id="data-truncate-table",
        pattern="truncate table ",
        scope="metadata_operational",
        severity="reject",
        reason="Destructive bulk data removal is prohibited.",
        recommended_action="Escalate to audit and reject execution.",
    ),
    PolicyRule(
        rule_id="data-delete-database",
        pattern="delete database",
        scope="intent_text",
        severity="reject",
        reason="Database destruction intent is prohibited.",
        recommended_action="Escalate to audit and reject execution.",
    ),
    PolicyRule(
        rule_id="data-wipe-database",
        pattern="wipe database",
        scope="intent_text",
        severity="reject",
        reason="Database wipe intent is prohibited.",
        recommended_action="Escalate to audit and reject execution.",
    ),
    PolicyRule(
        rule_id="resource-infinite-loop",
        pattern="introduce infinite loop",
        scope="intent_text",
        severity="reject",
        reason="Introducing infinite loops is prohibited.",
        recommended_action="Escalate to audit and reject execution.",
    ),
    PolicyRule(
        rule_id="resource-create-infinite-loop",
        pattern="create infinite loop",
        scope="intent_text",
        severity="reject",
        reason="Creating infinite loops is prohibited.",
        recommended_action="Escalate to audit and reject execution.",
    ),
    PolicyRule(
        rule_id="resource-destructive-recursion",
        pattern="destructive recursion",
        scope="intent_text",
        severity="review",
        reason="Destructive recursion language requires contextual review.",
        allow_context_hints=SAFE_CONTEXT_HINTS,
        recommended_action="Require governance review before execution.",
    ),
    PolicyRule(
        rule_id="resource-fork-bomb",
        pattern="fork bomb",
        scope="intent_text",
        severity="review",
        reason="Fork bomb language requires contextual review.",
        allow_context_hints=SAFE_CONTEXT_HINTS,
        recommended_action="Require governance review before execution.",
    ),
    PolicyRule(
        rule_id="resource-self-replicate",
        pattern="self replicate without limit",
        scope="intent_text",
        severity="reject",
        reason="Unbounded self-replication is prohibited.",
        recommended_action="Escalate to audit and reject execution.",
    ),
    PolicyRule(
        rule_id="resource-while-true",
        pattern="while true without break",
        scope="metadata_operational",
        severity="reject",
        reason="Unbounded looping behavior is prohibited.",
        recommended_action="Escalate to audit and reject execution.",
    ),
    PolicyRule(
        rule_id="security-exploit",
        pattern="exploit_vulnerability",
        scope="metadata_operational",
        severity="reject",
        reason="Exploit execution is prohibited.",
        recommended_action="Escalate to audit and reject execution.",
    ),
    PolicyRule(
        rule_id="security-execute-exploit",
        pattern="execute exploit",
        scope="intent_text",
        severity="reject",
        reason="Exploit execution is prohibited.",
        recommended_action="Escalate to audit and reject execution.",
    ),
    PolicyRule(
        rule_id="security-run-exploit",
        pattern="run exploit",
        scope="intent_text",
        severity="review",
        reason="Exploit language requires contextual review.",
        allow_context_hints=SAFE_CONTEXT_HINTS,
        recommended_action="Require governance review before execution.",
    ),
    PolicyRule(
        rule_id="security-privilege-escalation",
        pattern="privilege escalation",
        scope="intent_text",
        severity="review",
        reason="Privilege escalation language requires contextual review.",
        allow_context_hints=SAFE_CONTEXT_HINTS,
        recommended_action="Require governance review before execution.",
    ),
    PolicyRule(
        rule_id="security-disable-audit",
        pattern="disable audit",
        scope="intent_text",
        severity="review",
        reason="Audit bypass language requires contextual review.",
        allow_context_hints=SAFE_CONTEXT_HINTS,
        recommended_action="Require governance review before execution.",
    ),
    PolicyRule(
        rule_id="security-skip-audit",
        pattern="skip audit",
        scope="intent_text",
        severity="review",
        reason="Audit bypass language requires contextual review.",
        allow_context_hints=SAFE_CONTEXT_HINTS,
        recommended_action="Require governance review before execution.",
    ),
    PolicyRule(
        rule_id="security-bypass-audit",
        pattern="bypass audit",
        scope="intent_text",
        severity="review",
        reason="Audit bypass language requires contextual review.",
        allow_context_hints=SAFE_CONTEXT_HINTS,
        recommended_action="Require governance review before execution.",
    ),
    PolicyRule(
        rule_id="security-disable-patimokkha",
        pattern="disable patimokkha",
        scope="intent_text",
        severity="reject",
        reason="Disabling Patimokkha enforcement is prohibited.",
        recommended_action="Escalate to audit and reject execution.",
    ),
    PolicyRule(
        rule_id="security-override-patimokkha",
        pattern="override patimokkha",
        scope="intent_text",
        severity="reject",
        reason="Overriding Patimokkha enforcement is prohibited.",
        recommended_action="Escalate to audit and reject execution.",
    ),
    PolicyRule(
        rule_id="secret-exfiltrate-secrets",
        pattern="exfiltrate secrets",
        scope="intent_text",
        severity="reject",
        reason="Secret exfiltration is prohibited.",
        recommended_action="Escalate to audit and reject execution.",
    ),
    PolicyRule(
        rule_id="secret-exfiltrate-credentials",
        pattern="exfiltrate credentials",
        scope="intent_text",
        severity="reject",
        reason="Credential exfiltration is prohibited.",
        recommended_action="Escalate to audit and reject execution.",
    ),
    PolicyRule(
        rule_id="secret-leak-secrets",
        pattern="leak secrets",
        scope="intent_text",
        severity="review",
        reason="Secret leakage language requires contextual review.",
        allow_context_hints=SAFE_CONTEXT_HINTS,
        recommended_action="Require governance review before execution.",
    ),
    PolicyRule(
        rule_id="secret-dump-environment",
        pattern="dump environment secrets",
        scope="metadata_operational",
        severity="reject",
        reason="Environment secret dumping is prohibited.",
        recommended_action="Escalate to audit and reject execution.",
    ),
    PolicyRule(
        rule_id="secret-overwrite-protected-path",
        pattern="overwrite protected path",
        scope="metadata_operational",
        severity="reject",
        reason="Writing to protected paths is prohibited.",
        recommended_action="Escalate to audit and reject execution.",
    ),
    PolicyRule(
        rule_id="secret-modify-protected-path",
        pattern="modify protected path",
        scope="metadata_operational",
        severity="reject",
        reason="Writing to protected paths is prohibited.",
        recommended_action="Escalate to audit and reject execution.",
    ),
)
