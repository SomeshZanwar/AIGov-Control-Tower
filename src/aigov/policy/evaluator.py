from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml
from sqlalchemy import text

from src.aigov.database import get_engine


DECISION_PRECEDENCE = {
    "APPROVED": 1,
    "APPROVED_WITH_CONTROLS": 2,
    "REQUIRES_REVIEW": 3,
    "BLOCKED": 4,
}


@dataclass(frozen=True)
class PolicyDecision:
    system_id: int
    system_key: str
    system_name: str
    policy_name: str
    policy_category: str
    decision: str
    severity: str
    reason: str
    control_required: str | None


def load_policies(policy_file_path: str | Path) -> list[dict[str, Any]]:
    path = Path(policy_file_path)

    if not path.exists():
        raise FileNotFoundError(f"Policy file not found: {path}")

    policy_data = yaml.safe_load(path.read_text(encoding="utf-8"))

    if not policy_data or "policies" not in policy_data:
        raise ValueError(f"Policy file has no 'policies' section: {path}")

    return policy_data["policies"]


def fetch_policy_context() -> list[dict[str, Any]]:
    query = text(
        """
        SELECT
            s.system_id,
            s.system_key,
            s.system_name,
            s.decision_impact,
            s.customer_facing,
            s.third_party_vendor,
            s.approval_status,
            s.prohibited_use_case,
            s.human_review_present,
            COALESCE(r.risk_tier, 'UNKNOWN') AS risk_tier,
            EXISTS (
                SELECT 1
                FROM inventory.ai_data_sources ds
                WHERE ds.system_id = s.system_id
                  AND ds.contains_sensitive_data = TRUE
                  AND ds.approved_for_ai_use = FALSE
            ) AS has_unapproved_sensitive_data_source
        FROM inventory.ai_systems s
        LEFT JOIN governance.risk_assessments r
            ON r.system_id = s.system_id
           AND r.assessment_status = 'ACTIVE'
        ORDER BY s.system_key
        """
    )

    engine = get_engine()

    with engine.begin() as connection:
        rows = connection.execute(query).mappings().all()

    return [dict(row) for row in rows]


def policy_matches(context: dict[str, Any], rules: dict[str, Any]) -> bool:
    for field_name, expected_value in rules.items():
        actual_value = context.get(field_name)

        if actual_value != expected_value:
            return False

    return True


def evaluate_policies(policy_file_path: str | Path) -> list[PolicyDecision]:
    policies = load_policies(policy_file_path)
    contexts = fetch_policy_context()
    decisions: list[PolicyDecision] = []

    for context in contexts:
        for policy in policies:
            rules = policy.get("rules", {})

            if policy_matches(context, rules):
                decisions.append(
                    PolicyDecision(
                        system_id=context["system_id"],
                        system_key=context["system_key"],
                        system_name=context["system_name"],
                        policy_name=policy["policy_name"],
                        policy_category=policy["policy_category"],
                        decision=policy["decision"],
                        severity=policy["severity"],
                        reason=policy["description"],
                        control_required=policy.get("control_required"),
                    )
                )

    return decisions


def save_policy_decisions(decisions: list[PolicyDecision]) -> None:
    delete_sql = text("DELETE FROM governance.policy_decisions")

    insert_sql = text(
        """
        INSERT INTO governance.policy_decisions (
            system_id,
            policy_name,
            policy_category,
            decision,
            severity,
            reason,
            control_required
        )
        VALUES (
            :system_id,
            :policy_name,
            :policy_category,
            :decision,
            :severity,
            :reason,
            :control_required
        )
        """
    )

    engine = get_engine()

    with engine.begin() as connection:
        connection.execute(delete_sql)
        for decision in decisions:
            connection.execute(
                insert_sql,
                {
                    "system_id": decision.system_id,
                    "policy_name": decision.policy_name,
                    "policy_category": decision.policy_category,
                    "decision": decision.decision,
                    "severity": decision.severity,
                    "reason": decision.reason,
                    "control_required": decision.control_required,
                },
            )


def strongest_decision_for_system(decisions: list[PolicyDecision]) -> dict[str, PolicyDecision]:
    strongest: dict[str, PolicyDecision] = {}

    for decision in decisions:
        current = strongest.get(decision.system_key)

        if current is None:
            strongest[decision.system_key] = decision
            continue

        if DECISION_PRECEDENCE[decision.decision] > DECISION_PRECEDENCE[current.decision]:
            strongest[decision.system_key] = decision

    return strongest


def run_policy_evaluation(policy_file_path: str | Path) -> list[PolicyDecision]:
    decisions = evaluate_policies(policy_file_path)
    save_policy_decisions(decisions)
    return decisions