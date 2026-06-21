# AIGov Control Tower — Full-Stack Runbook

This runbook explains how to run the full AIGov Control Tower locally, including the PostgreSQL database, Python governance pipeline, FastAPI backend, and React command center frontend.

## System Architecture

AIGov Control Tower has four main layers:

```text
PostgreSQL database
        ↓
Python governance pipeline
        ↓
FastAPI read-only API
        ↓
React governance command center
```

The backend pipeline creates and updates governance evidence. The FastAPI layer exposes that evidence through API endpoints. The React frontend displays the AI governance control tower interface.

## Prerequisites

Install the following before running the project:

```text
Python 3.12+
PostgreSQL
Node.js 20.19+ or newer
npm
Git
```

The project has been tested locally with:

```text
Python 3.12.4
PostgreSQL 18.3
Node.js 24.13.0
npm 11.13.0
```

## 1. Clone the Repository

```cmd
git clone https://github.com/SomeshZanwar/AIGov-Control-Tower.git
cd AIGov-Control-Tower
```

## 2. Create and Activate Python Virtual Environment

```cmd
python -m venv .venv
.venv\Scripts\activate
```

Install Python dependencies:

```cmd
pip install -r requirements.txt
```

## 3. Configure Environment Variables

Copy the example environment file:

```cmd
copy .env.example .env
```

Update `.env` with your local PostgreSQL credentials:

```env
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=aigov_control_tower
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password_here
```

Do not commit `.env`.

## 4. Create PostgreSQL Database

Open PostgreSQL or psql and create the database:

```sql
CREATE DATABASE aigov_control_tower;
```

## 5. Run the Governance Pipeline

From the project root, run:

```cmd
python scripts\aigov.py run-pipeline --setup-database
```

This command applies the schema and runs the full governance pipeline:

```text
1. Load AI incident evidence
2. Load AI system inventory
3. Load data sources
4. Load incident evidence mappings
5. Score AI system risk
6. Evaluate YAML governance policies
7. Check documentation completeness
8. Schedule human review workflows
9. Schedule reassessment cadences
10. Generate audit reports
```

Expected output includes:

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

For normal reruns after setup, use:

```cmd
python scripts\aigov.py run-pipeline
```

## 6. Start FastAPI Backend

Open a terminal from the project root and activate the virtual environment:

```cmd
.venv\Scripts\activate
```

Start the API server:

```cmd
uvicorn src.aigov.api.main:app --reload --host 0.0.0.0 --port 8000
```

The API should run at:

```text
http://localhost:8000
```

Verify the backend:

```text
http://localhost:8000/health
http://localhost:8000/api/summary
http://localhost:8000/api/systems
http://localhost:8000/api/systems/AI-005
http://localhost:8000/docs
```

The `/docs` endpoint opens the interactive FastAPI Swagger interface.

## 7. Start React Frontend

Open a second terminal from the project root.

Go into the frontend folder:

```cmd
cd frontend
```

Install frontend dependencies:

```cmd
npm install
```

Start the React development server:

```cmd
npm run dev
```

Open the app:

```text
http://localhost:5173
```

The frontend expects the FastAPI backend to be running at:

```text
http://localhost:8000
```

## 8. Expected Frontend Experience

The React command center should show:

```text
- AI system registry rail
- Governance command metrics
- Risk heat strip
- Governance action queue
- System-level dossier
- Policy decision memo
- Evidence trail
- Documentation gap board
- Data source readiness
- External incident evidence mappings
- Generated audit report preview
```

The blocked demo system is:

```text
AI-005 — Autonomous Termination Recommender
```

It should show:

```text
Risk Tier: BLOCKED
Policy Decision: BLOCKED
Reason: Prohibited use case + missing human review
Documentation Completion: 0 / 12
Mapped Risk Evidence: AIID-EXAMPLE-001
```

## 9. Useful CLI Commands

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

Check documentation completeness:

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

Run the full pipeline:

```cmd
python scripts\aigov.py run-pipeline
```

## 10. Key API Endpoints

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

Example:

```text
http://localhost:8000/api/systems/AI-005
```

## 11. Troubleshooting

### React shows “Control Tower API unavailable”

Make sure FastAPI is running:

```cmd
uvicorn src.aigov.api.main:app --reload --host 0.0.0.0 --port 8000
```

Then verify:

```text
http://localhost:8000/health
```

### API works, but React still fails

Check the browser console for failed API requests.

The React frontend uses this default API base URL:

```text
http://localhost:8000
```

### Audit report preview is empty

Regenerate audit reports:

```cmd
python scripts\aigov.py generate-reports
```

### Database connection fails

Check `.env`:

```env
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=aigov_control_tower
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password_here
```

Also confirm PostgreSQL is running and the database exists.

## 12. Development Notes

Generated audit reports are ignored by Git:

```text
docs/audit_reports/
```

The reports are reproducible from the database by running:

```cmd
python scripts\aigov.py generate-reports
```

The React frontend is intentionally read-only. Governance state is produced by the backend pipeline and exposed through FastAPI.
