CREATE SCHEMA IF NOT EXISTS inventory;
CREATE SCHEMA IF NOT EXISTS governance;
CREATE SCHEMA IF NOT EXISTS evidence;
CREATE SCHEMA IF NOT EXISTS monitoring;
CREATE SCHEMA IF NOT EXISTS audit;

CREATE TABLE IF NOT EXISTS inventory.ai_systems (
    system_id SERIAL PRIMARY KEY,
    system_key TEXT NOT NULL UNIQUE,
    system_name TEXT NOT NULL,
    system_description TEXT,
    department TEXT NOT NULL,
    business_owner TEXT,
    technical_owner TEXT,
    governance_owner TEXT,
    use_case TEXT NOT NULL,
    business_value TEXT,
    ai_type TEXT NOT NULL,
    model_provider TEXT NOT NULL,
    model_name TEXT,
    model_version TEXT,
    deployment_stage TEXT NOT NULL,
    customer_facing BOOLEAN NOT NULL DEFAULT FALSE,
    employee_facing BOOLEAN NOT NULL DEFAULT TRUE,
    external_user_facing BOOLEAN NOT NULL DEFAULT FALSE,
    decision_impact TEXT NOT NULL,
    autonomy_level TEXT NOT NULL,
    uses_personal_data BOOLEAN NOT NULL DEFAULT FALSE,
    uses_sensitive_data BOOLEAN NOT NULL DEFAULT FALSE,
    uses_children_data BOOLEAN NOT NULL DEFAULT FALSE,
    uses_financial_data BOOLEAN NOT NULL DEFAULT FALSE,
    uses_health_data BOOLEAN NOT NULL DEFAULT FALSE,
    human_review_required BOOLEAN NOT NULL DEFAULT FALSE,
    human_review_present BOOLEAN NOT NULL DEFAULT FALSE,
    third_party_vendor BOOLEAN NOT NULL DEFAULT FALSE,
    vendor_name TEXT,
    prohibited_use_case BOOLEAN NOT NULL DEFAULT FALSE,
    production_critical BOOLEAN NOT NULL DEFAULT FALSE,
    approval_status TEXT NOT NULL DEFAULT 'NOT_REVIEWED',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS inventory.ai_data_sources (
    data_source_id SERIAL PRIMARY KEY,
    system_id INTEGER NOT NULL REFERENCES inventory.ai_systems(system_id) ON DELETE CASCADE,
    source_name TEXT NOT NULL,
    source_type TEXT NOT NULL,
    source_system TEXT,
    data_owner TEXT,
    business_domain TEXT,
    contains_pii BOOLEAN NOT NULL DEFAULT FALSE,
    contains_sensitive_data BOOLEAN NOT NULL DEFAULT FALSE,
    contains_financial_data BOOLEAN NOT NULL DEFAULT FALSE,
    contains_health_data BOOLEAN NOT NULL DEFAULT FALSE,
    quality_status TEXT NOT NULL,
    lineage_available BOOLEAN NOT NULL DEFAULT FALSE,
    approved_for_ai_use BOOLEAN NOT NULL DEFAULT FALSE,
    retention_policy TEXT,
    access_control_status TEXT NOT NULL DEFAULT 'UNKNOWN',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS governance.risk_assessments (
    assessment_id SERIAL PRIMARY KEY,
    system_id INTEGER NOT NULL REFERENCES inventory.ai_systems(system_id) ON DELETE CASCADE,
    risk_score NUMERIC(5,2) NOT NULL,
    risk_tier TEXT NOT NULL,
    business_impact_score INTEGER NOT NULL,
    data_sensitivity_score INTEGER NOT NULL,
    autonomy_score INTEGER NOT NULL,
    exposure_score INTEGER NOT NULL,
    vendor_risk_score INTEGER NOT NULL,
    documentation_risk_score INTEGER NOT NULL,
    risk_factors TEXT,
    assessment_status TEXT NOT NULL DEFAULT 'ACTIVE',
    assessed_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS governance.policy_decisions (
    decision_id SERIAL PRIMARY KEY,
    system_id INTEGER NOT NULL REFERENCES inventory.ai_systems(system_id) ON DELETE CASCADE,
    policy_name TEXT NOT NULL,
    policy_category TEXT NOT NULL,
    decision TEXT NOT NULL,
    severity TEXT NOT NULL,
    reason TEXT NOT NULL,
    control_required TEXT,
    evaluated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS governance.required_documents (
    document_id SERIAL PRIMARY KEY,
    system_id INTEGER NOT NULL REFERENCES inventory.ai_systems(system_id) ON DELETE CASCADE,
    document_name TEXT NOT NULL,
    document_category TEXT NOT NULL,
    required BOOLEAN NOT NULL DEFAULT TRUE,
    completed BOOLEAN NOT NULL DEFAULT FALSE,
    owner TEXT,
    due_date DATE,
    completed_at TIMESTAMP,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS governance.human_review_workflows (
    review_id SERIAL PRIMARY KEY,
    system_id INTEGER NOT NULL REFERENCES inventory.ai_systems(system_id) ON DELETE CASCADE,
    review_type TEXT NOT NULL,
    review_owner TEXT,
    review_status TEXT NOT NULL DEFAULT 'NOT_STARTED',
    required_reason TEXT NOT NULL,
    due_date DATE,
    completed_at TIMESTAMP,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS governance.reassessment_schedule (
    schedule_id SERIAL PRIMARY KEY,
    system_id INTEGER NOT NULL REFERENCES inventory.ai_systems(system_id) ON DELETE CASCADE,
    risk_tier TEXT NOT NULL,
    review_frequency_days INTEGER NOT NULL,
    last_reviewed_at TIMESTAMP,
    next_review_due_at TIMESTAMP NOT NULL,
    review_status TEXT NOT NULL DEFAULT 'SCHEDULED',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS evidence.governance_evidence (
    evidence_id SERIAL PRIMARY KEY,
    system_id INTEGER NOT NULL REFERENCES inventory.ai_systems(system_id) ON DELETE CASCADE,
    evidence_type TEXT NOT NULL,
    evidence_name TEXT NOT NULL,
    evidence_status TEXT NOT NULL,
    evidence_summary TEXT,
    source_location TEXT,
    collected_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS evidence.ai_incidents (
    incident_id SERIAL PRIMARY KEY,
    external_incident_id TEXT UNIQUE,
    source_name TEXT NOT NULL,
    source_url TEXT,
    incident_title TEXT NOT NULL,
    incident_description TEXT,
    incident_date DATE,
    affected_domain TEXT,
    harm_category TEXT,
    severity TEXT,
    ai_system_type TEXT,
    organization_involved TEXT,
    evidence_status TEXT NOT NULL DEFAULT 'IMPORTED',
    imported_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS evidence.ai_incident_reports (
    report_id SERIAL PRIMARY KEY,
    incident_id INTEGER NOT NULL REFERENCES evidence.ai_incidents(incident_id) ON DELETE CASCADE,
    report_title TEXT,
    report_url TEXT,
    publisher TEXT,
    published_date DATE,
    report_summary TEXT,
    imported_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS evidence.ai_risk_evidence_mappings (
    mapping_id SERIAL PRIMARY KEY,
    system_id INTEGER NOT NULL REFERENCES inventory.ai_systems(system_id) ON DELETE CASCADE,
    incident_id INTEGER NOT NULL REFERENCES evidence.ai_incidents(incident_id) ON DELETE CASCADE,
    relevance_reason TEXT NOT NULL,
    mapped_risk_category TEXT NOT NULL,
    mapped_control TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS monitoring.ai_monitoring_metrics (
    metric_id SERIAL PRIMARY KEY,
    system_id INTEGER NOT NULL REFERENCES inventory.ai_systems(system_id) ON DELETE CASCADE,
    metric_name TEXT NOT NULL,
    metric_value NUMERIC(10,4),
    metric_unit TEXT,
    metric_status TEXT NOT NULL,
    threshold_value NUMERIC(10,4),
    measured_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS monitoring.governance_kpis (
    kpi_id SERIAL PRIMARY KEY,
    kpi_name TEXT NOT NULL,
    kpi_value NUMERIC(10,4) NOT NULL,
    kpi_unit TEXT,
    kpi_status TEXT NOT NULL,
    calculated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS audit.audit_events (
    event_id SERIAL PRIMARY KEY,
    system_id INTEGER REFERENCES inventory.ai_systems(system_id) ON DELETE SET NULL,
    event_type TEXT NOT NULL,
    event_summary TEXT NOT NULL,
    event_source TEXT NOT NULL,
    actor TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);