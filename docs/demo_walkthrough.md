# AIGov Control Tower — Demo Walkthrough

This walkthrough explains how to present AIGov Control Tower as a full-stack AI governance portfolio project.

The strongest demo scenario is:

```text id="xza7st"
AI-005 — Autonomous Termination Recommender
```

This system shows the complete governance workflow because it is blocked by policy, has missing documentation, requires human review, and is mapped to external incident evidence.

---

## 1. One-Minute Project Explanation

AIGov Control Tower is a full-stack AI governance platform for tracking AI systems, scoring risk, evaluating governance policies, checking documentation readiness, scheduling human review, and generating audit-ready evidence.

The project connects four layers:

```text id="wvvuyr"
PostgreSQL database
Python governance pipeline
FastAPI backend
React command center
```

The key idea is simple:

> AI governance should not be a spreadsheet or a static dashboard. It should be a repeatable evidence pipeline that can explain why an AI system is approved, requires review, or must be blocked.

---

## 2. Demo Setup

Start the backend:

```cmd id="smqsmf"
uvicorn src.aigov.api.main:app --reload --host 0.0.0.0 --port 8000
```

Start the frontend:

```cmd id="3t5i0i"
cd frontend
npm run dev
```

Open:

```text id="m6y5wl"
http://localhost:5173
```

---

## 3. Start with the Command Center

Show the top-level command center first.

Point out:

* Total AI systems
* Blocked systems
* Policy findings
* Required documents
* Governance action queue
* Risk heat strip

Explain:

> The command center gives a governance team a live view of which AI systems need attention. It is not just showing application metrics; it is showing governance posture.

---

## 4. Select the Blocked System

Select:

```text id="qpzdh9"
AI-005 — Autonomous Termination Recommender
```

Explain:

> This is the main demo case. It represents an AI system that makes or recommends employment termination decisions without sufficient human review. The platform blocks it because it triggers prohibited-use and high-impact AI governance policies.

---

## 5. Explain the System Dossier

In the system dossier, highlight:

```text id="j0s7r6"
Risk Tier: BLOCKED
Decision Impact: HIGH
Autonomy Level: HIGH
Human Review: missing or insufficient
Documentation Completion: 0 / 12
```

Explain:

> The dossier pulls together system metadata, risk classification, documentation readiness, and governance status into one reviewable record.

---

## 6. Explain Policy Decisions

Show the policy decision memo.

For AI-005, the important policy decisions are:

```text id="7e6aej"
BLOCKED — prohibited_use_case_blocked
REQUIRES_REVIEW — missing_human_review_for_high_impact_ai
REQUIRES_REVIEW — sensitive_data_without_approved_source_review
```

Explain:

> The policy layer is YAML-based, so the governance logic is not hidden in the frontend. Policies can be reviewed, changed, and rerun through the backend pipeline.

---

## 7. Explain Documentation Gaps

Show the documentation gap board.

For AI-005:

```text id="gfby9u"
0 of 12 required documents are complete
```

Explain:

> This is where the project connects policy decisions to operational readiness. A system should not move forward if required documents, review plans, and governance approvals are missing.

---

## 8. Explain External Incident Evidence

Show the evidence mapping section.

Explain:

> The project maps internal AI systems to external AI incident risk patterns. This helps justify why controls are required and connects governance decisions to real-world AI failure modes.

For AI-005, the mapped risk pattern is employment automation risk.

---

## 9. Explain the Audit Report Preview

Show the audit report preview.

Explain:

> The audit report is generated from database evidence. It summarizes the system, risk tier, data context, policy findings, documentation gaps, human review status, reassessment status, and governance conclusion.

For AI-005, the conclusion is:

> This AI system should remain blocked until formal governance review determines whether the use case can be redesigned or retired.

---

## 10. Technical Architecture Explanation

Explain the architecture in this order:

```text id="9iua5z"
1. PostgreSQL stores governance evidence.
2. Python pipeline loads inventory, scores risk, evaluates policies, checks documentation, schedules reviews, and generates audit reports.
3. FastAPI exposes the evidence through read-only API endpoints.
4. React displays the governance state as a command center.
5. GitHub Actions verifies backend imports and frontend build.
```

---

## 11. Why This Is Different from a Dashboard

Use this explanation:

> A normal dashboard only visualizes data. This project creates governance evidence first, then visualizes it. The value is in the pipeline: inventory, risk scoring, policy evaluation, documentation checks, human review scheduling, reassessment, and audit reporting.

---

## 12. Interview Talking Points

Use these points in interviews:

```text id="1f4pld"
- I built this to understand how AI governance can work as an operating system, not just a policy document.
- The project uses policy-as-code to evaluate AI systems consistently.
- It connects data governance, risk management, documentation readiness, and audit evidence.
- The frontend is intentionally read-only so governance state remains traceable to backend logic.
- The blocked system demo shows how the platform handles a high-risk AI use case.
- The system is full-stack: PostgreSQL, Python, FastAPI, React, and GitHub Actions CI.
```

---

## 13. Short Recruiter Version

Use this when explaining quickly:

> I built AIGov Control Tower, a full-stack AI governance platform that inventories AI systems, scores their risk, evaluates YAML governance policies, checks documentation gaps, schedules reviews, and generates audit-ready reports. It uses PostgreSQL, Python, FastAPI, and React, with CI through GitHub Actions. The main demo shows how a high-risk employment AI system is blocked and documented through a repeatable governance workflow.

---

## 14. Strongest Demo Flow

The best order for a live demo is:

```text id="ldqcw8"
1. Show GitHub README and screenshots.
2. Start the React app.
3. Show the command center summary.
4. Select AI-005.
5. Explain why it is blocked.
6. Show policy decisions.
7. Show missing documents.
8. Show external incident evidence.
9. Show audit report preview.
10. Mention the backend pipeline and CI.
```

---

## 15. Closing Explanation

End the demo with:

> The project is meant to show how governance can become a repeatable system. Instead of manually arguing whether an AI use case is safe, the platform creates a structured evidence trail that explains the risk, triggered policies, missing controls, review obligations, and audit conclusion.
