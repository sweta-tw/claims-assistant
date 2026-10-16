
import { useCallback, useEffect, useMemo, useState } from "react";
import {
  Activity,
  ArrowRight,
  Bot,
  CheckCircle2,
  Clock3,
  FileSearch,
  FileText,
  LayoutDashboard,
  LogOut,
  Plus,
  RefreshCw,
  Search,
  ShieldCheck,
  Sparkles,
  Trash2,
  X,
  Eye,
} from "lucide-react";

import {
  login,
  getClaims,
  getClaim,
  createClaim,
  updateClaimStatus,
  deleteClaim,
} from "./api";

import "./App.css";
import AssistantChat from "./AssistantChat";

const navigation = [
  { label: "Overview", icon: LayoutDashboard },
  { label: "Claims", icon: FileText },
  { label: "AI Assistant", icon: Bot },
  { label: "Approvals", icon: ShieldCheck },
  { label: "Policy Search", icon: FileSearch },
];

const statusLabels = {
  SUBMITTED: "Submitted",
  UNDER_REVIEW: "Under review",
  APPROVED: "Approved",
  REJECTED: "Rejected",
  SETTLED: "Settled",
};

const allowedTransitions = {
  SUBMITTED: ["UNDER_REVIEW"],
  UNDER_REVIEW: ["APPROVED", "REJECTED"],
  APPROVED: ["SETTLED"],
  REJECTED: [],
  SETTLED: [],
};

function formatAmount(amount) {
  const value = Number(amount);
  if (!Number.isFinite(value)) return String(amount ?? "—");

  return new Intl.NumberFormat("en-IN", {
    style: "currency",
    currency: "INR",
    maximumFractionDigits: 2,
  }).format(value);
}

function StatusBadge({ status }) {
  const className = String(status || "unknown")
    .toLowerCase()
    .replaceAll("_", "-");

  return (
    <span className={`status-badge status-${className}`}>
      {statusLabels[status] || status || "Unknown"}
    </span>
  );
}

function Sidebar({ active, onNavigate, onLogout }) {
  return (
    <aside className="sidebar">
      <div className="brand">
        <div className="brand-icon">
          <ShieldCheck size={22} />
        </div>
        <div>
          <div className="brand-name">ClaimsIQ</div>
          <div className="brand-caption">INTELLIGENCE PLATFORM</div>
        </div>
      </div>

      <div className="workspace-label">WORKSPACE</div>

      <nav className="navigation">
        {navigation.map(({ label, icon: Icon }) => (
          <button
            key={label}
            className={`nav-item ${active === label ? "nav-active" : ""}`}
            onClick={() => onNavigate(label)}
          >
            <Icon size={19} />
            <span>{label}</span>
          </button>
        ))}
      </nav>

      <div className="sidebar-spacer" />

      <div className="profile">
        <div className="profile-avatar">ST</div>
        <div className="profile-info">
          <strong>Claims Administrator</strong>
          <span>Authenticated session</span>
        </div>
        <button
          className="icon-button"
          onClick={onLogout}
          aria-label="Log out"
          title="Log out"
        >
          <LogOut size={17} />
        </button>
      </div>
    </aside>
  );
}

function LoginScreen({ onLogin, loading, error }) {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");

  async function submit(event) {
    event.preventDefault();
    await onLogin(username, password);
  }

  return (
    <main className="login-screen">
      <form className="login-form" onSubmit={submit}>
        <div className="brand-icon">
          <ShieldCheck size={24} />
        </div>
        <h1>Sign in to ClaimsIQ</h1>
        <p>Sign in using your configured backend credentials.</p>

        <label>
          Username
          <input
            required
            autoComplete="username"
            value={username}
            onChange={(event) => setUsername(event.target.value)}
          />
        </label>

        <label>
          Password
          <input
            required
            type="password"
            autoComplete="current-password"
            value={password}
            onChange={(event) => setPassword(event.target.value)}
          />
        </label>

        {error && <p className="form-error" role="alert">{error}</p>}

        <button className="primary-button" type="submit" disabled={loading}>
          {loading ? "Signing in..." : "Sign in"}
        </button>
      </form>
    </main>
  );
}

function Overview({ claims, onNavigate, onRefresh, loading }) {
  const count = (status) =>
    claims.filter((claim) => claim.status === status).length;

  const metrics = [
    { label: "Total claims", value: claims.length, icon: FileText, description: "Returned by API" },
    { label: "Submitted", value: count("SUBMITTED"), icon: Clock3, description: "Awaiting review" },
    { label: "Approved", value: count("APPROVED"), icon: CheckCircle2, description: "Approved claims" },
    { label: "Needs attention", value: count("UNDER_REVIEW"), icon: ShieldCheck, description: "Under review" },
  ];

  return (
    <>
      <section className="welcome-row">
        <div>
          <div className="eyebrow">INSURANCE CLAIMS WORKSPACE</div>
          <h1>Claims overview</h1>
          <p className="page-description">
            Monitor claims retrieved from your existing backend.
          </p>
        </div>
        <button className="primary-button" onClick={() => onNavigate("AI Assistant")}>
          <Sparkles size={17} /> Ask AI Assistant
        </button>
      </section>

      <section className="metrics-grid">
        {metrics.map(({ label, value, icon: Icon, description }, index) => (
          <article className="metric-card" key={label}>
            <div className="metric-top">
              <span className="metric-label">{label}</span>
              <div className={`metric-icon tone-${["blue", "amber", "green", "purple"][index]}`}>
                <Icon size={19} />
              </div>
            </div>
            <div className="metric-value">{value}</div>
            <div className="metric-footer">
              <span className="metric-description">{description}</span>
            </div>
          </article>
        ))}
      </section>

      <section className="insight-banner">
        <div className="insight-symbol"><Activity size={22} /></div>
        <div className="insight-content">
          <div className="insight-title">Connected claims dashboard</div>
          <div className="insight-text">
            Claim counts and records are loaded from the API.
          </div>
        </div>
        <button className="insight-action" onClick={onRefresh} disabled={loading}>
          <RefreshCw size={16} /> Refresh
        </button>
      </section>

      <section className="claims-panel">
        <div className="panel-heading">
          <div>
            <h2>Claims</h2>
            <p>Manage records in the Claims section.</p>
          </div>
          <button className="secondary-button" onClick={() => onNavigate("Claims")}>
            Claims view <ArrowRight size={16} />
          </button>
        </div>
        <div className="table-bottom">
          <span>{claims.length} claim(s) loaded from API</span>
          <span className="table-page">Live API data</span>
        </div>
      </section>
    </>
  );
}

function ClaimDetails({ claim, onClose }) {
  if (!claim) return null;

  return (
    <section className="claims-panel claim-details-panel">
      <div className="panel-heading">
        <div>
          <h2>Claim details: {claim.id}</h2>
          <p>Full record retrieved using GET by claim ID.</p>
        </div>
        <button className="secondary-button" onClick={onClose}>
          <X size={15} /> Close
        </button>
      </div>

      <dl className="claim-details">
        {Object.entries(claim).map(([key, value]) => (
          <div className="claim-detail-row" key={key}>
            <dt>{key.replaceAll("_", " ")}</dt>
            <dd>
              {value !== null && typeof value === "object"
                ? JSON.stringify(value)
                : String(value ?? "—")}
            </dd>
          </div>
        ))}
      </dl>
    </section>
  );
}

function ClaimsPage({
  claims,
  token,
  loading,
  onRefresh,
  onCreated,
  onStatusUpdated,
  onDeleted,
}) {
  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState("All statuses");
  const [showForm, setShowForm] = useState(false);
  const [customer, setCustomer] = useState("");
  const [amount, setAmount] = useState("");
  const [selectedClaim, setSelectedClaim] = useState(null);
  const [detailLoading, setDetailLoading] = useState(false);
  const [busyClaimId, setBusyClaimId] = useState("");
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  const filteredClaims = useMemo(() => {
    const query = search.trim().toLowerCase();

    return claims.filter((claim) => {
      const matchesSearch =
        String(claim.id || "").toLowerCase().includes(query) ||
        String(claim.customer || "").toLowerCase().includes(query);

      const matchesStatus =
        statusFilter === "All statuses" ||
        statusLabels[claim.status] === statusFilter;

      return matchesSearch && matchesStatus;
    });
  }, [claims, search, statusFilter]);

  async function handleCreate(event) {
    event.preventDefault();
    setSaving(true);
    setError("");
    setSuccess("");

    try {
      const result = await createClaim(token, { customer, amount });
      await onCreated();
      setCustomer("");
      setAmount("");
      setShowForm(false);
      setSuccess(`Claim ${result?.id || ""} created successfully.`);
    } catch (err) {
      setError(err.message || "Unable to create claim.");
    } finally {
      setSaving(false);
    }
  }

  async function handleView(claimId) {
    setDetailLoading(true);
    setError("");
    setSelectedClaim(null);

    try {
      const data = await getClaim(token, claimId);
      setSelectedClaim(data);
    } catch (err) {
      setError(err.message || "Unable to retrieve claim details.");
    } finally {
      setDetailLoading(false);
    }
  }

  async function handleStatusChange(claimId, status) {
    if (!status) return;

    setBusyClaimId(claimId);
    setError("");
    setSuccess("");

    try {
      await updateClaimStatus(token, claimId, status);
      await onStatusUpdated();
      setSuccess(`${claimId} status updated to ${statusLabels[status]}.`);

      if (selectedClaim?.id === claimId) {
        setSelectedClaim(await getClaim(token, claimId));
      }
    } catch (err) {
      setError(err.message || "Unable to update claim status.");
    } finally {
      setBusyClaimId("");
    }
  }

  async function handleDelete(claimId) {
    if (!window.confirm(`Delete claim ${claimId}? This action may be irreversible.`)) {
      return;
    }

    setBusyClaimId(claimId);
    setError("");
    setSuccess("");

    try {
      await deleteClaim(token, claimId);
      await onDeleted();

      if (selectedClaim?.id === claimId) {
        setSelectedClaim(null);
      }

      setSuccess(`Claim ${claimId} deleted successfully.`);
    } catch (err) {
      setError(err.message || "Unable to delete claim.");
    } finally {
      setBusyClaimId("");
    }
  }

  return (
    <>
      <section className="welcome-row">
        <div>
          <div className="eyebrow">INSURANCE CLAIMS WORKSPACE</div>
          <h1>Claims management</h1>
          <p className="page-description">
            Create, inspect, update, and manage claims.
          </p>
        </div>
        <button className="primary-button" onClick={() => setShowForm((value) => !value)}>
          {showForm ? <X size={16} /> : <Plus size={16} />}
          {showForm ? "Cancel" : "Create Claim"}
        </button>
      </section>

      {error && <p className="form-error" role="alert">{error}</p>}
      {success && <p className="success-message" role="status">{success}</p>}

      {showForm && (
        <section className="claims-panel create-claim-section">
          <form className="create-claim-form" onSubmit={handleCreate}>
            <h3>Create a new claim</h3>
            <label>
              Customer name
              <input
                required
                maxLength={150}
                value={customer}
                onChange={(event) => setCustomer(event.target.value)}
                placeholder="Enter customer name"
              />
            </label>
            <label>
              Claim amount (INR)
              <input
                required
                type="number"
                min="0.01"
                step="0.01"
                value={amount}
                onChange={(event) => setAmount(event.target.value)}
                placeholder="Enter amount"
              />
            </label>
            <button className="primary-button" type="submit" disabled={saving}>
              {saving ? "Creating..." : "Submit Claim"}
            </button>
          </form>
        </section>
      )}

      <ClaimDetails
        claim={selectedClaim}
        onClose={() => setSelectedClaim(null)}
      />

      {detailLoading && <p role="status">Loading claim details...</p>}

      <section className="claims-panel">
        <div className="panel-heading">
          <div>
            <h2>Claims</h2>
            <p>{claims.length} records returned by the claims API.</p>
          </div>
          <button className="secondary-button" onClick={onRefresh} disabled={loading}>
            <RefreshCw size={15} /> Refresh
          </button>
        </div>

        <div className="table-toolbar">
          <label className="search-box">
            <Search size={17} />
            <input
              type="search"
              placeholder="Search claim ID or customer..."
              value={search}
              onChange={(event) => setSearch(event.target.value)}
            />
          </label>

          <select
            className="status-filter"
            value={statusFilter}
            onChange={(event) => setStatusFilter(event.target.value)}
            aria-label="Filter claims by status"
          >
            <option>All statuses</option>
            {Object.values(statusLabels).map((label) => (
              <option key={label}>{label}</option>
            ))}
          </select>
        </div>

        {loading ? (
          <p className="empty-state">Loading claims...</p>
        ) : (
          <div className="table-scroll">
            <table className="claims-table">
              <thead>
                <tr>
                  <th>CLAIM</th>
                  <th>CUSTOMER</th>
                  <th>CLAIM TYPE</th>
                  <th>AMOUNT</th>
                  <th>STATUS</th>
                  <th>UPDATE STATUS</th>
                  <th>ACTIONS</th>
                </tr>
              </thead>
              <tbody>
                {filteredClaims.map((claim) => {
                  const transitions = allowedTransitions[claim.status] || [];

                  return (
                    <tr key={claim.id}>
                      <td>
                        <button
                          className="claim-id claim-id-button"
                          onClick={() => handleView(claim.id)}
                          title={`View ${claim.id}`}
                        >
                          {claim.id}
                        </button>
                      </td>
                      <td>{claim.customer || "Unknown customer"}</td>
                      <td className="muted-cell">Not provided by API</td>
                      <td className="amount-cell">{formatAmount(claim.amount)}</td>
                      <td><StatusBadge status={claim.status} /></td>
                      <td>
                        <select
                          className="status-filter"
                          aria-label={`Update status for ${claim.id}`}
                          value=""
                          disabled={!transitions.length || busyClaimId === claim.id}
                          onChange={(event) =>
                            handleStatusChange(claim.id, event.target.value)
                          }
                        >
                          <option value="">
                            {busyClaimId === claim.id
                              ? "Working..."
                              : transitions.length
                                ? "Change status"
                                : "No transitions"}
                          </option>
                          {transitions.map((status) => (
                            <option key={status} value={status}>
                              {statusLabels[status]}
                            </option>
                          ))}
                        </select>
                      </td>
                      <td>
                        <div className="claims-actions">
                          <button
                            className="icon-button"
                            onClick={() => handleView(claim.id)}
                            title="View full claim"
                            aria-label={`View ${claim.id}`}
                          >
                            <Eye size={16} />
                          </button>
                          <button
                            className="icon-button delete-button"
                            onClick={() => handleDelete(claim.id)}
                            disabled={busyClaimId === claim.id}
                            title="Delete claim"
                            aria-label={`Delete ${claim.id}`}
                          >
                            <Trash2 size={16} />
                          </button>
                        </div>
                      </td>
                    </tr>
                  );
                })}

                {filteredClaims.length === 0 && (
                  <tr>
                    <td colSpan={7} className="empty-state">
                      No claims match your search or status filter.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        )}

        <div className="table-bottom">
          <span>{filteredClaims.length} displayed of {claims.length} claims</span>
          <span className="table-page">Live API data</span>
        </div>
      </section>
    </>
  );
}

function PlaceholderPage({ page, onNavigate }) {
  const details = {
    "AI Assistant": {
      icon: Bot,
      title: "AI Assistant",
      description: "The existing LangGraph and MCP workflow has not yet been connected to this UI.",
      target: "Claims",
      action: "View claims",
    },
    Approvals: {
      icon: ShieldCheck,
      title: "Human review queue",
      description: "Approval workflows are not connected to this page yet.",
      target: "Claims",
      action: "View claims",
    },
    "Policy Search": {
      icon: FileSearch,
      title: "Policy knowledge base",
      description: "Policy retrieval will be connected to the existing RAG pipeline.",
      target: "AI Assistant",
      action: "Open AI assistant",
    },
  };

  const item = details[page] || details["AI Assistant"];
  const Icon = item.icon;

  return (
    <section className="placeholder-page">
      <div className="placeholder-icon"><Icon size={30} /></div>
      <h1>{item.title}</h1>
      <p>{item.description}</p>
      <div className="placeholder-note">
        <Activity size={18} />
        <span>This module is not connected to the frontend yet.</span>
      </div>
      <button className="primary-button" onClick={() => onNavigate(item.target)}>
        {item.action} <ArrowRight size={16} />
      </button>
    </section>
  );
}

export default function App() {
  const [active, setActive] = useState("Overview");
  const [token, setToken] = useState(null);
  const [claims, setClaims] = useState([]);
  const [loading, setLoading] = useState(false);
  const [loginLoading, setLoginLoading] = useState(false);
  const [error, setError] = useState("");
  const [loginError, setLoginError] = useState("");

  const refreshClaims = useCallback(async (accessToken) => {
    setLoading(true);
    setError("");

    try {
      const data = await getClaims(accessToken);

      if (!Array.isArray(data)) {
        throw new Error("Unexpected response from the claims API.");
      }

      setClaims(data);
      return true;
    } catch (err) {
      setError(err.message || "Unable to load claims.");

      if (err.status === 401) {
        setToken(null);
        setClaims([]);
      }

      return false;
    } finally {
      setLoading(false);
    }
  }, []);

  async function handleLogin(username, password) {
    setLoginLoading(true);
    setLoginError("");

    try {
      const result = await login(username, password);

      if (!result?.access_token) {
        throw new Error("Login response did not contain an access token.");
      }

      const loaded = await refreshClaims(result.access_token);

      if (!loaded) {
        setLoginError("Login succeeded, but claims could not be loaded.");
        return;
      }

      setToken(result.access_token);
    } catch (err) {
      setLoginError(err.message || "Login failed.");
    } finally {
      setLoginLoading(false);
    }
  }

  function handleLogout() {
    setToken(null);
    setClaims([]);
    setError("");
    setLoginError("");
    setActive("Overview");
  }

  useEffect(() => {
    if (token) {
      refreshClaims(token);
    }
  }, [token, refreshClaims]);

  if (!token) {
    return (
      <LoginScreen
        onLogin={handleLogin}
        loading={loginLoading}
        error={loginError || error}
      />
    );
  }

  return (
    <div className="app-shell">
      <Sidebar
        active={active}
        onNavigate={setActive}
        onLogout={handleLogout}
      />

      <main className="main-area">
        <header className="topbar">
          <div className="breadcrumbs">
            Workspace <span>/</span> <strong>{active}</strong>
          </div>
          <div className="topbar-right">
            <span className="environment-label">
              <span className="online-dot" /> Development
            </span>
            <div className="topbar-avatar">ST</div>
          </div>
        </header>

        <div className="page-content">
          {active === "Overview" ? (
            <Overview
              claims={claims}
              onNavigate={setActive}
              onRefresh={() => refreshClaims(token)}
              loading={loading}
            />
          ) : active === "Claims" ? (
            <ClaimsPage
              claims={claims}
              token={token}
              loading={loading}
              onRefresh={() => refreshClaims(token)}
              onCreated={() => refreshClaims(token)}
              onStatusUpdated={() => refreshClaims(token)}
              onDeleted={() => refreshClaims(token)}
            />
          ) : active === "AI Assistant" ? (
            <AssistantChat token={token} />
          ) : (
            <PlaceholderPage page={active} onNavigate={setActive} />
          )}

          <footer className="app-footer">
            <span>ClaimsIQ · Insurance Claims Assistant</span>
            <span>Development environment</span>
          </footer>
        </div>
      </main>
    </div>
  );
}
