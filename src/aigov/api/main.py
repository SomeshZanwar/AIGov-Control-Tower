from __future__ import annotations

from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.encoders import jsonable_encoder
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from src.aigov.database import get_engine


app = FastAPI(
    title="AIGov Control Tower API",
    description="Read-only API for AI governance inventory, risk, policy, evidence, and audit reporting.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def fetch_all(query: str, params: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    engine = get_engine()

    with engine.begin() as connection:
        rows = connection.execute(text(query), params or {}).mappings().all()

    return jsonable_encoder([dict(row) for row in rows])


def fetch_one(query: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
    engine = get_engine()

    with engine.begin() as connection:
        row = connection.execute(text(query), params or {}).mappings().first()

    if row is None:
        raise HTTPException(status_code=404, detail="Resource not found")

    return jsonable_encoder(dict(row))


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok", "service": "aigov-control-tower-api"}


@app.get("/api/summary")
def get_summary() -> dict[str, Any]:
    query = """
        WITH doc_summary AS (
            SELECT
                system_id,
                COUNT(*) AS required_documents,
                SUM(CASE WHEN completed THEN 1 ELSE 0 END) AS completed_documents
            FROM governance.required_documents
            GROUP BY system_id
        ),
        policy_summary AS (
            SELECT
                system_id,
                COUNT(*) AS policy_findings,
                SUM(CASE WHEN decision = 'BLOCKED' THEN 1 ELSE 0 END) AS blocked_findings,
                SUM(CASE WHEN decision = 'REQUIRES_REVIEW' THEN 1 ELSE 0 END) AS review_findings
            FROM governance.policy_decisions
            GROUP BY system_id
        )
        SELECT
            COUNT(*) AS total_systems,
            SUM(CASE WHEN r.risk_tier = 'BLOCKED' THEN 1 ELSE 0 END) AS blocked_systems,
            SUM(CASE WHEN r.risk_tier = 'MODERATE' THEN 1 ELSE 0 END) AS moderate_risk_systems,
            SUM(CASE WHEN r.risk_tier = 'LOW' THEN 1 ELSE 0 END) AS low_risk_systems,
            COALESCE(SUM(p.policy_findings), 0) AS total_policy_findings,
            COALESCE(SUM(p.blocked_findings), 0) AS blocked_policy_findings,
            COALESCE(SUM(p.review_findings), 0) AS review_policy_findings,
            COALESCE(SUM(d.required_documents), 0) AS required_documents,
            COALESCE(SUM(d.completed_documents), 0) AS completed_documents
        FROM inventory.ai_systems s
        LEFT JOIN governance.risk_assessments r
            ON r.system_id = s.system_id
           AND r.assessment_status = 'ACTIVE'
        LEFT JOIN policy_summary p
            ON p.system_id = s.system_id
        LEFT JOIN doc_summary d
            ON d.system_id = s.system_id
    """

    return fetch_one(query)


@app.get("/api/systems")
def get_systems() -> list[dict[str, Any]]:
    query = """
        WITH doc_summary AS (
            SELECT
                system_id,
                COUNT(*) AS required_documents,
                SUM(CASE WHEN completed THEN 1 ELSE 0 END) AS completed_documents,
                ROUND(
                    SUM(CASE WHEN completed THEN 1 ELSE 0 END)::numeric / NULLIF(COUNT(*), 0),
                    2
                ) AS completion_rate
            FROM governance.required_documents
            GROUP BY system_id
        ),
        policy_summary AS (
            SELECT
                system_id,
                COUNT(*) AS policy_findings,
                SUM(CASE WHEN decision = 'BLOCKED' THEN 1 ELSE 0 END) AS blocked_findings,
                SUM(CASE WHEN decision = 'REQUIRES_REVIEW' THEN 1 ELSE 0 END) AS review_findings
            FROM governance.policy_decisions
            GROUP BY system_id
        )
        SELECT
            s.system_key,
            s.system_name,
            s.department,
            s.business_owner,
            s.technical_owner,
            s.governance_owner,
            s.use_case,
            s.ai_type,
            s.deployment_stage,
            s.decision_impact,
            s.autonomy_level,
            s.customer_facing,
            s.external_user_facing,
            s.third_party_vendor,
            s.prohibited_use_case,
            s.production_critical,
            s.approval_status,
            COALESCE(r.risk_score, 0) AS risk_score,
            COALESCE(r.risk_tier, 'UNKNOWN') AS risk_tier,
            COALESCE(r.risk_factors, 'Not assessed') AS risk_factors,
            COALESCE(d.required_documents, 0) AS required_documents,
            COALESCE(d.completed_documents, 0) AS completed_documents,
            COALESCE(d.completion_rate, 0) AS completion_rate,
            COALESCE(p.policy_findings, 0) AS policy_findings,
            COALESCE(p.blocked_findings, 0) AS blocked_findings,
            COALESCE(p.review_findings, 0) AS review_findings,
            COALESCE(h.review_status, 'NOT_REQUIRED') AS human_review_status,
            h.review_owner,
            h.due_date AS human_review_due_date,
            rs.review_frequency_days,
            rs.next_review_due_at::date AS next_review_due_date,
            COALESCE(rs.review_status, 'NOT_SCHEDULED') AS reassessment_status
        FROM inventory.ai_systems s
        LEFT JOIN governance.risk_assessments r
            ON r.system_id = s.system_id
           AND r.assessment_status = 'ACTIVE'
        LEFT JOIN doc_summary d
            ON d.system_id = s.system_id
        LEFT JOIN policy_summary p
            ON p.system_id = s.system_id
        LEFT JOIN governance.human_review_workflows h
            ON h.system_id = s.system_id
        LEFT JOIN governance.reassessment_schedule rs
            ON rs.system_id = s.system_id
        ORDER BY s.system_key
    """

    return fetch_all(query)


@app.get("/api/systems/{system_key}")
def get_system(system_key: str) -> dict[str, Any]:
    query = """
        SELECT
            s.*,
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

    return fetch_one(query, {"system_key": system_key})


@app.get("/api/systems/{system_key}/data-sources")
def get_system_data_sources(system_key: str) -> list[dict[str, Any]]:
    query = """
        SELECT
            ds.source_name,
            ds.source_type,
            ds.source_system,
            ds.data_owner,
            ds.business_domain,
            ds.contains_pii,
            ds.contains_sensitive_data,
            ds.contains_financial_data,
            ds.contains_health_data,
            ds.quality_status,
            ds.lineage_available,
            ds.approved_for_ai_use,
            ds.retention_policy,
            ds.access_control_status
        FROM inventory.ai_data_sources ds
        JOIN inventory.ai_systems s
            ON s.system_id = ds.system_id
        WHERE s.system_key = :system_key
        ORDER BY ds.source_name
    """

    return fetch_all(query, {"system_key": system_key})


@app.get("/api/systems/{system_key}/policy-decisions")
def get_system_policy_decisions(system_key: str) -> list[dict[str, Any]]:
    query = """
        SELECT
            p.policy_name,
            p.policy_category,
            p.decision,
            p.severity,
            p.reason,
            p.control_required
        FROM governance.policy_decisions p
        JOIN inventory.ai_systems s
            ON s.system_id = p.system_id
        WHERE s.system_key = :system_key
        ORDER BY
            CASE p.severity
                WHEN 'CRITICAL' THEN 1
                WHEN 'HIGH' THEN 2
                WHEN 'MEDIUM' THEN 3
                WHEN 'LOW' THEN 4
                ELSE 5
            END,
            p.policy_name
    """

    return fetch_all(query, {"system_key": system_key})


@app.get("/api/systems/{system_key}/documents")
def get_system_documents(system_key: str) -> list[dict[str, Any]]:
    query = """
        SELECT
            d.document_name,
            d.document_category,
            d.required,
            d.completed,
            d.owner,
            d.due_date,
            d.completed_at
        FROM governance.required_documents d
        JOIN inventory.ai_systems s
            ON s.system_id = d.system_id
        WHERE s.system_key = :system_key
        ORDER BY d.completed ASC, d.due_date, d.document_name
    """

    return fetch_all(query, {"system_key": system_key})


@app.get("/api/systems/{system_key}/incident-evidence")
def get_system_incident_evidence(system_key: str) -> list[dict[str, Any]]:
    query = """
        SELECT
            i.external_incident_id,
            i.source_name,
            i.source_url,
            i.incident_title,
            i.affected_domain,
            i.harm_category,
            i.severity,
            i.ai_system_type,
            m.mapped_risk_category,
            m.mapped_control,
            m.relevance_reason
        FROM evidence.ai_risk_evidence_mappings m
        JOIN evidence.ai_incidents i
            ON i.incident_id = m.incident_id
        JOIN inventory.ai_systems s
            ON s.system_id = m.system_id
        WHERE s.system_key = :system_key
        ORDER BY i.severity, i.external_incident_id
    """

    return fetch_all(query, {"system_key": system_key})


@app.get("/api/systems/{system_key}/audit-report")
def get_system_audit_report(system_key: str) -> dict[str, Any]:
    report_path = f"docs/audit_reports/{system_key}_audit_report.md"

    try:
        with open(report_path, "r", encoding="utf-8") as file:
            report_text = file.read()
    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=404,
            detail="Audit report not found. Run python scripts\\aigov.py generate-reports first.",
        ) from exc

    return {
        "system_key": system_key,
        "report_text": report_text,
    }


@app.get("/api/review-queue")
def get_review_queue() -> list[dict[str, Any]]:
    query = """
        SELECT
            s.system_key,
            s.system_name,
            s.department,
            h.review_status,
            h.review_owner,
            h.due_date,
            h.required_reason,
            r.risk_tier,
            r.risk_score
        FROM governance.human_review_workflows h
        JOIN inventory.ai_systems s
            ON s.system_id = h.system_id
        LEFT JOIN governance.risk_assessments r
            ON r.system_id = s.system_id
           AND r.assessment_status = 'ACTIVE'
        ORDER BY h.due_date, s.system_key
    """

    return fetch_all(query)