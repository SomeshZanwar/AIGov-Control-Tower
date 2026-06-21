from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from sqlalchemy import text

from src.aigov.database import get_engine


@dataclass(frozen=True)
class AuditReport:
    system_key: str
    system_name: str
    report_text: str


def fetch_system_keys() -> list[str]:
    query = text(
        """
        SELECT system_key
        FROM inventory.ai_systems
        ORDER BY system_key
        """
    )

    engine = get_engine()

    with engine.begin() as connection:
        rows = connection.execute(query).scalars().all()

    return list(rows)


def fetch_system_report_context(system_key: str) -> dict[str, Any]:
    query = text(
        """
        SELECT
            s.system_id,
            s.system_key,
            s.system_name,
            s.system_description,
            s.department,
            s.business_owner,
            s.technical_owner,
            s.governance_owner,
            s.use_case,
            s.business_value,
            s.ai_type,
            s.model_provider,
            s.model_name,
            s.model_version,
            s.deployment_stage,
            s.customer_facing,
            s.external_user_facing,
            s.decision_impact,
            s.autonomy_level,
            s.uses_personal_data,
            s.uses_sensitive_data,
            s.third_party_vendor,
            s.vendor_name,
            s.prohibited_use_case,
            s.production_critical,
            s.approval_status,
            r.risk_score,
            r.risk_tier,
            r.risk_factors,
            h.review_status AS human_review_status,
            h.review_owner,
            h.due_date AS human_review_due_date,
            h.required_reason AS human_review_reason,
            rs.review_frequency_days,
            rs.next_review_due_at,
            rs.review_status AS reassessment_status
        FROM inventory.ai_systems s
        LEFT JOIN governance.risk_assessments r
            ON r.system_id = s.system_id
           AND r.assessment_status = 'ACTIVE'
        LEFT JOIN governance.human_review_workflows h
            ON h.system_id = s.system_id
        LEFT JOIN governance.reassessment_schedule rs
            ON rs.system_id = s.system_id
        WHERE s.system_key = :system_key
        """
    )

    engine = get_engine()

    with engine.begin() as connection:
        row = connection.execute(query, {"system_key": system_key}).mappings().first()

    if row is None:
        raise ValueError(f"No AI system found for system_key={system_key}")

    return dict(row)


def fetch_data_sources(system_id: int) -> list[dict[str, Any]]:
    query = text(
        """
        SELECT
            source_name,
            source_type,
            source_system,
            data_owner,
            business_domain,
            contains_pii,
            contains_sensitive_data,
            quality_status,
            approved_for_ai_use,
            access_control_status
        FROM inventory.ai_data_sources
        WHERE system_id = :system_id
        ORDER BY source_name
        """
    )

    engine = get_engine()

    with engine.begin() as connection:
        rows = connection.execute(query, {"system_id": system_id}).mappings().all()

    return [dict(row) for row in rows]


def fetch_policy_decisions(system_id: int) -> list[dict[str, Any]]:
    query = text(
        """
        SELECT
            policy_name,
            policy_category,
            decision,
            severity,
            reason,
            control_required
        FROM governance.policy_decisions
        WHERE system_id = :system_id
        ORDER BY
            CASE severity
                WHEN 'CRITICAL' THEN 1
                WHEN 'HIGH' THEN 2
                WHEN 'MEDIUM' THEN 3
                WHEN 'LOW' THEN 4
                ELSE 5
            END,
            policy_name
        """
    )

    engine = get_engine()

    with engine.begin() as connection:
        rows = connection.execute(query, {"system_id": system_id}).mappings().all()

    return [dict(row) for row in rows]


def fetch_document_summary(system_id: int) -> dict[str, Any]:
    query = text(
        """
        SELECT
            COUNT(*) AS required_documents,
            SUM(CASE WHEN completed THEN 1 ELSE 0 END) AS completed_documents,
            ROUND(
                SUM(CASE WHEN completed THEN 1 ELSE 0 END)::numeric / NULLIF(COUNT(*), 0),
                2
            ) AS completion_rate
        FROM governance.required_documents
        WHERE system_id = :system_id
        """
    )

    engine = get_engine()

    with engine.begin() as connection:
        row = connection.execute(query, {"system_id": system_id}).mappings().first()

    return dict(row) if row else {
        "required_documents": 0,
        "completed_documents": 0,
        "completion_rate": 0,
    }


def fetch_missing_documents(system_id: int) -> list[dict[str, Any]]:
    query = text(
        """
        SELECT
            document_name,
            document_category,
            owner,
            due_date
        FROM governance.required_documents
        WHERE system_id = :system_id
          AND completed = FALSE
        ORDER BY due_date, document_name
        """
    )

    engine = get_engine()

    with engine.begin() as connection:
        rows = connection.execute(query, {"system_id": system_id}).mappings().all()

    return [dict(row) for row in rows]


def fetch_mapped_incident_evidence(system_id: int) -> list[dict[str, Any]]:
    query = text(
        """
        SELECT
            i.external_incident_id,
            i.source_name,
            i.incident_title,
            i.affected_domain,
            i.harm_category,
            i.severity,
            m.mapped_risk_category,
            m.mapped_control,
            m.relevance_reason
        FROM evidence.ai_risk_evidence_mappings m
        JOIN evidence.ai_incidents i
            ON i.incident_id = m.incident_id
        WHERE m.system_id = :system_id
        ORDER BY i.severity, i.external_incident_id
        """
    )

    engine = get_engine()

    with engine.begin() as connection:
        rows = connection.execute(query, {"system_id": system_id}).mappings().all()

    return [dict(row) for row in rows]


def yes_no(value: Any) -> str:
    return "Yes" if value else "No"


def value_or_na(value: Any) -> str:
    return str(value) if value not in {None, ""} else "N/A"


def build_report_text(system_key: str) -> AuditReport:
    context = fetch_system_report_context(system_key)
    system_id = context["system_id"]

    data_sources = fetch_data_sources(system_id)
    policies = fetch_policy_decisions(system_id)
    document_summary = fetch_document_summary(system_id)
    missing_documents = fetch_missing_documents(system_id)
    incident_evidence = fetch_mapped_incident_evidence(system_id)

    lines: list[str] = []

    lines.append(f"# AI System Governance Audit Report: {context['system_name']}")
    lines.append("")
    lines.append("## System Overview")
    lines.append(f"- System Key: {context['system_key']}")
    lines.append(f"- Department: {context['department']}")
    lines.append(f"- Business Owner: {value_or_na(context['business_owner'])}")
    lines.append(f"- Technical Owner: {value_or_na(context['technical_owner'])}")
    lines.append(f"- Governance Owner: {value_or_na(context['governance_owner'])}")
    lines.append(f"- Use Case: {context['use_case']}")
    lines.append(f"- Business Value: {value_or_na(context['business_value'])}")
    lines.append(f"- AI Type: {context['ai_type']}")
    lines.append(f"- Model Provider: {context['model_provider']}")
    lines.append(f"- Model: {value_or_na(context['model_name'])}")
    lines.append(f"- Deployment Stage: {context['deployment_stage']}")
    lines.append(f"- Approval Status: {context['approval_status']}")
    lines.append("")

    lines.append("## Risk Assessment")
    lines.append(f"- Risk Score: {value_or_na(context['risk_score'])}")
    lines.append(f"- Risk Tier: {value_or_na(context['risk_tier'])}")
    lines.append(f"- Decision Impact: {context['decision_impact']}")
    lines.append(f"- Autonomy Level: {context['autonomy_level']}")
    lines.append(f"- Production Critical: {yes_no(context['production_critical'])}")
    lines.append(f"- Prohibited Use Case: {yes_no(context['prohibited_use_case'])}")
    lines.append(f"- Risk Factors: {value_or_na(context['risk_factors'])}")
    lines.append("")

    lines.append("## Data and Privacy Context")
    lines.append(f"- Uses Personal Data: {yes_no(context['uses_personal_data'])}")
    lines.append(f"- Uses Sensitive Data: {yes_no(context['uses_sensitive_data'])}")
    lines.append(f"- Third-Party Vendor: {yes_no(context['third_party_vendor'])}")
    lines.append(f"- Vendor Name: {value_or_na(context['vendor_name'])}")
    lines.append("")

    lines.append("### Data Sources")
    if data_sources:
        for source in data_sources:
            lines.append(
                f"- {source['source_name']} | {source['source_type']} | "
                f"Owner: {value_or_na(source['data_owner'])} | "
                f"Quality: {source['quality_status']} | "
                f"Approved for AI: {yes_no(source['approved_for_ai_use'])} | "
                f"Access: {source['access_control_status']}"
            )
    else:
        lines.append("- No data sources documented.")
    lines.append("")

    lines.append("## Policy Decisions")
    if policies:
        for policy in policies:
            lines.append(
                f"- {policy['decision']} | {policy['severity']} | "
                f"{policy['policy_name']} | Control: {value_or_na(policy['control_required'])}"
            )
    else:
        lines.append("- No policy violations or control decisions recorded.")
    lines.append("")

    lines.append("## Documentation Completeness")
    lines.append(f"- Required Documents: {document_summary['required_documents']}")
    lines.append(f"- Completed Documents: {document_summary['completed_documents']}")
    lines.append(f"- Completion Rate: {document_summary['completion_rate']}")
    lines.append("")

    if missing_documents:
        lines.append("### Missing Documents")
        for document in missing_documents:
            lines.append(
                f"- {document['document_name']} | "
                f"Category: {document['document_category']} | "
                f"Owner: {value_or_na(document['owner'])} | "
                f"Due: {value_or_na(document['due_date'])}"
            )
        lines.append("")

    lines.append("## Human Review and Reassessment")
    lines.append(f"- Human Review Status: {value_or_na(context['human_review_status'])}")
    lines.append(f"- Human Review Owner: {value_or_na(context['review_owner'])}")
    lines.append(f"- Human Review Due Date: {value_or_na(context['human_review_due_date'])}")
    lines.append(f"- Human Review Reason: {value_or_na(context['human_review_reason'])}")
    lines.append(f"- Reassessment Frequency Days: {value_or_na(context['review_frequency_days'])}")
    lines.append(f"- Next Reassessment Due: {value_or_na(context['next_review_due_at'])}")
    lines.append(f"- Reassessment Status: {value_or_na(context['reassessment_status'])}")
    lines.append("")

    lines.append("## Mapped Real-World Risk Evidence")
    if incident_evidence:
        for evidence in incident_evidence:
            lines.append(
                f"- {evidence['external_incident_id']} | "
                f"{evidence['source_name']} | "
                f"{evidence['mapped_risk_category']} | "
                f"Control: {value_or_na(evidence['mapped_control'])}"
            )
            lines.append(f"  - Reason: {evidence['relevance_reason']}")
    else:
        lines.append("- No external risk evidence mapped.")
    lines.append("")

    lines.append("## Audit Conclusion")
    if context["prohibited_use_case"]:
        lines.append(
            "This AI system should remain blocked until a formal governance review determines whether the use case can be redesigned or retired."
        )
    elif context["risk_tier"] in {"HIGH", "BLOCKED"}:
        lines.append(
            "This AI system requires formal governance review, documented controls, and close reassessment before production approval."
        )
    elif policies:
        lines.append(
            "This AI system has governance controls or review requirements that must be addressed before full approval."
        )
    else:
        lines.append(
            "This AI system currently has no blocking governance findings based on available evidence."
        )

    report_text = "\n".join(lines)

    return AuditReport(
        system_key=context["system_key"],
        system_name=context["system_name"],
        report_text=report_text,
    )


def write_report(report: AuditReport, output_dir: str | Path) -> Path:
    path = Path(output_dir)
    path.mkdir(parents=True, exist_ok=True)

    output_path = path / f"{report.system_key}_audit_report.md"
    output_path.write_text(report.report_text, encoding="utf-8")

    return output_path


def generate_all_audit_reports(output_dir: str | Path) -> list[Path]:
    output_paths: list[Path] = []

    for system_key in fetch_system_keys():
        report = build_report_text(system_key)
        output_paths.append(write_report(report, output_dir))

    return output_paths