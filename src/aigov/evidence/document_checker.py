from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
from typing import Any

from sqlalchemy import text

from src.aigov.database import get_engine


@dataclass(frozen=True)
class RequiredDocument:
    system_id: int
    system_key: str
    system_name: str
    document_name: str
    document_category: str
    required: bool
    completed: bool
    owner: str | None
    due_date: date | None


BASE_DOCUMENTS = [
    ("Business Case", "use_case_governance"),
    ("AI Risk Assessment", "risk_management"),
    ("Data Source Inventory", "data_governance"),
    ("Monitoring Plan", "monitoring"),
    ("Incident Response Plan", "incident_response"),
]

SENSITIVE_DATA_DOCUMENTS = [
    ("Privacy Review", "privacy"),
    ("Data Protection Impact Assessment", "privacy"),
]

VENDOR_DOCUMENTS = [
    ("Vendor Risk Review", "third_party_risk"),
    ("Vendor Usage Attestation", "third_party_risk"),
]

CUSTOMER_FACING_DOCUMENTS = [
    ("Customer Disclosure Review", "transparency"),
    ("Output Quality Control Plan", "quality_control"),
]

HUMAN_REVIEW_DOCUMENTS = [
    ("Human Review Workflow", "human_oversight"),
    ("Escalation Procedure", "human_oversight"),
]

HIGH_RISK_DOCUMENTS = [
    ("Model Card", "model_documentation"),
    ("Bias and Fairness Assessment", "fairness"),
    ("Governance Committee Approval", "approval"),
]


def fetch_document_context() -> list[dict[str, Any]]:
    query = text(
        """
        SELECT
            s.system_id,
            s.system_key,
            s.system_name,
            s.governance_owner,
            s.business_owner,
            s.technical_owner,
            s.customer_facing,
            s.third_party_vendor,
            s.uses_sensitive_data,
            s.uses_personal_data,
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


def document_is_completed(context: dict[str, Any], document_name: str) -> bool:
    approval_status = (context.get("approval_status") or "").upper()

    if approval_status == "BLOCKED":
        return False

    if approval_status == "NOT_REVIEWED":
        return False

    if approval_status == "REQUIRES_REVIEW":
        return document_name in {
            "Business Case",
            "Data Source Inventory",
        }

    if approval_status == "APPROVED_WITH_CONTROLS":
        incomplete_control_docs = {
            "Bias and Fairness Assessment",
            "Governance Committee Approval",
        }
        return document_name not in incomplete_control_docs

    return False


def owner_for_document(context: dict[str, Any], category: str) -> str | None:
    if category in {"privacy", "data_governance"}:
        return context.get("governance_owner") or context.get("business_owner")

    if category in {"model_documentation", "monitoring", "quality_control"}:
        return context.get("technical_owner") or context.get("governance_owner")

    if category in {"approval", "risk_management", "human_oversight"}:
        return context.get("governance_owner")

    if category == "third_party_risk":
        return context.get("governance_owner") or context.get("business_owner")

    return context.get("business_owner") or context.get("governance_owner")


def due_date_for_document(context: dict[str, Any]) -> date:
    risk_tier = (context.get("risk_tier") or "").upper()

    if risk_tier == "BLOCKED":
        return date.today() + timedelta(days=7)
    if risk_tier == "HIGH":
        return date.today() + timedelta(days=14)
    if risk_tier == "MODERATE":
        return date.today() + timedelta(days=30)
    return date.today() + timedelta(days=60)


def documents_for_system(context: dict[str, Any]) -> list[RequiredDocument]:
    document_specs = list(BASE_DOCUMENTS)

    if context["uses_sensitive_data"] or context["uses_personal_data"]:
        document_specs.extend(SENSITIVE_DATA_DOCUMENTS)

    if context["third_party_vendor"]:
        document_specs.extend(VENDOR_DOCUMENTS)

    if context["customer_facing"]:
        document_specs.extend(CUSTOMER_FACING_DOCUMENTS)

    if context["human_review_required"] or not context["human_review_present"]:
        document_specs.extend(HUMAN_REVIEW_DOCUMENTS)

    if context["risk_tier"] in {"HIGH", "BLOCKED"} or context["prohibited_use_case"]:
        document_specs.extend(HIGH_RISK_DOCUMENTS)

    documents: list[RequiredDocument] = []

    for document_name, category in document_specs:
        documents.append(
            RequiredDocument(
                system_id=context["system_id"],
                system_key=context["system_key"],
                system_name=context["system_name"],
                document_name=document_name,
                document_category=category,
                required=True,
                completed=document_is_completed(context, document_name),
                owner=owner_for_document(context, category),
                due_date=due_date_for_document(context),
            )
        )

    return documents


def save_required_documents(documents: list[RequiredDocument]) -> None:
    delete_sql = text("DELETE FROM governance.required_documents")

    insert_sql = text(
        """
        INSERT INTO governance.required_documents (
            system_id,
            document_name,
            document_category,
            required,
            completed,
            owner,
            due_date,
            completed_at
        )
        VALUES (
            :system_id,
            :document_name,
            :document_category,
            :required,
            :completed,
            :owner,
            :due_date,
            CASE WHEN :completed = TRUE THEN CURRENT_TIMESTAMP ELSE NULL END
        )
        """
    )

    engine = get_engine()

    with engine.begin() as connection:
        connection.execute(delete_sql)
        for document in documents:
            connection.execute(
                insert_sql,
                {
                    "system_id": document.system_id,
                    "document_name": document.document_name,
                    "document_category": document.document_category,
                    "required": document.required,
                    "completed": document.completed,
                    "owner": document.owner,
                    "due_date": document.due_date,
                },
            )


def run_document_completeness_check() -> list[RequiredDocument]:
    contexts = fetch_document_context()

    documents: list[RequiredDocument] = []
    for context in contexts:
        documents.extend(documents_for_system(context))

    save_required_documents(documents)
    return documents


def calculate_document_summary(documents: list[RequiredDocument]) -> dict[str, dict[str, int | float]]:
    summary: dict[str, dict[str, int | float]] = {}

    for document in documents:
        if document.system_key not in summary:
            summary[document.system_key] = {
                "required": 0,
                "completed": 0,
                "completion_rate": 0.0,
            }

        summary[document.system_key]["required"] += 1

        if document.completed:
            summary[document.system_key]["completed"] += 1

    for system_key, values in summary.items():
        required = int(values["required"])
        completed = int(values["completed"])
        values["completion_rate"] = round(completed / required, 2) if required else 0.0

    return summary