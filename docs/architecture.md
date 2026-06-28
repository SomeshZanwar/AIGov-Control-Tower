# AIGov Control Tower — Architecture

## Overview

AIGov Control Tower is a full-stack AI governance platform designed to help teams manage AI systems from intake to audit evidence.

The system is built around one core governance question:

> Can this AI system be approved, monitored, and defended with evidence?

The architecture separates governance logic, evidence storage, API access, and frontend presentation into clear layers.

```text
PostgreSQL database
        ↓
Python governance pipeline
        ↓
FastAPI read-only API
        ↓
React governance command center
```

---

## Design Goals

The project was designed with the following goals:

1. Create a realistic AI governance workflow, not a static dashboard.
2. Store governance evidence in a relational database.
3. Evaluate AI systems using repeatable scoring and policy logic.
4. Generate audit-ready evidence from system data.
5. Present governance state through a product-style command center.
6. Keep the frontend read-only so governance state is produced by controlled backend processes.
7. Make the project easy to run, inspect, and extend.

---

## High-Level System Flow

```text
Sample AI inventory
        ↓
Data source records
        ↓
External incident evidence mappings
        ↓
Risk scoring engine
        ↓
YAML policy engine
        ↓
Documentation completeness checker
        ↓
Human review scheduler
        ↓
Reassessment scheduler
        ↓
Audit report generator
        ↓
FastAPI endpoints
        ↓
React command center
```

The backend pipeline produces governance decisions and evidence. The frontend displays that evidence but does not mutate governance state.

---

## Layer 1 — PostgreSQL Database

PostgreSQL is the source of truth for the governance platform.

The database is organized into domain-specific schemas:

| Schema       | Purpose                                                                        |
| ------------ | ------------------------------------------------------------------------------ |
| `inventory`  | AI systems and data sources                                                    |
| `governance` | Risk assessments, policy decisions, required documents, reviews, reassessments |
| `evidence`   | External AI incident evidence and system-to-risk mappings                      |
| `monitoring` | Governance KPIs and monitoring metrics                                         |
| `audit`      | Audit event records                                                            |

This schema separation makes the system easier to reason about because inventory, governance decisions, supporting evidence, and audit records are not mixed together.

---

## Layer 2 — Python Governance Pipeline

The Python pipeline is responsible for creating and updating governance evidence.

It performs the following steps:

1. Load AI incident evidence.
2. Load AI system inventory.
3. Load AI data sources.
4. Load AI-to-incident-evidence mappings.
5. Score AI system risk.
6. Evaluate YAML governance policies.
7. Check documentation completeness.
8. Schedule human review workflows.
9. Schedule reassessment cadences.
10. Generate audit reports.

The pipeline can be run through the CLI:

```cmd
python scripts\aigov.py run-pipeline
```

For first-time setup, it can also apply the database schema:

```cmd
python scripts\aigov.py run-pipeline --setup-database
```

---

## Layer 3 — Risk Scoring Engine

The risk scoring engine calculates AI governance risk using system-level metadata.

Risk factors include:

* Business impact
* Data sensitivity
* Autonomy level
* Customer or employee exposure
* Vendor dependency
* Documentation readiness
* Prohibited use-case status

The output is stored in `governance.risk_assessments`.

Example risk tiers:

| Risk Tier  | Meaning                                                    |
| ---------- | ---------------------------------------------------------- |
| `LOW`      | Lower-risk system with limited exposure                    |
| `MODERATE` | System requiring governance attention or controls          |
| `HIGH`     | Higher-impact system requiring stronger review             |
| `BLOCKED`  | System should not proceed without formal governance review |

The risk engine is intentionally explainable. It does not only output a score; it also stores risk factors that explain why a system received its tier.

---

## Layer 4 — YAML Policy Engine

Governance policies are defined in YAML instead of being hardcoded directly into application logic.

Policy categories include:

* Prohibited use
* Human review
* Data governance
* Customer-facing AI controls
* Vendor risk
* Risk management

The policy engine evaluates each AI system against those policies and stores matched policy decisions in `governance.policy_decisions`.

Possible decisions include:

```text
APPROVED
APPROVED_WITH_CONTROLS
REQUIRES_REVIEW
BLOCKED
```

This design allows policy logic to be updated separately from the frontend and database schema.

---

## Layer 5 — Documentation Completeness Checker

AI governance often fails because required documentation is missing, inconsistent, or scattered.

The documentation checker determines which governance documents are required for each AI system based on its risk profile.

Required documents may include:

* Business Case
* AI Risk Assessment
* Data Source Inventory
* Monitoring Plan
* Incident Response Plan
* Privacy Review
* Vendor Risk Review
* Human Review Workflow
* Bias and Fairness Assessment
* Governance Committee Approval

The output is stored in `governance.required_documents`.

The frontend then displays documentation readiness as part of the system dossier.

---

## Layer 6 — Human Review and Reassessment Scheduling

The review scheduler creates governance follow-up obligations.

It generates:

* Human review workflows
* Review reasons
* Review owners
* Review due dates
* Reassessment frequencies
* Next reassessment dates

Blocked or higher-risk systems receive shorter reassessment cadences.

Example:

| Risk Tier  | Reassessment Frequency |
| ---------- | ---------------------: |
| `BLOCKED`  |                 7 days |
| `HIGH`     |                30 days |
| `MODERATE` |                90 days |
| `LOW`      |               180 days |

This gives the platform a monitoring layer instead of treating governance as a one-time approval event.

---

## Layer 7 — Audit Report Generator

The audit report generator creates Markdown governance reports from the database.

Each report includes:

* System overview
* Risk assessment
* Data and privacy context
* Data sources
* Policy decisions
* Documentation completeness
* Missing documents
* Human review status
* Reassessment status
* External incident evidence mappings
* Audit conclusion

Generated reports are written to:

```text
docs/audit_reports/
```

This folder is ignored by Git because reports are reproducible from the database.

---

## Layer 8 — FastAPI API Layer

FastAPI exposes governance evidence through read-only endpoints.

The API exists to separate the frontend from direct database access.

Key endpoints include:

```text
GET /health
GET /api/summary
GET /api/systems
GET /api/systems/{system_key}
GET /api/systems/{system_key}/data-sources
GET /api/systems/{system_key}/policy-decisions
GET /api/systems/{system_key}/documents
GET /api/systems/{system_key}/incident-evidence
GET /api/systems/{system_key}/audit-report
GET /api/review-queue
```

The API does not currently mutate governance state. This is intentional for the current version because governance decisions should be produced by the pipeline, not manually edited through the UI.

---

## Layer 9 — React Governance Command Center

The React frontend presents governance state in a product-style interface.

It includes:

* AI system registry rail
* Governance command metrics
* Risk heat strip
* Governance action queue
* System-level dossier
* Policy decision memo
* Evidence trail
* Documentation gap board
* Data source readiness view
* External incident evidence view
* Audit report preview

The frontend calls the FastAPI backend at:

```text
http://localhost:8000
```

The frontend runs locally at:

```text
http://localhost:5173
```

---

## Read-Only Frontend Design

The React frontend is intentionally read-only.

This prevents the UI from becoming a loose manual editing layer. Instead, governance state is created through repeatable backend logic:

```text
Inventory + evidence + policies
        ↓
Pipeline execution
        ↓
Database records
        ↓
API
        ↓
Frontend display
```

This design better reflects real governance systems, where decisions should be traceable, reproducible, and auditable.

---

## Example Governance Scenario

The clearest demo system is:

```text
AI-005 — Autonomous Termination Recommender
```

This system is blocked because it represents a prohibited or unacceptable AI use case involving employment decisioning and insufficient human review.

The platform shows:

* Risk tier: `BLOCKED`
* Policy decision: `BLOCKED`
* Required review status: `BLOCKED_REVIEW_REQUIRED`
* Documentation completion: `0 / 12`
* Reassessment cadence: `7 days`
* External incident evidence mapping: employment automation risk

This demonstrates how the platform connects system metadata, data governance, policy logic, review obligations, and audit evidence into one governance record.

---

## Why This Architecture Matters

This project is not just a dashboard.

It demonstrates a practical AI governance operating model:

1. Inventory AI systems.
2. Understand their data and exposure.
3. Score governance risk.
4. Apply policy-as-code.
5. Identify missing controls and documents.
6. Schedule review and reassessment.
7. Produce audit evidence.
8. Present the result in a command center.

This architecture is relevant to work in:

* AI governance
* Data governance
* Responsible AI
* Model risk management
* AI product operations
* Data quality
* Analytics engineering
* Governance automation

---

## Future Architecture Extensions

Potential extensions include:

* Authentication and role-based access
* Workflow approvals
* Policy versioning
* Evidence versioning
* Audit event logging for every pipeline run
* Direct integration with data catalogs
* Direct integration with model registries
* Jira or ServiceNow workflow integration
* Cloud deployment
* Containerized local development
* More complete policy test coverage

These extensions would move the project closer to an enterprise-grade AI governance control plane.
