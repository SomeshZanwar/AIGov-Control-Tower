# AIGov Control Tower

**AI Use Case Registry, Risk Triage, Policy Controls, and Audit Evidence Platform**

AIGov Control Tower is a full-stack AI governance platform that helps teams inventory AI systems, classify risk, evaluate policy controls, track documentation readiness, schedule human review, map external incident evidence, and generate audit-ready governance reports.

The project is designed to answer one practical governance question:

> Can this AI system be approved, monitored, and defended with evidence?

---

## Why This Project Exists

Organizations are adopting AI systems faster than their governance processes can keep up.

Most teams need a way to track:

* Which AI systems exist
* What business function they support
* What data they use
* Whether they are customer-facing or employee-facing
* Whether they rely on third-party vendors
* Whether human review is required
* Which policies are triggered
* Which documents are missing
* When the next reassessment is due
* What evidence supports the approval or blocking decision

AIGov Control Tower turns that governance workflow into a working full-stack system.

---

## Core Idea

AIGov Control Tower works like an AI governance control plane.

```text
AI use case intake
        ↓
AI system inventory
        ↓
Data source and incident evidence mapping
        ↓
Risk scoring
        ↓
YAML policy evaluation
        ↓
Documentation completeness checks
        ↓
Human review and reassessment scheduling
        ↓
Audit-ready report generation
        ↓
React governance command center
```

---

## Full-Stack Architecture

```text
PostgreSQL database
        ↓
Python governance pipeline
        ↓
FastAPI read-only API
        ↓
React + Vite governance command center
```

### Backend

The backend is responsible for governance logic and evidence generation.

It includes:

* PostgreSQL schema
* AI system inventory loader
* AI incident evidence loader
* Risk scoring engine
* YAML policy engine
* Documentation completeness checker
* Human review scheduler
* Reassessment scheduler
* Audit report generator
* CLI pipeline runner
* FastAPI API layer

### Frontend

The frontend is a React governance command center.

It includes:

* AI system registry rail
* Governance command metrics
* Risk heat strip
* Action queue
* System dossier
* Policy decision memo
* Evidence trail
* Documentation gap board
* Data source readiness view
* External incident evidence view
* Audit report preview

---

## Technology Stack

| Layer            | Technology             |
| ---------------- | ---------------------- |
| Database         | PostgreSQL             |
| Backend Pipeline | Python                 |
| API              | FastAPI                |
| ORM / SQL        | SQLAlchemy             |
| CLI              | Typer + Rich           |
| Policy Format    | YAML                   |
| Frontend         | React + Vite           |
| Styling          | Custom CSS             |
| Data Handling    | pandas                 |
| Reports          | Markdown audit reports |

---

## Key Features

### 1. AI System Inventory

Tracks AI systems with governance-relevant metadata:

* System name and business use case
* Business, technical, and governance owners
* Department
* Model provider and model name
* Deployment stage
* Decision impact
* Autonomy level
* Customer-facing / employee-facing exposure
* Personal, sensitive, financial, and health data usage
* Human review requirements
* Third-party vendor dependency
* Approval status

---

### 2. Data Source Governance

Tracks data sources used by each AI system:

* Source name
* Source type
* Source system
* Data owner
* Business domain
* PII and sensitive data flags
* Financial and health data flags
* Quality status
* Lineage availability
* AI-use approval status
* Retention policy
* Access control status

---

### 3. External AI Incident Evidence Mapping

The project maps AI systems to external AI incident risk patterns.

This helps explain why a system requires controls by connecting internal governance signals to broader real-world AI risk categories.

Example mappings include:

* Employment bias risk
* Customer-facing AI output risk
* Financial decisioning risk
* Sensitive data exposure risk
* Third-party AI data leakage risk

---

### 4. AI Risk Scoring Engine

The risk engine calculates system-level AI governance risk using:

* Business impact
* Data sensitivity
* Autonomy level
* User exposure
* Vendor dependency
* Documentation readiness
* Prohibited use-case status

Example output:

| System                                    | Risk Score | Risk Tier |
| ----------------------------------------- | ---------: | --------- |
| AI-001 Internal Policy Assistant          |       1.17 | LOW       |
| AI-002 Customer Support GenAI Assistant   |       3.00 | MODERATE  |
| AI-003 Resume Screening Ranker            |       2.67 | MODERATE  |
| AI-004 Loan Default Risk Model            |       2.50 | MODERATE  |
| AI-005 Autonomous Termination Recommender |       3.33 | BLOCKED   |
| AI-006 Marketing Content Generator        |       1.83 | LOW       |

---

### 5. YAML Policy Engine

Governance policies are defined in YAML and evaluated against system risk context.

Example policy categories:

* Prohibited use
* Human review
* Data governance
* Customer-facing AI controls
* Vendor risk
* Risk management

Example decisions:

```text
APPROVED
APPROVED_WITH_CONTROLS
REQUIRES_REVIEW
BLOCKED
```

The blocked demo system is:

```text
AI-005 — Autonomous Termination Recommender
```

It is blocked because it represents a prohibited/high-risk employment decisioning scenario without meaningful human review.

---

### 6. Documentation Completeness Checker

The system calculates required governance documents based on risk and system context.

Required documents may include:

* Business Case
* AI Risk Assessment
* Data Source Inventory
* Monitoring Plan
* Incident Response Plan
* Privacy Review
* Data Protection Impact Assessment
* Vendor Risk Review
* Human Review Workflow
* Escalation Procedure
* Model Card
* Bias and Fairness Assessment
* Governance Committee Approval

Example output:

| System | Completed | Required | Completion Rate |
| ------ | --------: | -------: | --------------: |
| AI-001 |         9 |        9 |            100% |
| AI-002 |         2 |       13 |             15% |
| AI-003 |         2 |        9 |             22% |
| AI-004 |         9 |        9 |            100% |
| AI-005 |         0 |       12 |              0% |
| AI-006 |         0 |        9 |              0% |

---

### 7. Human Review and Reassessment Scheduler

The platform generates:

* Human review workflows
* Review owners
* Required review reasons
* Review due dates
* Reassessment frequency
* Next reassessment due dates

Example reassessment cadence:

| Risk Tier | Reassessment Frequency |
| --------- | ---------------------: |
| BLOCKED   |                 7 days |
| HIGH      |                30 days |
| MODERATE  |                90 days |
| LOW       |               180 days |

---

### 8. Audit Report Generator

The report generator creates Markdown governance reports for each AI system.

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
* Mapped external incident evidence
* Audit conclusion

Generated reports are written to:

```text
docs/audit_reports/
```

This folder is ignored by Git because reports are reproducible from the database.

---

## React Governance Command Center

The React frontend presents the project as a product-style AI governance control tower instead of a basic dashboard.

Main views include:

```text
- AI registry rail
- Governance action queue
- Risk heat strip
- System-level governance dossier
- Policy decision memo
- Evidence trail
- Documentation gap board
- Data source readiness table
- External incident evidence table
- Audit report preview
```

The frontend calls the FastAPI backend at:

```text
http://localhost:8000
```

The React app runs at:

```text
http://localhost:5173
```

---

## Project Structure

```text
aigov-control-tower/
│
├── data/
│   └── sample/
│       ├── ai_risk_evidence.csv
│       ├── ai_system_inventory.csv
│       ├── ai_data_sources.csv
│       └── ai_risk_evidence_mappings.csv
│
├── docs/
│   └── fullstack_runbook.md
│
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── App.css
│   │   ├── index.css
│   │   └── main.jsx
│   ├── package.json
│   └── vite.config.js
│
├── policies/
│   └── ai_governance_policies.yml
│
├── scripts/
│   ├── aigov.py
│   ├── setup_database.py
│   ├── load_incidents.py
│   ├── load_inventory.py
│   ├── score_risk.py
│   ├── evaluate_policies.py
│   ├── check_documents.py
│   ├── schedule_reviews.py
│   └── generate_audit_reports.py
│
├── sql/
│   └── 001_create_full_schema.sql
│
├── src/
│   └── aigov/
│       ├── api/
│       │   └── main.py
│       ├── evidence/
│       │   ├── document_checker.py
│       │   └── review_scheduler.py
│       ├── ingestion/
│       │   ├── load_incidents.py
│       │   └── load_inventory.py
│       ├── policy/
│       │   └── evaluator.py
│       ├── reports/
│       │   └── audit_report.py
│       ├── risk/
│       │   └── scorer.py
│       ├── cli.py
│       ├── config.py
│       └── database.py
│
├── .env.example
├── requirements.txt
├── app.py
└── README.md
```

---

## Quickstart

### 1. Clone the repository

```cmd
git clone https://github.com/SomeshZanwar/AIGov-Control-Tower.git
cd AIGov-Control-Tower
```

### 2. Create Python virtual environment

```cmd
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Configure environment variables

```cmd
copy .env.example .env
```

Update `.env`:

```env
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=aigov_control_tower
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password_here
```

### 4. Create PostgreSQL database

```sql
CREATE DATABASE aigov_control_tower;
```

### 5. Run the full governance pipeline

```cmd
python scripts\aigov.py run-pipeline --setup-database
```

Expected summary:

```text
Incident evidence: 4
AI systems: 6
Data sources: 7
Risk evidence mappings: 6
Risk assessments: 6
Policy decisions: 8
Required documents: 61
Human review workflows: 4
Reassessment schedules: 6
Audit reports: 6
```

---

## Run the Full-Stack App

Use two terminals.

### Terminal 1 — FastAPI Backend

From the project root:

```cmd
.venv\Scripts\activate
uvicorn src.aigov.api.main:app --reload --host 0.0.0.0 --port 8000
```

Verify:

```text
http://localhost:8000/health
http://localhost:8000/docs
```

### Terminal 2 — React Frontend

From the project root:

```cmd
cd frontend
npm install
npm run dev
```

Open:

```text
http://localhost:5173
```

---

## CLI Commands

Run the full pipeline:

```cmd
python scripts\aigov.py run-pipeline
```

Apply database schema:

```cmd
python scripts\aigov.py setup-db
```

Load incident evidence:

```cmd
python scripts\aigov.py load-incidents
```

Load AI inventory:

```cmd
python scripts\aigov.py load-inventory
```

Run risk scoring:

```cmd
python scripts\aigov.py score-risk
```

Evaluate policies:

```cmd
python scripts\aigov.py evaluate-policies
```

Check documents:

```cmd
python scripts\aigov.py check-documents
```

Schedule reviews:

```cmd
python scripts\aigov.py schedule-reviews
```

Generate audit reports:

```cmd
python scripts\aigov.py generate-reports
```

---

## API Endpoints

FastAPI exposes the governance evidence through read-only endpoints.

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

Interactive API docs:

```text
http://localhost:8000/docs
```

Example:

```text
http://localhost:8000/api/systems/AI-005
```

---

## Demo AI Systems

| System Key | System Name                        | Governance Posture                          |
| ---------- | ---------------------------------- | ------------------------------------------- |
| AI-001     | Internal Policy Assistant          | Low-risk approved internal assistant        |
| AI-002     | Customer Support GenAI Assistant   | Customer-facing system requiring review     |
| AI-003     | Resume Screening Ranker            | High-impact employment AI requiring review  |
| AI-004     | Loan Default Risk Model            | Financial model approved with controls      |
| AI-005     | Autonomous Termination Recommender | Blocked prohibited use case                 |
| AI-006     | Marketing Content Generator        | Third-party AI tool requiring vendor review |

---

## Example Blocked System

```text
AI-005 — Autonomous Termination Recommender
```

Governance findings:

```text
Risk Tier: BLOCKED
Policy Decision: BLOCKED
Documentation Completion: 0 / 12
Review Status: BLOCKED_REVIEW_REQUIRED
Reassessment Frequency: 7 days
Mapped Evidence: Employment automation risk pattern
```

Audit conclusion:

> This AI system should remain blocked until a formal governance review determines whether the use case can be redesigned or retired.

---

## What This Demonstrates

This project demonstrates practical ability across:

* AI governance
* Data governance
* Risk scoring
* Policy-as-code
* Audit evidence generation
* Documentation readiness
* Human-in-the-loop governance
* Reassessment scheduling
* Full-stack application design
* FastAPI backend development
* React frontend development
* PostgreSQL data modeling

It is designed as a portfolio project for roles involving:

```text
AI Governance
Data Governance
Responsible AI
AI Risk Management
Data Quality
Model Risk Management
Analytics Engineering
AI Product Operations
```

---

## Notes

The project uses sample AI systems and sample incident evidence mappings for demonstration purposes.

External incident evidence is used as governance risk context. It should not be interpreted as an internal incident record for the demo AI systems.

Generated audit reports are reproducible and ignored by Git:

```text
docs/audit_reports/
```

To regenerate reports:

```cmd
python scripts\aigov.py generate-reports
```

---

## Full Runbook

For detailed setup and troubleshooting, see:

```text
docs/fullstack_runbook.md
```
