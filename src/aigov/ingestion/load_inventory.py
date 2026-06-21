from __future__ import annotations

from pathlib import Path

import pandas as pd
from sqlalchemy import text

from src.aigov.database import get_engine


AI_SYSTEM_REQUIRED_COLUMNS = {
    "system_key",
    "system_name",
    "system_description",
    "department",
    "business_owner",
    "technical_owner",
    "governance_owner",
    "use_case",
    "business_value",
    "ai_type",
    "model_provider",
    "model_name",
    "model_version",
    "deployment_stage",
    "customer_facing",
    "employee_facing",
    "external_user_facing",
    "decision_impact",
    "autonomy_level",
    "uses_personal_data",
    "uses_sensitive_data",
    "uses_children_data",
    "uses_financial_data",
    "uses_health_data",
    "human_review_required",
    "human_review_present",
    "third_party_vendor",
    "vendor_name",
    "prohibited_use_case",
    "production_critical",
    "approval_status",
}

DATA_SOURCE_REQUIRED_COLUMNS = {
    "system_key",
    "source_name",
    "source_type",
    "source_system",
    "data_owner",
    "business_domain",
    "contains_pii",
    "contains_sensitive_data",
    "contains_financial_data",
    "contains_health_data",
    "quality_status",
    "lineage_available",
    "approved_for_ai_use",
    "retention_policy",
    "access_control_status",
}

EVIDENCE_MAPPING_REQUIRED_COLUMNS = {
    "system_key",
    "external_incident_id",
    "relevance_reason",
    "mapped_risk_category",
    "mapped_control",
}


BOOLEAN_COLUMNS = {
    "customer_facing",
    "employee_facing",
    "external_user_facing",
    "uses_personal_data",
    "uses_sensitive_data",
    "uses_children_data",
    "uses_financial_data",
    "uses_health_data",
    "human_review_required",
    "human_review_present",
    "third_party_vendor",
    "prohibited_use_case",
    "production_critical",
    "contains_pii",
    "contains_sensitive_data",
    "contains_financial_data",
    "contains_health_data",
    "lineage_available",
    "approved_for_ai_use",
}


def clean_value(value: object) -> object:
    if pd.isna(value):
        return None

    if isinstance(value, str):
        cleaned = value.strip()
        return cleaned if cleaned else None

    return value


def parse_bool(value: object) -> bool:
    if isinstance(value, bool):
        return value

    if pd.isna(value):
        return False

    return str(value).strip().lower() in {"true", "1", "yes", "y"}


def read_csv_with_required_columns(csv_path: str | Path, required_columns: set[str]) -> pd.DataFrame:
    path = Path(csv_path)

    if not path.exists():
        raise FileNotFoundError(f"CSV file not found: {path}")

    df = pd.read_csv(path)
    missing_columns = required_columns - set(df.columns)

    if missing_columns:
        missing = ", ".join(sorted(missing_columns))
        raise ValueError(f"{path.name} is missing required columns: {missing}")

    if df.empty:
        raise ValueError(f"{path.name} has no rows.")

    return df


def normalize_row(row: pd.Series) -> dict[str, object]:
    output: dict[str, object] = {}

    for column, value in row.items():
        if column in BOOLEAN_COLUMNS:
            output[column] = parse_bool(value)
        else:
            output[column] = clean_value(value)

    return output


def load_ai_systems(csv_path: str | Path) -> int:
    df = read_csv_with_required_columns(csv_path, AI_SYSTEM_REQUIRED_COLUMNS)

    insert_sql = text(
        """
        INSERT INTO inventory.ai_systems (
            system_key,
            system_name,
            system_description,
            department,
            business_owner,
            technical_owner,
            governance_owner,
            use_case,
            business_value,
            ai_type,
            model_provider,
            model_name,
            model_version,
            deployment_stage,
            customer_facing,
            employee_facing,
            external_user_facing,
            decision_impact,
            autonomy_level,
            uses_personal_data,
            uses_sensitive_data,
            uses_children_data,
            uses_financial_data,
            uses_health_data,
            human_review_required,
            human_review_present,
            third_party_vendor,
            vendor_name,
            prohibited_use_case,
            production_critical,
            approval_status
        )
        VALUES (
            :system_key,
            :system_name,
            :system_description,
            :department,
            :business_owner,
            :technical_owner,
            :governance_owner,
            :use_case,
            :business_value,
            :ai_type,
            :model_provider,
            :model_name,
            :model_version,
            :deployment_stage,
            :customer_facing,
            :employee_facing,
            :external_user_facing,
            :decision_impact,
            :autonomy_level,
            :uses_personal_data,
            :uses_sensitive_data,
            :uses_children_data,
            :uses_financial_data,
            :uses_health_data,
            :human_review_required,
            :human_review_present,
            :third_party_vendor,
            :vendor_name,
            :prohibited_use_case,
            :production_critical,
            :approval_status
        )
        ON CONFLICT (system_key) DO UPDATE SET
            system_name = EXCLUDED.system_name,
            system_description = EXCLUDED.system_description,
            department = EXCLUDED.department,
            business_owner = EXCLUDED.business_owner,
            technical_owner = EXCLUDED.technical_owner,
            governance_owner = EXCLUDED.governance_owner,
            use_case = EXCLUDED.use_case,
            business_value = EXCLUDED.business_value,
            ai_type = EXCLUDED.ai_type,
            model_provider = EXCLUDED.model_provider,
            model_name = EXCLUDED.model_name,
            model_version = EXCLUDED.model_version,
            deployment_stage = EXCLUDED.deployment_stage,
            customer_facing = EXCLUDED.customer_facing,
            employee_facing = EXCLUDED.employee_facing,
            external_user_facing = EXCLUDED.external_user_facing,
            decision_impact = EXCLUDED.decision_impact,
            autonomy_level = EXCLUDED.autonomy_level,
            uses_personal_data = EXCLUDED.uses_personal_data,
            uses_sensitive_data = EXCLUDED.uses_sensitive_data,
            uses_children_data = EXCLUDED.uses_children_data,
            uses_financial_data = EXCLUDED.uses_financial_data,
            uses_health_data = EXCLUDED.uses_health_data,
            human_review_required = EXCLUDED.human_review_required,
            human_review_present = EXCLUDED.human_review_present,
            third_party_vendor = EXCLUDED.third_party_vendor,
            vendor_name = EXCLUDED.vendor_name,
            prohibited_use_case = EXCLUDED.prohibited_use_case,
            production_critical = EXCLUDED.production_critical,
            approval_status = EXCLUDED.approval_status,
            updated_at = CURRENT_TIMESTAMP
        """
    )

    engine = get_engine()
    count = 0

    with engine.begin() as connection:
        for _, row in df.iterrows():
            connection.execute(insert_sql, normalize_row(row))
            count += 1

    return count


def load_ai_data_sources(csv_path: str | Path) -> int:
    df = read_csv_with_required_columns(csv_path, DATA_SOURCE_REQUIRED_COLUMNS)

    insert_sql = text(
        """
        INSERT INTO inventory.ai_data_sources (
            system_id,
            source_name,
            source_type,
            source_system,
            data_owner,
            business_domain,
            contains_pii,
            contains_sensitive_data,
            contains_financial_data,
            contains_health_data,
            quality_status,
            lineage_available,
            approved_for_ai_use,
            retention_policy,
            access_control_status
        )
        SELECT
            s.system_id,
            :source_name,
            :source_type,
            :source_system,
            :data_owner,
            :business_domain,
            :contains_pii,
            :contains_sensitive_data,
            :contains_financial_data,
            :contains_health_data,
            :quality_status,
            :lineage_available,
            :approved_for_ai_use,
            :retention_policy,
            :access_control_status
        FROM inventory.ai_systems s
        WHERE s.system_key = :system_key
        """
    )

    delete_sql = text(
        """
        DELETE FROM inventory.ai_data_sources
        WHERE system_id IN (
            SELECT system_id
            FROM inventory.ai_systems
            WHERE system_key = ANY(:system_keys)
        )
        """
    )

    system_keys = df["system_key"].dropna().astype(str).unique().tolist()
    engine = get_engine()
    count = 0

    with engine.begin() as connection:
        connection.execute(delete_sql, {"system_keys": system_keys})

        for _, row in df.iterrows():
            connection.execute(insert_sql, normalize_row(row))
            count += 1

    return count


def load_ai_risk_evidence_mappings(csv_path: str | Path) -> int:
    df = read_csv_with_required_columns(csv_path, EVIDENCE_MAPPING_REQUIRED_COLUMNS)

    insert_sql = text(
        """
        INSERT INTO evidence.ai_risk_evidence_mappings (
            system_id,
            incident_id,
            relevance_reason,
            mapped_risk_category,
            mapped_control
        )
        SELECT
            s.system_id,
            i.incident_id,
            :relevance_reason,
            :mapped_risk_category,
            :mapped_control
        FROM inventory.ai_systems s
        JOIN evidence.ai_incidents i
            ON i.external_incident_id = :external_incident_id
        WHERE s.system_key = :system_key
        """
    )

    delete_sql = text(
        """
        DELETE FROM evidence.ai_risk_evidence_mappings
        WHERE system_id IN (
            SELECT system_id
            FROM inventory.ai_systems
            WHERE system_key = ANY(:system_keys)
        )
        """
    )

    system_keys = df["system_key"].dropna().astype(str).unique().tolist()
    engine = get_engine()
    count = 0

    with engine.begin() as connection:
        connection.execute(delete_sql, {"system_keys": system_keys})

        for _, row in df.iterrows():
            connection.execute(insert_sql, normalize_row(row))
            count += 1

    return count


def load_inventory_bundle(
    systems_csv_path: str | Path,
    data_sources_csv_path: str | Path,
    evidence_mappings_csv_path: str | Path,
) -> dict[str, int]:
    systems_count = load_ai_systems(systems_csv_path)
    data_sources_count = load_ai_data_sources(data_sources_csv_path)
    mappings_count = load_ai_risk_evidence_mappings(evidence_mappings_csv_path)

    return {
        "systems": systems_count,
        "data_sources": data_sources_count,
        "risk_evidence_mappings": mappings_count,
    }