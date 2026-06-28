# AIGov Control Tower — Project Summary

## One-Line Summary

AIGov Control Tower is a full-stack AI governance platform that inventories AI systems, scores risk, evaluates governance policies, tracks documentation gaps, schedules reviews, and generates audit-ready evidence.

---

## Short Summary

AIGov Control Tower is a portfolio project focused on practical AI governance and data governance.

It uses PostgreSQL, Python, FastAPI, and React to simulate how an organization could manage AI systems from intake to governance review. The platform tracks AI use cases, data sources, risk factors, policy decisions, documentation readiness, human review obligations, reassessment timelines, and audit evidence.

The strongest demo scenario is a blocked high-risk employment AI system, showing how the platform identifies policy violations, missing controls, documentation gaps, and audit conclusions through a repeatable governance pipeline.

---

## Technical Stack

```text id="hex0pg"
PostgreSQL
Python
SQLAlchemy
FastAPI
React
Vite
YAML
Typer
Rich
GitHub Actions
```

---

## What the Project Does

AIGov Control Tower performs the following workflow:

```text id="ee7wjy"
1. Loads AI system inventory
2. Loads AI data source metadata
3. Maps systems to external AI incident evidence
4. Scores AI system risk
5. Evaluates YAML governance policies
6. Identifies required and missing governance documents
7. Schedules human review workflows
8. Schedules AI system reassessment cadences
9. Generates audit-ready Markdown reports
10. Displays governance state in a React command center
```

---

## Key Features

* AI system inventory
* Data source governance tracking
* External AI incident evidence mapping
* Explainable AI risk scoring
* YAML policy-as-code evaluation
* Documentation completeness checks
* Human review workflow scheduling
* Reassessment scheduling
* Audit report generation
* FastAPI read-only governance API
* React governance command center
* GitHub Actions CI for backend and frontend checks

---

## Main Demo System

```text id="y41udt"
AI-005 — Autonomous Termination Recommender
```

This system is blocked because it represents a high-risk employment AI use case with insufficient human review and missing governance documentation.

The platform shows:

```text id="3svi74"
Risk Tier: BLOCKED
Policy Decision: BLOCKED
Review Status: BLOCKED_REVIEW_REQUIRED
Documentation Completion: 0 / 12
Reassessment Frequency: 7 days
Mapped Evidence: employment automation risk
```

---

## Why the Project Matters

AIGov Control Tower demonstrates how AI governance can be implemented as a repeatable system instead of a manual checklist.

The project connects:

* AI use case inventory
* Data governance
* Risk management
* Policy enforcement
* Documentation readiness
* Human review
* Reassessment
* Audit evidence

This makes it relevant for AI governance, data governance, responsible AI, model risk management, AI product operations, analytics engineering, and data quality roles.

---

## Resume-Friendly Bullet Version

* Built AIGov Control Tower, a full-stack AI governance platform using PostgreSQL, Python, FastAPI, and React to inventory AI systems, score risk, evaluate governance policies, and generate audit-ready evidence.
* Designed a YAML policy-as-code engine to classify AI systems as approved, requiring review, approved with controls, or blocked based on governance risk conditions.
* Developed backend pipeline for AI system inventory ingestion, data source governance tracking, external incident evidence mapping, documentation completeness checks, human review scheduling, reassessment scheduling, and audit report generation.
* Built a React governance command center displaying AI system risk posture, policy decisions, documentation gaps, evidence mappings, review obligations, and audit report previews.
* Added GitHub Actions CI to validate backend imports and frontend production builds.

---

## Interview Explanation

AIGov Control Tower is a full-stack project I built to explore how AI governance can move beyond static policies and spreadsheets.

The backend uses PostgreSQL and Python to create a governance evidence pipeline. It loads AI systems, evaluates data and risk factors, applies YAML governance policies, checks documentation readiness, schedules review obligations, and generates audit reports.

The FastAPI layer exposes this governance evidence through read-only endpoints, and the React frontend presents it as a command center for reviewing system-level AI governance posture.

The main demo system is an autonomous termination recommender, which is blocked because it represents a high-risk employment AI use case without sufficient human review and governance documentation.

---

## LinkedIn Short Version

AIGov Control Tower is a full-stack AI governance platform I built to show how organizations can manage AI use cases with evidence instead of spreadsheets.

It inventories AI systems, scores risk, evaluates YAML governance policies, checks documentation gaps, schedules review workflows, maps external incident evidence, and generates audit-ready reports.

Tech stack: PostgreSQL, Python, FastAPI, React, Vite, YAML, SQLAlchemy, GitHub Actions.

The main demo shows how a high-risk employment AI system is blocked through a repeatable governance workflow.
