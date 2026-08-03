import { useEffect, useState } from "react";
import {
  BellRing,
  Bookmark,
  BriefcaseBusiness,
  Building2,
  Clock3,
  ExternalLink,
  Mail,
  MapPin,
  Play,
  SearchCheck,
  Trash2,
} from "lucide-react";
import { Link, useNavigate } from "react-router-dom";

import api from "../services/api";

function formatDate(value) {
  if (!value) return "Not run yet";
  return new Date(value).toLocaleString([], {
    dateStyle: "medium",
    timeStyle: "short",
  });
}

function filterSummary(filters) {
  return [
    filters.keyword,
    filters.country || "Worldwide",
    filters.city,
    filters.work_mode,
    filters.employment_type,
    filters.posted_within_days
      ? `Past ${filters.posted_within_days} days`
      : "",
  ].filter(Boolean).join(" · ");
}

export default function JobLibrary() {
  const navigate = useNavigate();
  const [savedJobs, setSavedJobs] = useState([]);
  const [savedSearches, setSavedSearches] = useState([]);
  const [emailAlertStatus, setEmailAlertStatus] = useState(null);
  const [alertDeliveries, setAlertDeliveries] = useState([]);
  const [activeTab, setActiveTab] = useState("jobs");
  const [loading, setLoading] = useState(true);
  const [runningSearchId, setRunningSearchId] = useState(null);
  const [savingAlertId, setSavingAlertId] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    let active = true;
    Promise.all([
      api.get("/job-library/saved-jobs"),
      api.get("/job-library/searches"),
      api.get("/job-library/email-alerts/status"),
      api.get("/job-library/email-alerts/deliveries"),
    ])
      .then(([
        jobsResponse,
        searchesResponse,
        statusResponse,
        deliveriesResponse,
      ]) => {
        if (!active) return;
        setSavedJobs(jobsResponse.data);
        setSavedSearches(searchesResponse.data);
        setEmailAlertStatus(statusResponse.data);
        setAlertDeliveries(deliveriesResponse.data);
      })
      .catch((requestError) => {
        if (!active) return;
        setError(
          requestError.response?.data?.detail
            || "Your job library could not be loaded.",
        );
      })
      .finally(() => {
        if (active) setLoading(false);
      });

    return () => {
      active = false;
    };
  }, []);

  async function removeSavedJob(savedJobId) {
    setError("");
    try {
      await api.delete(`/job-library/saved-jobs/${savedJobId}`);
      setSavedJobs((current) =>
        current.filter((item) => item.id !== savedJobId),
      );
    } catch (requestError) {
      setError(
        requestError.response?.data?.detail
          || "The saved job could not be removed.",
      );
    }
  }

  async function removeSavedSearch(savedSearchId) {
    setError("");
    try {
      await api.delete(`/job-library/searches/${savedSearchId}`);
      setSavedSearches((current) =>
        current.filter((item) => item.id !== savedSearchId),
      );
    } catch (requestError) {
      setError(
        requestError.response?.data?.detail
          || "The saved search could not be removed.",
      );
    }
  }

  async function runSavedSearch(savedSearch) {
    setRunningSearchId(savedSearch.id);
    setError("");
    try {
      const response = await api.post(
        `/job-library/searches/${savedSearch.id}/run`,
      );
      setSavedSearches((current) =>
        current.map((item) =>
          item.id === savedSearch.id
            ? response.data.saved_search
            : item,
        ),
      );
      navigate("/jobs", {
        state: {
          savedSearchRun: response.data,
        },
      });
    } catch (requestError) {
      setError(
        requestError.response?.data?.detail
          || "The saved search could not be run.",
      );
    } finally {
      setRunningSearchId(null);
    }
  }

  async function updateEmailAlert(
    savedSearch,
    enabled,
    frequency = savedSearch.alert_frequency || "daily",
  ) {
    setSavingAlertId(savedSearch.id);
    setError("");
    try {
      const timezone = (
        savedSearch.alert_timezone
        || Intl.DateTimeFormat().resolvedOptions().timeZone
        || "UTC"
      );
      const response = await api.patch(
        `/job-library/searches/${savedSearch.id}/email-alerts`,
        {
          enabled,
          frequency,
          timezone,
        },
      );
      setSavedSearches((current) =>
        current.map((item) =>
          item.id === savedSearch.id ? response.data : item,
        ),
      );
    } catch (requestError) {
      setError(
        requestError.response?.data?.detail
          || "The email alert preference could not be saved.",
      );
    } finally {
      setSavingAlertId(null);
    }
  }

  const newMatchCount = savedSearches.reduce(
    (total, search) => total + Number(search.new_match_count || 0),
    0,
  );

  return (
    <div className="space-y-7">
      <section className="flex flex-col justify-between gap-5 rounded-3xl bg-gradient-to-r from-blue-600 to-indigo-700 p-8 text-white shadow-xl md:flex-row md:items-center">
        <div>
          <div className="flex items-center gap-3">
            <BriefcaseBusiness size={30} />
            <h1 className="text-3xl font-bold sm:text-4xl">Job Library</h1>
          </div>
          <p className="mt-3 max-w-2xl text-blue-100">
            Keep promising roles, repeat your best searches, and see when a
            saved search finds something new.
          </p>
        </div>
        <Link
          to="/jobs"
          className="inline-flex items-center justify-center gap-2 rounded-xl bg-white px-5 py-3 font-semibold text-blue-700 hover:bg-blue-50"
        >
          <SearchCheck size={18} />
          Search jobs
        </Link>
      </section>

      <div className="flex flex-wrap gap-2" role="tablist" aria-label="Job library">
        <button
          type="button"
          role="tab"
          aria-selected={activeTab === "jobs"}
          onClick={() => setActiveTab("jobs")}
          className={`inline-flex items-center gap-2 rounded-full px-4 py-2 text-sm font-semibold ${
            activeTab === "jobs"
              ? "bg-blue-600 text-white"
              : "border border-slate-300 bg-white text-slate-700"
          }`}
        >
          <Bookmark size={17} />
          Saved jobs ({savedJobs.length})
        </button>
        <button
          type="button"
          role="tab"
          aria-selected={activeTab === "searches"}
          onClick={() => setActiveTab("searches")}
          className={`inline-flex items-center gap-2 rounded-full px-4 py-2 text-sm font-semibold ${
            activeTab === "searches"
              ? "bg-blue-600 text-white"
              : "border border-slate-300 bg-white text-slate-700"
          }`}
        >
          <BellRing size={17} />
          Saved searches ({savedSearches.length})
          {newMatchCount > 0 && (
            <span className="rounded-full bg-amber-400 px-2 py-0.5 text-xs font-bold text-amber-950">
              {newMatchCount} new
            </span>
          )}
        </button>
      </div>

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
          Loading your job library...
        </div>
      ) : activeTab === "jobs" ? (
        savedJobs.length ? (
          <section className="grid gap-5 xl:grid-cols-2">
            {savedJobs.map((savedJob) => {
              const job = savedJob.job;
              const providerUrl = job.listing_url || job.apply_url;
              return (
                <article
                  key={savedJob.id}
                  className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm"
                >
                  <div className="flex items-start justify-between gap-4">
                    <div>
                      <h2 className="text-xl font-bold text-slate-950">
                        {job.title}
                      </h2>
                      <p className="mt-2 flex items-center gap-2 text-sm text-slate-600">
                        <Building2 size={16} />
                        {job.company}
                      </p>
                      <p className="mt-2 flex items-center gap-2 text-sm text-slate-600">
                        <MapPin size={16} />
                        {job.location || "Location not listed"}
                      </p>
                    </div>
                    {Number.isFinite(Number(job.analysis?.match_score)) && (
                      <span className="rounded-xl bg-blue-100 px-3 py-2 font-bold text-blue-700">
                        {Number(job.analysis.match_score)}%
                      </span>
                    )}
                  </div>

                  {job.description && (
                    <p className="mt-4 line-clamp-4 text-sm leading-6 text-slate-600">
                      {job.description}
                    </p>
                  )}

                  <div className="mt-5 flex flex-wrap items-center justify-between gap-3 border-t border-slate-100 pt-5">
                    <p className="text-xs text-slate-500">
                      Saved {formatDate(savedJob.created_at)}
                    </p>
                    <div className="flex flex-wrap gap-2">
                      <button
                        type="button"
                        onClick={() => removeSavedJob(savedJob.id)}
                        className="inline-flex items-center gap-2 rounded-xl border border-slate-300 px-4 py-2 text-sm font-semibold text-slate-700 hover:bg-slate-50"
                      >
                        <Trash2 size={16} />
                        Remove
                      </button>
                      {providerUrl && (
                        <a
                          href={providerUrl}
                          target="_blank"
                          rel="noreferrer"
                          className="inline-flex items-center gap-2 rounded-xl bg-blue-600 px-4 py-2 text-sm font-semibold text-white hover:bg-blue-700"
                        >
                          Continue to listing on {job.source || "provider"}
                          <ExternalLink size={16} />
                        </a>
                      )}
                    </div>
                  </div>
                </article>
              );
            })}
          </section>
        ) : (
          <EmptyState
            icon={Bookmark}
            title="No saved jobs yet"
            message="Save promising roles from job search so you can compare and revisit them here."
          />
        )
      ) : savedSearches.length ? (
        <section className="space-y-4">
          {savedSearches.map((savedSearch) => (
            <article
              key={savedSearch.id}
              className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm"
            >
              <div className="flex flex-col gap-5 lg:flex-row lg:items-center">
                <div className="min-w-0 flex-1">
                  <div className="flex flex-wrap items-center gap-2">
                    <h2 className="text-xl font-bold text-slate-950">
                      {savedSearch.name}
                    </h2>
                    {savedSearch.new_match_count > 0 && (
                      <span className="rounded-full bg-amber-100 px-3 py-1 text-xs font-bold text-amber-800">
                        {savedSearch.new_match_count} new matches
                      </span>
                    )}
                  </div>
                  <p className="mt-2 text-sm text-slate-600">
                    {filterSummary(savedSearch.filters)}
                  </p>
                  <p className="mt-2 text-xs text-slate-500">
                    Last checked: {formatDate(savedSearch.last_run_at)}
                    {savedSearch.last_run_at
                      ? ` · ${savedSearch.last_result_count} results`
                      : ""}
                  </p>
                </div>
                <div className="flex flex-wrap gap-2">
                  <button
                    type="button"
                    onClick={() => removeSavedSearch(savedSearch.id)}
                    className="inline-flex items-center gap-2 rounded-xl border border-slate-300 px-4 py-2 text-sm font-semibold text-slate-700 hover:bg-slate-50"
                  >
                    <Trash2 size={16} />
                    Delete
                  </button>
                  <button
                    type="button"
                    disabled={runningSearchId === savedSearch.id}
                    onClick={() => runSavedSearch(savedSearch)}
                    className="inline-flex items-center gap-2 rounded-xl bg-blue-600 px-4 py-2 text-sm font-semibold text-white hover:bg-blue-700 disabled:cursor-wait disabled:opacity-60"
                  >
                    <Play size={16} />
                    {runningSearchId === savedSearch.id
                      ? "Checking..."
                      : "Check for matches"}
                  </button>
                </div>
              </div>

              <div className="mt-5 rounded-xl border border-slate-200 bg-slate-50 p-4">
                <div className="flex flex-col justify-between gap-4 sm:flex-row sm:items-center">
                  <div>
                    <p className="flex items-center gap-2 font-semibold text-slate-900">
                      <Mail size={17} className="text-blue-600" />
                      Email me about new matches
                    </p>
                    <p className="mt-1 max-w-2xl text-xs leading-5 text-slate-600">
                      {emailAlertStatus?.available
                        ? emailAlertStatus.email_verified
                          ? "Off by default. Turn this on only if you want NextHire to email your verified account address."
                          : "Verify your account email before enabling this alert."
                        : "Automatic email delivery is not enabled for this deployment. Manual checks and in-app notifications still work."}
                    </p>
                  </div>
                  <div className="flex flex-wrap items-center gap-3">
                    <label>
                      <span className="sr-only">Email alert frequency</span>
                      <select
                        value={savedSearch.alert_frequency || "daily"}
                        disabled={
                          !savedSearch.email_alerts_enabled
                          || savingAlertId === savedSearch.id
                        }
                        onChange={(event) =>
                          updateEmailAlert(
                            savedSearch,
                            true,
                            event.target.value,
                          )}
                        className="rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm text-slate-800 disabled:opacity-60"
                      >
                        <option value="daily">Daily</option>
                        <option value="weekly">Weekly</option>
                      </select>
                    </label>
                    <button
                      type="button"
                      role="switch"
                      aria-checked={savedSearch.email_alerts_enabled}
                      disabled={
                        !emailAlertStatus?.available
                        || !emailAlertStatus?.email_verified
                        || savingAlertId === savedSearch.id
                      }
                      onClick={() =>
                        updateEmailAlert(
                          savedSearch,
                          !savedSearch.email_alerts_enabled,
                        )}
                      className={`rounded-full px-4 py-2 text-sm font-bold ${
                        savedSearch.email_alerts_enabled
                          ? "bg-emerald-600 text-white"
                          : "border border-slate-300 bg-white text-slate-700"
                      } disabled:cursor-not-allowed disabled:opacity-50`}
                    >
                      {savingAlertId === savedSearch.id
                        ? "Saving..."
                        : savedSearch.email_alerts_enabled
                          ? "Email on"
                          : "Email off"}
                    </button>
                  </div>
                </div>
                {savedSearch.email_alerts_enabled && (
                  <p className="mt-3 flex items-center gap-2 text-xs text-slate-500">
                    <Clock3 size={14} />
                    Next scheduled check:{" "}
                    {formatDate(savedSearch.next_alert_at)}
                    {savedSearch.last_email_at
                      ? ` · Last email: ${formatDate(savedSearch.last_email_at)}`
                      : ""}
                  </p>
                )}
              </div>
            </article>
          ))}

          {alertDeliveries.length > 0 && (
            <section className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
              <h2 className="text-lg font-bold text-slate-950">
                Recent email alert activity
              </h2>
              <div className="mt-4 divide-y divide-slate-100">
                {alertDeliveries.slice(0, 5).map((delivery) => (
                  <div
                    key={delivery.id}
                    className="flex flex-wrap items-center justify-between gap-3 py-3 text-sm"
                  >
                    <span className="text-slate-700">
                      {delivery.match_count} new{" "}
                      {delivery.match_count === 1 ? "match" : "matches"}
                    </span>
                    <span className="text-xs font-semibold uppercase text-slate-500">
                      {delivery.status} ·{" "}
                      {formatDate(delivery.sent_at || delivery.created_at)}
                    </span>
                  </div>
                ))}
              </div>
            </section>
          )}
        </section>
      ) : (
        <EmptyState
          icon={BellRing}
          title="No saved searches yet"
          message="Run a job search and save its filters to check the same opportunity set again later."
        />
      )}
    </div>
  );
}

function EmptyState({ icon: Icon, title, message }) {
  return (
    <section className="rounded-2xl border border-dashed border-slate-300 bg-white p-12 text-center">
      <Icon className="mx-auto text-blue-600" size={42} />
      <h2 className="mt-4 text-xl font-bold text-slate-900">{title}</h2>
      <p className="mx-auto mt-2 max-w-xl text-slate-600">{message}</p>
      <Link
        to="/jobs"
        className="mt-5 inline-flex rounded-xl bg-blue-600 px-5 py-3 font-semibold text-white hover:bg-blue-700"
      >
        Search jobs
      </Link>
    </section>
  );
}
