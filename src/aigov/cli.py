from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from src.aigov.database import execute_sql_file
from src.aigov.evidence.document_checker import (
    calculate_document_summary,
    run_document_completeness_check,
)
from src.aigov.evidence.review_scheduler import run_review_scheduling
from src.aigov.ingestion.load_incidents import load_incidents_from_csv
from src.aigov.ingestion.load_inventory import load_inventory_bundle
from src.aigov.policy.evaluator import (
    run_policy_evaluation,
    strongest_decision_for_system,
)
from src.aigov.reports.audit_report import generate_all_audit_reports
from src.aigov.risk.scorer import run_risk_scoring


PROJECT_ROOT = Path(__file__).resolve().parents[2]
SAMPLE_DIR = PROJECT_ROOT / "data" / "sample"
POLICY_FILE = PROJECT_ROOT / "policies" / "ai_governance_policies.yml"
SCHEMA_FILE = PROJECT_ROOT / "sql" / "001_create_full_schema.sql"
AUDIT_REPORT_DIR = PROJECT_ROOT / "docs" / "audit_reports"

INCIDENTS_CSV = SAMPLE_DIR / "ai_risk_evidence.csv"
SYSTEMS_CSV = SAMPLE_DIR / "ai_system_inventory.csv"
DATA_SOURCES_CSV = SAMPLE_DIR / "ai_data_sources.csv"
EVIDENCE_MAPPINGS_CSV = SAMPLE_DIR / "ai_risk_evidence_mappings.csv"


app = typer.Typer(
    help="AIGov Control Tower CLI for running AI governance workflows.",
    no_args_is_help=True,
)
console = Console()


def print_section(title: str) -> None:
    console.print()
    console.print(f"[bold cyan]{title}[/bold cyan]")


def run_setup_database_step() -> None:
    execute_sql_file(SCHEMA_FILE)
    console.print(f"[green]OK[/green] Applied schema: {SCHEMA_FILE}")


def run_incident_ingestion_step() -> int:
    count = load_incidents_from_csv(INCIDENTS_CSV)
    console.print(f"[green]OK[/green] Loaded incident evidence records: {count}")
    return count


def run_inventory_ingestion_step() -> dict[str, int]:
    result = load_inventory_bundle(
        systems_csv_path=SYSTEMS_CSV,
        data_sources_csv_path=DATA_SOURCES_CSV,
        evidence_mappings_csv_path=EVIDENCE_MAPPINGS_CSV,
    )

    console.print(
        "[green]OK[/green] Loaded inventory bundle: "
        f"{result['systems']} systems, "
        f"{result['data_sources']} data sources, "
        f"{result['risk_evidence_mappings']} evidence mappings"
    )

    return result


def run_risk_scoring_step() -> int:
    risk_scores = run_risk_scoring()

    table = Table(title="Risk Scoring Summary")
    table.add_column("System")
    table.add_column("Score")
    table.add_column("Tier")

    for score in risk_scores:
        table.add_row(score.system_key, str(score.risk_score), score.risk_tier)

    console.print(table)
    return len(risk_scores)


def run_policy_evaluation_step() -> int:
    decisions = run_policy_evaluation(POLICY_FILE)
    strongest = strongest_decision_for_system(decisions)

    table = Table(title="Policy Decision Summary")
    table.add_column("System")
    table.add_column("Decision")
    table.add_column("Policy")

    for system_key, decision in sorted(strongest.items()):
        table.add_row(system_key, decision.decision, decision.policy_name)

    console.print(table)
    console.print(f"[green]OK[/green] Total policy matches: {len(decisions)}")

    return len(decisions)


def run_document_check_step() -> int:
    documents = run_document_completeness_check()
    summary = calculate_document_summary(documents)

    table = Table(title="Documentation Completeness Summary")
    table.add_column("System")
    table.add_column("Completed")
    table.add_column("Required")
    table.add_column("Completion Rate")

    for system_key, values in sorted(summary.items()):
        table.add_row(
            system_key,
            str(values["completed"]),
            str(values["required"]),
            str(values["completion_rate"]),
        )

    console.print(table)
    console.print(f"[green]OK[/green] Total document records: {len(documents)}")

    return len(documents)


def run_review_scheduling_step() -> tuple[int, int]:
    workflows, schedules = run_review_scheduling()

    table = Table(title="Human Review Workflow Summary")
    table.add_column("System")
    table.add_column("Status")
    table.add_column("Due Date")

    for workflow in workflows:
        table.add_row(
            workflow.system_key,
            workflow.review_status,
            str(workflow.due_date.date()),
        )

    console.print(table)
    console.print(f"[green]OK[/green] Human review workflows: {len(workflows)}")
    console.print(f"[green]OK[/green] Reassessment schedules: {len(schedules)}")

    return len(workflows), len(schedules)


def run_report_generation_step() -> int:
    output_paths = generate_all_audit_reports(AUDIT_REPORT_DIR)

    console.print(f"[green]OK[/green] Generated audit reports: {len(output_paths)}")
    console.print(f"[green]OK[/green] Output directory: {AUDIT_REPORT_DIR}")

    return len(output_paths)


@app.command("setup-db")
def setup_db_command() -> None:
    """Apply the PostgreSQL schema."""
    print_section("Database Setup")
    run_setup_database_step()


@app.command("load-incidents")
def load_incidents_command() -> None:
    """Load AI incident evidence records."""
    print_section("Incident Evidence Ingestion")
    run_incident_ingestion_step()


@app.command("load-inventory")
def load_inventory_command() -> None:
    """Load AI system inventory, data sources, and incident mappings."""
    print_section("AI Inventory Ingestion")
    run_inventory_ingestion_step()


@app.command("score-risk")
def score_risk_command() -> None:
    """Run AI system risk scoring."""
    print_section("Risk Scoring")
    run_risk_scoring_step()


@app.command("evaluate-policies")
def evaluate_policies_command() -> None:
    """Evaluate AI governance policies."""
    print_section("Policy Evaluation")
    run_policy_evaluation_step()


@app.command("check-documents")
def check_documents_command() -> None:
    """Run documentation completeness checks."""
    print_section("Documentation Completeness")
    run_document_check_step()


@app.command("schedule-reviews")
def schedule_reviews_command() -> None:
    """Generate human review workflows and reassessment schedules."""
    print_section("Review Scheduling")
    run_review_scheduling_step()


@app.command("generate-reports")
def generate_reports_command() -> None:
    """Generate markdown audit reports."""
    print_section("Audit Report Generation")
    run_report_generation_step()


@app.command("run-pipeline")
def run_pipeline_command(
    setup_database: bool = typer.Option(
        False,
        "--setup-database",
        help="Apply the database schema before running the pipeline.",
    )
) -> None:
    """Run the full AI governance control tower pipeline."""
    console.print("[bold]Running AIGov Control Tower pipeline[/bold]")

    if setup_database:
        print_section("Database Setup")
        run_setup_database_step()

    print_section("Incident Evidence Ingestion")
    incident_count = run_incident_ingestion_step()

    print_section("AI Inventory Ingestion")
    inventory_result = run_inventory_ingestion_step()

    print_section("Risk Scoring")
    risk_count = run_risk_scoring_step()

    print_section("Policy Evaluation")
    policy_count = run_policy_evaluation_step()

    print_section("Documentation Completeness")
    document_count = run_document_check_step()

    print_section("Review Scheduling")
    workflow_count, schedule_count = run_review_scheduling_step()

    print_section("Audit Report Generation")
    report_count = run_report_generation_step()

    print_section("Pipeline Complete")

    summary = Table(title="Pipeline Output Summary")
    summary.add_column("Layer")
    summary.add_column("Records")

    summary.add_row("Incident evidence", str(incident_count))
    summary.add_row("AI systems", str(inventory_result["systems"]))
    summary.add_row("Data sources", str(inventory_result["data_sources"]))
    summary.add_row("Risk evidence mappings", str(inventory_result["risk_evidence_mappings"]))
    summary.add_row("Risk assessments", str(risk_count))
    summary.add_row("Policy decisions", str(policy_count))
    summary.add_row("Required documents", str(document_count))
    summary.add_row("Human review workflows", str(workflow_count))
    summary.add_row("Reassessment schedules", str(schedule_count))
    summary.add_row("Audit reports", str(report_count))

    console.print(summary)


if __name__ == "__main__":
    app()