from __future__ import annotations

from pathlib import Path

import pandas as pd
from sqlalchemy import text

from src.aigov.database import get_engine


REQUIRED_COLUMNS = {
    "external_incident_id",
    "source_name",
    "source_url",
    "incident_title",
    "incident_description",
    "incident_date",
    "affected_domain",
    "harm_category",
    "severity",
    "ai_system_type",
    "organization_involved",
}


def validate_incident_dataframe(df: pd.DataFrame) -> None:
    missing_columns = REQUIRED_COLUMNS - set(df.columns)

    if missing_columns:
        missing = ", ".join(sorted(missing_columns))
        raise ValueError(f"Incident CSV is missing required columns: {missing}")

    if df.empty:
        raise ValueError("Incident CSV has no rows.")

    if df["incident_title"].isna().any():
        raise ValueError("Incident CSV contains rows with missing incident_title.")


def normalize_date(value: object) -> object:
    if pd.isna(value) or value == "":
        return None

    parsed = pd.to_datetime(value, errors="coerce")

    if pd.isna(parsed):
        return None

    return parsed.date()


def load_incidents_from_csv(csv_path: str | Path) -> int:
    path = Path(csv_path)

    if not path.exists():
        raise FileNotFoundError(f"CSV file not found: {path}")

    df = pd.read_csv(path)
    validate_incident_dataframe(df)

    engine = get_engine()
    inserted_count = 0

    insert_sql = text(
        """
        INSERT INTO evidence.ai_incidents (
            external_incident_id,
            source_name,
            source_url,
            incident_title,
            incident_description,
            incident_date,
            affected_domain,
            harm_category,
            severity,
            ai_system_type,
            organization_involved
        )
        VALUES (
            :external_incident_id,
            :source_name,
            :source_url,
            :incident_title,
            :incident_description,
            :incident_date,
            :affected_domain,
            :harm_category,
            :severity,
            :ai_system_type,
            :organization_involved
        )
        ON CONFLICT (external_incident_id) DO UPDATE SET
            source_name = EXCLUDED.source_name,
            source_url = EXCLUDED.source_url,
            incident_title = EXCLUDED.incident_title,
            incident_description = EXCLUDED.incident_description,
            incident_date = EXCLUDED.incident_date,
            affected_domain = EXCLUDED.affected_domain,
            harm_category = EXCLUDED.harm_category,
            severity = EXCLUDED.severity,
            ai_system_type = EXCLUDED.ai_system_type,
            organization_involved = EXCLUDED.organization_involved
        """
    )

    with engine.begin() as connection:
        for _, row in df.iterrows():
            connection.execute(
                insert_sql,
                {
                    "external_incident_id": clean_value(row["external_incident_id"]),
                    "source_name": clean_value(row["source_name"]),
                    "source_url": clean_value(row["source_url"]),
                    "incident_title": clean_value(row["incident_title"]),
                    "incident_description": clean_value(row["incident_description"]),
                    "incident_date": normalize_date(row["incident_date"]),
                    "affected_domain": clean_value(row["affected_domain"]),
                    "harm_category": clean_value(row["harm_category"]),
                    "severity": clean_value(row["severity"]),
                    "ai_system_type": clean_value(row["ai_system_type"]),
                    "organization_involved": clean_value(row["organization_involved"]),
                },
            )
            inserted_count += 1

    return inserted_count


def clean_value(value: object) -> object:
    if pd.isna(value):
        return None

    if isinstance(value, str):
        cleaned = value.strip()
        return cleaned if cleaned else None

    return value