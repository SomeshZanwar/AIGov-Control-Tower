import { useEffect, useMemo, useState } from "react";
import "./App.css";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

async function fetchJson(path) {
  const response = await fetch(`${API_BASE_URL}${path}`);

  if (!response.ok) {
    throw new Error(`API request failed: ${path} (${response.status})`);
  }

  return response.json();
}

function formatPercent(value) {
  const numberValue = Number(value || 0);
  return `${Math.round(numberValue * 100)}%`;
}

function riskClass(tier) {
  return `risk-${String(tier || "unknown").toLowerCase()}`;
}

function decisionClass(decision) {
  return `decision-${String(decision || "unknown").toLowerCase()}`;
}

function MetricCard({ label, value, detail }) {
  return (
    <div className="metric-card">
      <div className="metric-label">{label}</div>
      <div className="metric-value">{value}</div>
      <div className="metric-detail">{detail}</div>
    </div>
  );
}

function StatusPill({ label, className = "" }) {
  return <span className={`status-pill ${className}`}>{label}</span>;
}

function LoadingState() {
  return (
    <div className="loading-shell">
      <div className="loading-orb" />
      <div>
        <h2>Loading AIGov Control Tower</h2>
        <p>Connecting to governance evidence API...</p>
      </div>
    </div>
  );
}

function ErrorState({ error }) {
  return (
    <div className="error-state">
      <h2>Control Tower API unavailable</h2>
      <p>{error}</p>
      <code>uvicorn src.aigov.api.main:app --reload --port 8000</code>
    </div>
  );
}

function SystemRail({ systems, selectedKey, onSelect }) {
  return (
    <aside className="system-rail">
      <div className="rail-header">
        <div className="eyebrow">AI Registry</div>
        <h3>Systems under governance</h3>
      </div>

      <div className="system-list">
        {systems.map((system) => (
          <button
            key={system.system_key}
            className={`system-item ${selectedKey === system.system_key ? "active" : ""}`}
            onClick={() => onSelect(system.system_key)}
          >
            <div className="system-item-top">
              <span className="system-key">{system.system_key}</span>
              <StatusPill label={system.risk_tier} className={riskClass(system.risk_tier)} />
            </div>
            <div className="system-name">{system.system_name}</div>
            <div className="system-meta">
              {system.department} · {system.approval_status}
            </div>
          </button>
        ))}
      </div>
    </aside>
  );
}

function GovernanceActionQueue({ reviewQueue }) {
  if (!reviewQueue.length) {
    return (
      <section className="panel">
        <div className="section-heading">
          <span className="eyebrow">Action Queue</span>
          <h2>No active governance review items</h2>
        </div>
      </section>
    );
  }

  return (
    <section className="panel">
      <div className="section-heading">
        <span className="eyebrow">Action Queue</span>
        <h2>Governance work requiring attention</h2>
      </div>

      <div className="action-list">
        {reviewQueue.map((item) => (
          <div key={item.system_key} className="action-card">
            <div className="action-card-main">
              <div className="action-topline">
                <StatusPill label={item.review_status} className="decision-requires_review" />
                <StatusPill label={item.risk_tier} className={riskClass(item.risk_tier)} />
              </div>
              <h3>
                {item.system_key} · {item.system_name}
              </h3>
              <p>{item.required_reason}</p>
            </div>
            <div className="action-card-side">
              <div className="side-label">Owner</div>
              <div className="side-value">{item.review_owner || "Unassigned"}</div>
              <div className="side-label">Due</div>
              <div className="side-value">{item.due_date}</div>
            </div>
          </div>
        ))}
      </div>
    </section>
  );
}

function RiskHeatStrip({ systems, selectedKey, onSelect }) {
  return (
    <section className="heat-strip">
      {systems.map((system) => (
        <button
          key={system.system_key}
          className={`heat-cell ${riskClass(system.risk_tier)} ${
            selectedKey === system.system_key ? "active" : ""
          }`}
          onClick={() => onSelect(system.system_key)}
        >
          <span>{system.risk_tier}</span>
          <strong>{system.system_key}</strong>
        </button>
      ))}
    </section>
  );
}

function DossierHeader({ system }) {
  return (
    <section className="dossier-hero">
      <div>
        <div className="dossier-pills">
          <StatusPill label={system.risk_tier || "UNKNOWN"} className={riskClass(system.risk_tier)} />
          <StatusPill label={system.approval_status || "UNKNOWN"} className="approval-pill" />
          {system.prohibited_use_case && (
            <StatusPill label="PROHIBITED USE CASE" className="risk-blocked" />
          )}
        </div>
        <h1>{system.system_name}</h1>
        <p>{system.use_case}</p>
      </div>

      <div className="dossier-score">
        <span>Risk score</span>
        <strong>{system.risk_score ?? "N/A"}</strong>
      </div>
    </section>
  );
}

function EvidenceTrail({ system, policies, dataSources, incidents }) {
  const primaryPolicy = policies[0];

  return (
    <section className="panel evidence-trail">
      <div className="section-heading">
        <span className="eyebrow">Evidence Trail</span>
        <h2>Why the system received this governance posture</h2>
      </div>

      <div className="trail-grid">
        <div className="trail-step">
          <span>01</span>
          <h4>Inventory signal</h4>
          <p>
            {system.decision_impact} impact · {system.autonomy_level} autonomy ·{" "}
            {system.deployment_stage} stage
          </p>
        </div>

        <div className="trail-step">
          <span>02</span>
          <h4>Data signal</h4>
          <p>
            {dataSources.length} source(s),{" "}
            {dataSources.filter((source) => source.approved_for_ai_use === false).length} requiring
            AI-use approval
          </p>
        </div>

        <div className="trail-step">
          <span>03</span>
          <h4>Policy signal</h4>
          <p>
            {primaryPolicy
              ? `${primaryPolicy.decision}: ${primaryPolicy.policy_name}`
              : "No active policy findings"}
          </p>
        </div>

        <div className="trail-step">
          <span>04</span>
          <h4>External risk evidence</h4>
          <p>
            {incidents.length
              ? `${incidents.length} mapped incident evidence pattern(s)`
              : "No mapped external incident evidence"}
          </p>
        </div>
      </div>
    </section>
  );
}

function PolicyDecisionMemo({ system, policies }) {
  const strongest = policies.find((policy) => policy.decision === "BLOCKED") || policies[0];

  return (
    <section className="panel memo-panel">
      <div className="section-heading">
        <span className="eyebrow">Decision Memo</span>
        <h2>Governance recommendation</h2>
      </div>

      {strongest ? (
        <div className="memo-body">
          <div className="memo-decision-row">
            <span>Recommended decision</span>
            <StatusPill label={strongest.decision} className={decisionClass(strongest.decision)} />
          </div>

          <h3>{strongest.policy_name}</h3>
          <p>{strongest.reason}</p>

          <div className="control-box">
            <span>Required control</span>
            <strong>{strongest.control_required || "No additional control recorded."}</strong>
          </div>
        </div>
      ) : (
        <div className="memo-body">
          <div className="memo-decision-row">
            <span>Recommended decision</span>
            <StatusPill label="NO FINDINGS" className="risk-low" />
          </div>
          <h3>No blocking policy findings</h3>
          <p>
            {system.system_name} currently has no active policy findings based on available
            governance evidence.
          </p>
        </div>
      )}
    </section>
  );
}

function DataTable({ rows, columns, emptyText }) {
  if (!rows.length) {
    return <div className="empty-table">{emptyText}</div>;
  }

  return (
    <div className="table-wrap">
      <table>
        <thead>
          <tr>
            {columns.map((column) => (
              <th key={column.key}>{column.label}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((row, index) => (
            <tr key={index}>
              {columns.map((column) => (
                <td key={column.key}>{String(row[column.key] ?? "N/A")}</td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function SystemDossier({
  system,
  policies,
  dataSources,
  documents,
  incidents,
  auditReport,
}) {
  const missingDocuments = documents.filter((document) => !document.completed);

  return (
    <main className="dossier">
      <DossierHeader system={system} />

      <div className="dossier-metrics">
        <MetricCard label="Policy findings" value={policies.length} detail="Triggered control checks" />
        <MetricCard
          label="Evidence readiness"
          value={formatPercent(system.completion_rate)}
          detail={`${system.completed_documents || 0}/${system.required_documents || 0} documents complete`}
        />
        <MetricCard
          label="Human review"
          value={system.human_review_status || "NOT_REQUIRED"}
          detail={system.review_owner || "No owner assigned"}
        />
        <MetricCard
          label="Next reassessment"
          value={system.next_review_due_date || "N/A"}
          detail={`${system.review_frequency_days || "N/A"} day cadence`}
        />
      </div>

      <EvidenceTrail
        system={system}
        policies={policies}
        dataSources={dataSources}
        incidents={incidents}
      />

      <div className="two-column">
        <PolicyDecisionMemo system={system} policies={policies} />

        <section className="panel">
          <div className="section-heading">
            <span className="eyebrow">Documentation Gaps</span>
            <h2>Evidence still required</h2>
          </div>

          {missingDocuments.length ? (
            <div className="gap-list">
              {missingDocuments.slice(0, 8).map((document) => (
                <div key={document.document_name} className="gap-item">
                  <strong>{document.document_name}</strong>
                  <span>{document.document_category}</span>
                  <small>
                    Owner: {document.owner || "Unassigned"} · Due: {document.due_date || "N/A"}
                  </small>
                </div>
              ))}
            </div>
          ) : (
            <div className="empty-table">All required documents are complete.</div>
          )}
        </section>
      </div>

      <section className="panel">
        <div className="section-heading">
          <span className="eyebrow">Data Sources</span>
          <h2>Data readiness and access controls</h2>
        </div>

        <DataTable
          rows={dataSources}
          emptyText="No data sources documented."
          columns={[
            { key: "source_name", label: "Source" },
            { key: "source_type", label: "Type" },
            { key: "data_owner", label: "Owner" },
            { key: "quality_status", label: "Quality" },
            { key: "approved_for_ai_use", label: "Approved for AI" },
            { key: "access_control_status", label: "Access" },
          ]}
        />
      </section>

      <section className="panel">
        <div className="section-heading">
          <span className="eyebrow">External Risk Evidence</span>
          <h2>Mapped incident patterns</h2>
        </div>

        <DataTable
          rows={incidents}
          emptyText="No incident evidence mapped."
          columns={[
            { key: "external_incident_id", label: "Incident ID" },
            { key: "harm_category", label: "Harm" },
            { key: "severity", label: "Severity" },
            { key: "mapped_risk_category", label: "Mapped Risk" },
            { key: "mapped_control", label: "Mapped Control" },
          ]}
        />
      </section>

      <section className="panel audit-preview">
        <div className="section-heading">
          <span className="eyebrow">Audit Dossier</span>
          <h2>Generated governance report</h2>
        </div>

        <pre>{auditReport?.report_text || "Audit report not generated yet."}</pre>
      </section>
    </main>
  );
}

function App() {
  const [summary, setSummary] = useState(null);
  const [systems, setSystems] = useState([]);
  const [reviewQueue, setReviewQueue] = useState([]);
  const [selectedKey, setSelectedKey] = useState(null);
  const [selectedSystem, setSelectedSystem] = useState(null);
  const [policies, setPolicies] = useState([]);
  const [dataSources, setDataSources] = useState([]);
  const [documents, setDocuments] = useState([]);
  const [incidents, setIncidents] = useState([]);
  const [auditReport, setAuditReport] = useState(null);
  const [loading, setLoading] = useState(true);
  const [detailLoading, setDetailLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    async function loadInitialData() {
      try {
        const [summaryData, systemsData, reviewQueueData] = await Promise.all([
          fetchJson("/api/summary"),
          fetchJson("/api/systems"),
          fetchJson("/api/review-queue"),
        ]);

        setSummary(summaryData);
        setSystems(systemsData);
        setReviewQueue(reviewQueueData);

        if (systemsData.length) {
          setSelectedKey(systemsData[0].system_key);
        }
      } catch (requestError) {
        setError(requestError.message);
      } finally {
        setLoading(false);
      }
    }

    loadInitialData();
  }, []);

  useEffect(() => {
    if (!selectedKey) return;

    async function loadSystemDetail() {
      setDetailLoading(true);

      try {
        const [
          systemData,
          policyData,
          dataSourceData,
          documentData,
          incidentData,
          auditData,
        ] = await Promise.all([
          fetchJson(`/api/systems/${selectedKey}`),
          fetchJson(`/api/systems/${selectedKey}/policy-decisions`),
          fetchJson(`/api/systems/${selectedKey}/data-sources`),
          fetchJson(`/api/systems/${selectedKey}/documents`),
          fetchJson(`/api/systems/${selectedKey}/incident-evidence`),
          fetchJson(`/api/systems/${selectedKey}/audit-report`).catch(() => null),
        ]);

        const overviewSystem =
          systems.find((system) => system.system_key === selectedKey) || {};

        setSelectedSystem({ ...overviewSystem, ...systemData });
        setPolicies(policyData);
        setDataSources(dataSourceData);
        setDocuments(documentData);
        setIncidents(incidentData);
        setAuditReport(auditData);
      } catch (requestError) {
        setError(requestError.message);
      } finally {
        setDetailLoading(false);
      }
    }

    loadSystemDetail();
  }, [selectedKey, systems]);

  const reviewRequired = useMemo(() => {
    return systems.filter(
      (system) =>
        system.policy_findings > 0 ||
        system.approval_status === "REQUIRES_REVIEW" ||
        system.risk_tier === "BLOCKED"
    ).length;
  }, [systems]);

  if (loading) return <LoadingState />;
  if (error) return <ErrorState error={error} />;

  return (
    <div className="app-shell">
      <SystemRail systems={systems} selectedKey={selectedKey} onSelect={setSelectedKey} />

      <div className="workspace">
        <header className="topbar">
          <div>
            <div className="eyebrow">AI Governance Command Center</div>
            <h1>AIGov Control Tower</h1>
            <p>
              Registry, risk triage, policy controls, evidence readiness, human review,
              reassessment scheduling, and audit dossier generation.
            </p>
          </div>

          <div className="api-badge">
            <span className="pulse" />
            FastAPI connected
          </div>
        </header>

        <section className="command-metrics">
          <MetricCard
            label="Registered AI systems"
            value={summary.total_systems}
            detail="Systems in governed inventory"
          />
          <MetricCard
            label="Blocked systems"
            value={summary.blocked_systems}
            detail="Systems requiring stop or redesign"
          />
          <MetricCard
            label="Governance actions"
            value={reviewRequired}
            detail="Review, blocked, or policy findings"
          />
          <MetricCard
            label="Audit evidence"
            value={`${summary.completed_documents}/${summary.required_documents}`}
            detail="Completed required documents"
          />
        </section>

        <RiskHeatStrip systems={systems} selectedKey={selectedKey} onSelect={setSelectedKey} />

        <GovernanceActionQueue reviewQueue={reviewQueue} />

        {detailLoading && <div className="inline-loader">Loading system dossier...</div>}

        {selectedSystem && !detailLoading && (
          <SystemDossier
            system={selectedSystem}
            policies={policies}
            dataSources={dataSources}
            documents={documents}
            incidents={incidents}
            auditReport={auditReport}
          />
        )}
      </div>
    </div>
  );
}

export default App;