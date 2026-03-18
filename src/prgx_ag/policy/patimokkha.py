from __future__ import annotations

from typing import Any, Iterable

from prgx_ag.policy.ruleset import (
    POLICY_RULES,
    PRINCIPLES,
    PolicyRule,
    SAFE_AETHEBUD_TERMS,
    SAFE_EXPORTED_COMMANDS,
)
from prgx_ag.schemas import AuditResult, EthicalStatus, Intent


class PatimokkhaChecker:
    """Context-aware intent auditor for governed execution."""

    def _flatten(self, value: Any) -> Iterable[str]:
        if value is None:
            return []

        if isinstance(value, dict):
            parts: list[str] = []
            for key, item in value.items():
                parts.append(str(key))
                parts.extend(self._flatten(item))
            return parts

        if isinstance(value, (list, tuple, set)):
            items: list[str] = []
            for item in value:
                items.extend(self._flatten(item))
            return items

        return [str(value)]

    def _normalize_text(self, value: Any) -> str:
        return " ".join(str(value).split()).strip().lower()

    def _metadata(self, intent: Intent) -> dict[str, Any]:
        return intent.metadata if isinstance(intent.metadata, dict) else {}

    def _intent_fields(self, intent: Intent) -> dict[str, str]:
        return {
            "id": self._normalize_text(getattr(intent, "id", "")),
            "source_agent": self._normalize_text(getattr(intent, "source_agent", "")),
            "target_firma": self._normalize_text(getattr(intent, "target_firma", "")),
            "description": self._normalize_text(getattr(intent, "description", "")),
        }

    def _metadata_fields(self, metadata: dict[str, Any]) -> dict[str, str]:
        fields: dict[str, str] = {}
        for key, value in metadata.items():
            fields[f"metadata.{key}"] = self._normalize_text(" ".join(self._flatten(value)))
        return fields

    def _safe_command_context(self, metadata: dict[str, Any]) -> bool:
        internal_term = self._normalize_text(metadata.get("internal_term", ""))
        exported_command = self._normalize_text(metadata.get("exported_command", ""))

        return (
            internal_term in SAFE_AETHEBUD_TERMS
            or exported_command in SAFE_EXPORTED_COMMANDS
        )

    def _find_context_hint(self, text: str, token: str, hints: tuple[str, ...], window: int = 96) -> str | None:
        start = 0
        while True:
            index = text.find(token, start)
            if index == -1:
                return None

            left = max(0, index - window)
            right = min(len(text), index + len(token) + window)
            local_text = text[left:right]

            for hint in hints:
                if hint in local_text:
                    return hint.strip()

            start = index + len(token)

    def _rule_applies_to_field(self, rule: PolicyRule, field_name: str) -> bool:
        if rule.scope == "intent_text":
            return field_name in {"id", "source_agent", "target_firma", "description"}
        if rule.scope == "metadata_operational":
            return field_name.startswith("metadata.") and any(
                token in field_name
                for token in (
                    "command",
                    "operation",
                    "script",
                    "shell",
                    "query",
                    "sql",
                    "action",
                    "plan",
                    "step",
                    "payload",
                )
            )
        if rule.scope == "metadata_context":
            return field_name.startswith("metadata.")
        return False

    def _collect_matches(self, fields: dict[str, str]) -> list[dict[str, Any]]:
        matches: list[dict[str, Any]] = []
        for field_name, field_text in fields.items():
            if not field_text:
                continue

            for rule in POLICY_RULES:
                if not self._rule_applies_to_field(rule, field_name):
                    continue
                if rule.pattern not in field_text:
                    continue

                context_hint = self._find_context_hint(field_text, rule.pattern, rule.allow_context_hints)
                matches.append(
                    {
                        "field": field_name,
                        "pattern": rule.pattern,
                        "rule_id": rule.rule_id,
                        "scope": rule.scope,
                        "severity": rule.severity,
                        "reason": rule.reason,
                        "recommended_action": rule.recommended_action,
                        "context_hint": context_hint,
                        "review_mode": bool(context_hint and rule.allow_context_hints),
                    }
                )
        return matches

    def _derive_operational_status(self, metadata: dict[str, Any]) -> EthicalStatus:
        raw_status = self._normalize_text(metadata.get("ethical_status", ""))

        if raw_status == self._normalize_text(EthicalStatus.PARAJIKA.value):
            return EthicalStatus.PARAJIKA

        if raw_status == self._normalize_text(EthicalStatus.MAJOR_VIOLATION.value):
            return EthicalStatus.MAJOR_VIOLATION

        if raw_status == self._normalize_text(EthicalStatus.MINOR_INFRACTION.value):
            return EthicalStatus.MINOR_INFRACTION

        return EthicalStatus.CLEAN

    def validate_intent(self, intent: Intent) -> AuditResult:
        metadata = self._metadata(intent)
        intent_fields = self._intent_fields(intent)
        metadata_fields = self._metadata_fields(metadata)
        matches = self._collect_matches({**intent_fields, **metadata_fields})

        direct_rejects = [match for match in matches if match["severity"] == "reject" and not match["review_mode"]]
        contextual_reviews = [
            match for match in matches if match["review_mode"] or match["severity"] == "review"
        ]

        if direct_rejects:
            primary = direct_rejects[0]
            return AuditResult(
                is_allowed=False,
                status=EthicalStatus.PARAJIKA,
                reason=f"{primary['reason']} Matched pattern: {primary['pattern']}",
                suggested_action=primary["recommended_action"],
                outcome="reject",
                metadata={
                    "outcome": "reject",
                    "evaluation_mode": "direct_block",
                    "matched_fields": sorted({match["field"] for match in direct_rejects}),
                    "rule_fired": primary["rule_id"],
                    "evidence": direct_rejects,
                },
            )

        if contextual_reviews:
            primary = contextual_reviews[0]
            return AuditResult(
                is_allowed=True,
                status=EthicalStatus.MINOR_INFRACTION,
                reason=(
                    f"{primary['reason']} Matched pattern: {primary['pattern']} in {primary['field']}"
                ),
                suggested_action="Require human or governance review before execution.",
                outcome="review_required",
                metadata={
                    "outcome": "review_required",
                    "evaluation_mode": "contextual_review",
                    "matched_fields": sorted({match["field"] for match in contextual_reviews}),
                    "rule_fired": primary["rule_id"],
                    "evidence": contextual_reviews,
                },
            )

        operational_status = self._derive_operational_status(metadata)
        if operational_status in {
            EthicalStatus.MAJOR_VIOLATION,
            EthicalStatus.PARAJIKA,
        } and self._safe_command_context(metadata):
            return AuditResult(
                is_allowed=True,
                status=operational_status,
                reason=(
                    "High-severity operational state acknowledged, but intent remains "
                    "bounded by recognized safety commands and governance context."
                ),
                suggested_action="Proceed with strict monitoring and retain full audit evidence.",
                outcome="allow",
                metadata={
                    "outcome": "allow",
                    "evaluation_mode": "safe_operational_override",
                    "matched_fields": [],
                    "rule_fired": None,
                    "evidence": [],
                },
            )

        principles = ", ".join(PRINCIPLES)
        return AuditResult(
            is_allowed=True,
            status=EthicalStatus.CLEAN,
            reason=f"Intent complies with Patimokkha principles: {principles}.",
            suggested_action="Proceed with monitored execution.",
            outcome="allow",
            metadata={
                "outcome": "allow",
                "evaluation_mode": "no_rule_triggered",
                "matched_fields": [],
                "rule_fired": None,
                "evidence": [],
            },
        )
