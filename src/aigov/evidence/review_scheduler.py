from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any

from sqlalchemy import text

from src.aigov.database import get_engine


@dataclass(frozen=True)
class HumanReviewWorkflow:
    system_id: int
    system_key: str
    system_name: str
    review_type: str
    review_owner: str | None
    review_status: str
    required_reason: str
    due_date: datetime


@dataclass(frozen=True)
class ReassessmentSchedule:
    system_id: int
    system_key: str
    system_name: str
    risk_tier: str
    review_frequency_days: int
    last_reviewed_at: datetime | None
    next_review_due_at: datetime
    review_status: str


def fetch_review_context() -> list[dict[str, Any]]:
    query = text(
        """
        SELECT
            s.system_id,
            s.system_key,
            s.system_name,
            s.business_owner,
            s.technical_owner,
            s.governance_owner,
            s.decision_impact,
            s.customer_facing,
            s.external_user_facing,
            s.human_review_required,
            s.human_review_present,
            s.prohibited_use_case,
            s.approval_status,
            COALESCE(r.risk_tier, 'UNKNOWN') AS risk_tier
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


def review_owner(context: dict[str, Any]) -> str | None:
    return (
        context.get("governance_owner")
        or context.get("business_owner")
        or context.get("technical_owner")
    )


def human_review_due_date(context: dict[str, Any]) -> datetime:
    risk_tier = (context.get("risk_tier") or "").upper()

    if risk_tier == "BLOCKED":
        return datetime.now() + timedelta(days=7)
    if risk_tier == "HIGH":
        return datetime.now() + timedelta(days=14)
    if risk_tier == "MODERATE":
        return datetime.now() + timedelta(days=30)

    return datetime.now() + timedelta(days=60)


def review_status(context: dict[str, Any]) -> str:
    approval_status = (context.get("approval_status") or "").upper()

    if approval_status == "BLOCKED":
        return "BLOCKED_REVIEW_REQUIRED"

    if context["human_review_present"]:
        return "COMPLETED"

    if approval_status == "REQUIRES_REVIEW":
        return "PENDING"

    return "NOT_STARTED"


def review_reasons(context: dict[str, Any]) -> list[str]:
    reasons: list[str] = []

    if context["prohibited_use_case"]:
        reasons.append("Prohibited or blocked AI use case requires governance review")

    if context["decision_impact"] == "HIGH":
        reasons.append("High-impact AI system requires meaningful human oversight")

    if context["customer_facing"] or context["external_user_facing"]:
        reasons.append("Customer-facing or external-facing AI requires escalation controls")

    if context["human_review_required"] and not context["human_review_present"]:
        reasons.append("Required human review workflow is missing")

    if context["risk_tier"] in {"HIGH", "BLOCKED"}:
        reasons.append("Risk tier requires formal governance review")

    return reasons


def build_human_review_workflows(contexts: list[dict[str, Any]]) -> list[HumanReviewWorkflow]:
    workflows: list[HumanReviewWorkflow] = []

    for context in contexts:
        reasons = review_reasons(context)

        if not reasons:
            continue

        workflows.append(
            HumanReviewWorkflow(
                system_id=context["system_id"],
                system_key=context["system_key"],
                system_name=context["system_name"],
                review_type="AI_GOVERNANCE_REVIEW",
                review_owner=review_owner(context),
                review_status=review_status(context),
                required_reason="; ".join(reasons),
                due_date=human_review_due_date(context),
            )
        )

    return workflows


def reassessment_frequency_days(risk_tier: str) -> int:
    tier = (risk_tier or "").upper()

    if tier == "BLOCKED":
        return 7
    if tier == "HIGH":
        return 30
    if tier == "MODERATE":
        return 90
    if tier == "LOW":
        return 180

    return 90


def build_reassessment_schedules(contexts: list[dict[str, Any]]) -> list[ReassessmentSchedule]:
    schedules: list[ReassessmentSchedule] = []

    now = datetime.now()

    for context in contexts:
        risk_tier = context["risk_tier"]
        frequency_days = reassessment_frequency_days(risk_tier)
        next_review_due_at = now + timedelta(days=frequency_days)

        schedules.append(
            ReassessmentSchedule(
                system_id=context["system_id"],
                system_key=context["system_key"],
                system_name=context["system_name"],
                risk_tier=risk_tier,
                review_frequency_days=frequency_days,
                last_reviewed_at=None,
                next_review_due_at=next_review_due_at,
                review_status="SCHEDULED",
            )
        )

    return schedules


def save_human_review_workflows(workflows: list[HumanReviewWorkflow]) -> None:
    delete_sql = text("DELETE FROM governance.human_review_workflows")

    insert_sql = text(
        """
        INSERT INTO governance.human_review_workflows (
            system_id,
            review_type,
            review_owner,
            review_status,
            required_reason,
            due_date
        )
        VALUES (
            :system_id,
            :review_type,
            :review_owner,
            :review_status,
            :required_reason,
            :due_date
        )
        """
    )

    engine = get_engine()

    with engine.begin() as connection:
        connection.execute(delete_sql)
        for workflow in workflows:
            connection.execute(
                insert_sql,
                {
                    "system_id": workflow.system_id,
                    "review_type": workflow.review_type,
                    "review_owner": workflow.review_owner,
                    "review_status": workflow.review_status,
                    "required_reason": workflow.required_reason,
                    "due_date": workflow.due_date.date(),
                },
            )


def save_reassessment_schedules(schedules: list[ReassessmentSchedule]) -> None:
    delete_sql = text("DELETE FROM governance.reassessment_schedule")

    insert_sql = text(
        """
        INSERT INTO governance.reassessment_schedule (
            system_id,
            risk_tier,
            review_frequency_days,
            last_reviewed_at,
            next_review_due_at,
            review_status
        )
        VALUES (
            :system_id,
            :risk_tier,
            :review_frequency_days,
            :last_reviewed_at,
            :next_review_due_at,
            :review_status
        )
        """
    )

    engine = get_engine()

    with engine.begin() as connection:
        connection.execute(delete_sql)
        for schedule in schedules:
            connection.execute(
                insert_sql,
                {
                    "system_id": schedule.system_id,
                    "risk_tier": schedule.risk_tier,
                    "review_frequency_days": schedule.review_frequency_days,
                    "last_reviewed_at": schedule.last_reviewed_at,
                    "next_review_due_at": schedule.next_review_due_at,
                    "review_status": schedule.review_status,
                },
            )


def run_review_scheduling() -> tuple[list[HumanReviewWorkflow], list[ReassessmentSchedule]]:
    contexts = fetch_review_context()

    workflows = build_human_review_workflows(contexts)
    schedules = build_reassessment_schedules(contexts)

    save_human_review_workflows(workflows)
    save_reassessment_schedules(schedules)

    return workflows, schedules