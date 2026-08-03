import { useEffect, useState } from "react";
import {
  Activity,
  Bot,
  BriefcaseBusiness,
  CheckCircle2,
  CircleAlert,
  History,
  Mail,
  RefreshCw,
  ShieldCheck,
  Users,
} from "lucide-react";

import api from "../services/api";

const statusOptions = ["new", "in_progress", "resolved", "closed"];

function totalValues(values = {}) {
  return Object.values(values).reduce(
    (total, value) => total + Number(value || 0),
    0,
  );
}

function MetricCard({ icon: Icon, label, value, detail }) {
  return (
    <article className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
      <div className="flex items-start justify-between gap-3">
        <div>
          <p className="text-sm font-semibold text-slate-500">{label}</p>
          <p className="mt-2 text-3xl font-bold text-slate-950">{value}</p>
          {detail && <p className="mt-2 text-xs text-slate-500">{detail}</p>}
        </div>
        <span className="rounded-xl bg-blue-100 p-3 text-blue-700">
          <Icon size={22} />
        </span>
      </div>
    </article>
  );
}

export default function AdminOperations() {
  const [summary, setSummary] = useState(null);
  const [tickets, setTickets] = useState([]);
  const [auditEvents, setAuditEvents] = useState([]);
  const [filter, setFilter] = useState("");
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [savingTicketId, setSavingTicketId] = useState(null);
  const [error, setError] = useState("");

  async function loadOperations(showRefresh = false) {
    if (showRefresh) setRefreshing(true);
    setError("");
    try {
      const [
        summaryResponse,
        ticketResponse,
        auditResponse,
      ] = await Promise.all([
        api.get("/admin/operations"),
        api.get("/admin/support/tickets", {
          params: filter ? { status: filter } : {},
        }),
        api.get("/admin/audit-events"),
      ]);
      setSummary(summaryResponse.data);
      setTickets(ticketResponse.data);
      setAuditEvents(auditResponse.data);
    } catch (requestError) {
      setError(
        requestError.response?.status === 403
          ? "This page is available only to configured administrators."
          : requestError.response?.data?.detail
            || "Operations data could not be loaded.",
      );
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }

  useEffect(() => {
    loadOperations();
    // Reload whenever the administrator changes the status filter.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [filter]);

  function editTicket(ticketId, field, value) {
    setTickets((current) =>
      current.map((ticket) =>
        ticket.id === ticketId
          ? { ...ticket, [field]: value }
          : ticket,
      ),
    );
  }

  async function saveTicket(ticket) {
    setSavingTicketId(ticket.id);
    setError("");
    try {
      const response = await api.patch(
        `/admin/support/tickets/${ticket.id}`,
        {
          status: ticket.status,
          admin_note: ticket.admin_note || null,
        },
      );
      setTickets((current) =>
        current.map((item) =>
          item.id === ticket.id
            ? {
              ...item,
              ...response.data,
              user_email: item.user_email,
            }
            : item,
        ),
      );
      const [summaryResponse, auditResponse] = await Promise.all([
        api.get("/admin/operations"),
        api.get("/admin/audit-events"),
      ]);
      setSummary(summaryResponse.data);
      setAuditEvents(auditResponse.data);
    } catch (requestError) {
      setError(
        requestError.response?.data?.detail
          || "The support request could not be updated.",
      );
    } finally {
      setSavingTicketId(null);
    }
  }

  const metrics = summary?.metrics;

  return (
    <div className="space-y-7">
      <section className="flex flex-col justify-between gap-5 rounded-3xl bg-gradient-to-r from-slate-900 to-blue-900 p-8 text-white shadow-xl md:flex-row md:items-center">
        <div>
          <div className="flex items-center gap-3">
            <ShieldCheck size={30} />
            <h1 className="text-3xl font-bold sm:text-4xl">Operations</h1>
          </div>
          <p className="mt-3 max-w-2xl text-blue-100">
            Product activity, deployment integration status, and user support
            requests. Configuration is shown as status only; secrets are never
            displayed.
          </p>
        </div>
        <button
          type="button"
          onClick={() => loadOperations(true)}
          disabled={refreshing}
          className="inline-flex items-center justify-center gap-2 rounded-xl bg-white px-5 py-3 font-semibold text-blue-800 disabled:cursor-wait disabled:opacity-60"
        >
          <RefreshCw
            size={18}
            className={refreshing ? "animate-spin" : ""}
          />
          Refresh
        </button>
      </section>

      {error && (
        <div
          role="alert"
          className="rounded-xl border border-red-300 bg-red-50 p-4 text-red-700"
        >
          {error}
        </div>
      )}

      {loading ? (
        <div className="rounded-2xl border border-slate-200 bg-white p-10 text-center text-slate-500">
          Loading operations...
        </div>
      ) : summary && metrics ? (
        <>
          <section className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
            <MetricCard
              icon={Users}
              label="Accounts"
              value={metrics.users.total}
              detail={`${metrics.users.verified} email verified`}
            />
            <MetricCard
              icon={BriefcaseBusiness}
              label="Tracked applications"
              value={totalValues(metrics.applications)}
              detail={`${metrics.jobs.saved_jobs} saved jobs · ${metrics.jobs.saved_searches} saved searches · ${metrics.jobs.email_alert_searches || 0} email alerts`}
            />
            <MetricCard
              icon={Bot}
              label="AI requests"
              value={metrics.ai_requests_last_24_hours}
              detail="Last 24 hours"
            />
            <MetricCard
              icon={Mail}
              label="Open support requests"
              value={
                Number(metrics.support.new || 0)
                + Number(metrics.support.in_progress || 0)
              }
              detail={`${Number(metrics.support.resolved || 0)} resolved · ${Number(metrics.admin_audit_events || 0)} audited changes`}
            />
          </section>

          <section className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
            <div className="flex flex-wrap items-center justify-between gap-3">
              <div>
                <h2 className="text-xl font-bold text-slate-950">
                  Deployment status
                </h2>
                <p className="mt-1 text-sm text-slate-500">
                  {summary.environment} · {summary.release}
                </p>
              </div>
              <span className="inline-flex items-center gap-2 rounded-full bg-emerald-100 px-3 py-1 text-xs font-bold uppercase tracking-wide text-emerald-800">
                <Activity size={15} />
                API connected
              </span>
            </div>
            <div className="mt-5 grid gap-3 md:grid-cols-2 xl:grid-cols-4">
              {[
                ["Google sign-in", summary.configuration.google_sign_in],
                ["Email delivery", summary.configuration.email_delivery],
                [
                  "Saved-search email alerts",
                  summary.configuration.job_alert_emails,
                ],
                [
                  "Resume malware scanning",
                  summary.configuration.resume_malware_scanning,
                ],
                ["Billing", summary.configuration.billing],
              ].map(([label, configured]) => (
                <div
                  key={label}
                  className={`flex items-center gap-3 rounded-xl border p-4 ${
                    configured
                      ? "border-emerald-200 bg-emerald-50"
                      : "border-amber-200 bg-amber-50"
                  }`}
                >
                  {configured ? (
                    <CheckCircle2 className="text-emerald-700" size={20} />
                  ) : (
                    <CircleAlert className="text-amber-700" size={20} />
                  )}
                  <div>
                    <p className="font-semibold text-slate-900">{label}</p>
                    <p className="text-xs text-slate-600">
                      {configured ? "Configured" : "Not configured"}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </section>

          <section className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
            <div className="flex items-center gap-3">
              <span className="rounded-xl bg-blue-100 p-3 text-blue-700">
                <History size={21} />
              </span>
              <div>
                <h2 className="text-xl font-bold text-slate-950">
                  Administrator audit history
                </h2>
                <p className="mt-1 text-sm text-slate-600">
                  Append-only records of support changes. Ticket messages and
                  internal-note text are not copied into this history.
                </p>
              </div>
            </div>
            {auditEvents.length ? (
              <div className="mt-5 divide-y divide-slate-100">
                {auditEvents.map((event) => {
                  const details = event.details || {};
                  const noteChanged = (
                    details.previous_note_present
                    !== details.new_note_present
                  );
                  return (
                    <article
                      key={event.id}
                      className="flex flex-col justify-between gap-3 py-4 md:flex-row md:items-center"
                    >
                      <div>
                        <p className="font-semibold text-slate-900">
                          {event.actor_email} updated support request{" "}
                          {event.target_id}
                        </p>
                        <p className="mt-1 text-sm text-slate-600">
                          Status: {details.previous_status || "unknown"} →{" "}
                          {details.new_status || "unknown"}
                          {noteChanged ? " · Internal note presence changed" : ""}
                        </p>
                      </div>
                      <div className="shrink-0 text-xs text-slate-500 md:text-right">
                        <p>{new Date(event.created_at).toLocaleString()}</p>
                        {event.request_id && (
                          <p className="mt-1 font-mono">
                            Request {event.request_id}
                          </p>
                        )}
                      </div>
                    </article>
                  );
                })}
              </div>
            ) : (
              <p className="mt-5 rounded-xl border border-dashed border-slate-300 p-5 text-sm text-slate-500">
                No administrator changes have been recorded yet.
              </p>
            )}
          </section>

          <section className="space-y-4">
            <div className="flex flex-wrap items-end justify-between gap-4">
              <div>
                <h2 className="text-2xl font-bold text-slate-950">
                  Support requests
                </h2>
                <p className="mt-1 text-sm text-slate-600">
                  Review, classify, and record an internal resolution note.
                </p>
              </div>
              <label>
                <span className="mb-1 block text-xs font-bold uppercase tracking-wide text-slate-500">
                  Filter
                </span>
                <select
                  value={filter}
                  onChange={(event) => setFilter(event.target.value)}
                  className="rounded-xl border border-slate-300 bg-white px-4 py-2 text-slate-900"
                >
                  <option value="">All requests</option>
                  {statusOptions.map((status) => (
                    <option key={status} value={status}>
                      {status.replace("_", " ")}
                    </option>
                  ))}
                </select>
              </label>
            </div>

            {tickets.length ? tickets.map((ticket) => (
              <article
                key={ticket.id}
                className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm"
              >
                <div className="flex flex-col justify-between gap-4 lg:flex-row">
                  <div className="min-w-0">
                    <div className="flex flex-wrap items-center gap-2">
                      <h3 className="text-lg font-bold text-slate-950">
                        {ticket.subject}
                      </h3>
                      <span className="rounded-full bg-slate-100 px-3 py-1 text-xs font-semibold uppercase text-slate-600">
                        {ticket.category}
                      </span>
                    </div>
                    <p className="mt-2 text-sm text-slate-500">
                      {ticket.user_email} ·{" "}
                      {new Date(ticket.created_at).toLocaleString()}
                    </p>
                    <p className="mt-4 whitespace-pre-line text-sm leading-6 text-slate-700">
                      {ticket.message}
                    </p>
                  </div>
                  <label className="shrink-0">
                    <span className="mb-1 block text-xs font-bold uppercase tracking-wide text-slate-500">
                      Status
                    </span>
                    <select
                      value={ticket.status}
                      onChange={(event) =>
                        editTicket(ticket.id, "status", event.target.value)
                      }
                      className="rounded-xl border border-slate-300 bg-white px-4 py-2 text-slate-900"
                    >
                      {statusOptions.map((status) => (
                        <option key={status} value={status}>
                          {status.replace("_", " ")}
                        </option>
                      ))}
                    </select>
                  </label>
                </div>

                <div className="mt-5 flex flex-col gap-3 sm:flex-row sm:items-end">
                  <label className="min-w-0 flex-1">
                    <span className="mb-2 block text-sm font-semibold text-slate-700">
                      Internal note
                    </span>
                    <textarea
                      value={ticket.admin_note || ""}
                      onChange={(event) =>
                        editTicket(ticket.id, "admin_note", event.target.value)
                      }
                      rows={2}
                      maxLength={10000}
                      className="w-full rounded-xl border border-slate-300 px-4 py-3 text-slate-900"
                    />
                  </label>
                  <button
                    type="button"
                    onClick={() => saveTicket(ticket)}
                    disabled={savingTicketId === ticket.id}
                    className="rounded-xl bg-blue-600 px-5 py-3 font-semibold text-white hover:bg-blue-700 disabled:cursor-wait disabled:opacity-60"
                  >
                    {savingTicketId === ticket.id ? "Saving..." : "Save"}
                  </button>
                </div>
              </article>
            )) : (
              <div className="rounded-2xl border border-dashed border-slate-300 bg-white p-10 text-center text-slate-500">
                No support requests match this filter.
              </div>
            )}
          </section>
        </>
      ) : null}
    </div>
  );
}
