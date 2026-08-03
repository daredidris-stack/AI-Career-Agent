import { useEffect, useState } from "react";
import {
  BellPlus,
  Bookmark,
  BookmarkCheck,
  Building2,
  ExternalLink,
  MapPin,
  Search,
  Sparkles,
  X,
} from "lucide-react";
import { useLocation, useNavigate } from "react-router-dom";

import api from "../services/api";
import { getProfile } from "../services/api";
import { countries } from "../data/countries";
import ApplyAssistant from "../components/jobs/ApplyAssistant";

function jobIdentity(job) {
  if (job.source_job_id) {
    return `source:${String(job.source || "").toLowerCase()}:${job.source_job_id}`;
  }
  const providerUrl = job.apply_url || job.listing_url;
  if (providerUrl) return `url:${providerUrl}`;
  return [
    "job",
    String(job.title || "").toLowerCase(),
    String(job.company || "").toLowerCase(),
    String(job.location || "").toLowerCase(),
  ].join(":");
}

function savedJobPayload(job) {
  return {
    title: job.title,
    company: job.company,
    source: job.source || null,
    source_job_id: job.source_job_id || null,
    location: job.location || null,
    listing_url: job.listing_url || null,
    apply_url: job.apply_url || null,
    description: job.description || null,
    job_type: job.job_type || null,
    workplace_type: job.workplace_type || null,
    salary: job.salary || null,
    visa_sponsorship: job.visa_sponsorship ?? null,
    updated: job.updated || null,
    analysis: job.analysis || {},
  };
}


function Jobs() {
  const location = useLocation();
  const navigate = useNavigate();
  const [targetRole, setTargetRole] = useState("");
  const [country, setCountry] = useState("Worldwide");
  const [city, setCity] = useState("");
  const [industry, setIndustry] = useState("");
  const [workMode, setWorkMode] = useState("");
  const [employmentType, setEmploymentType] = useState("");
  const [postedWithinDays, setPostedWithinDays] = useState(0);
  const [minimumSalary, setMinimumSalary] = useState(0);
  const [minimumScore, setMinimumScore] = useState(0);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [selectedJob, setSelectedJob] = useState(null);
  const [savedJobs, setSavedJobs] = useState([]);
  const [savingJobIdentity, setSavingJobIdentity] = useState("");
  const [showSaveSearch, setShowSaveSearch] = useState(false);
  const [savedSearchName, setSavedSearchName] = useState("");
  const [savingSearch, setSavingSearch] = useState(false);
  const [saveMessage, setSaveMessage] = useState("");

  useEffect(() => {
    async function loadProfileDefaults() {
      try {
        const response = await getProfile();
        setTargetRole(response.data.target_role || "");
        setWorkMode(response.data.preferred_work_mode || "");
      } catch {
        // A profile is optional; the user can enter search filters directly.
      }
    }

    loadProfileDefaults();
  }, []);

  useEffect(() => {
    let active = true;
    api.get("/job-library/saved-jobs")
      .then((response) => {
        if (active) setSavedJobs(response.data);
      })
      .catch(() => {
        // Job search remains available if the saved-job list cannot be loaded.
      });
    return () => {
      active = false;
    };
  }, []);

  useEffect(() => {
    const savedSearchRun = location.state?.savedSearchRun;
    if (!savedSearchRun) return;

    const filters = savedSearchRun.saved_search.filters || {};
    setTargetRole(filters.keyword || "");
    setCountry(filters.country || "Worldwide");
    setCity(filters.city || "");
    setIndustry(filters.industry || "");
    setWorkMode(filters.work_mode || "");
    setEmploymentType(filters.employment_type || "");
    setPostedWithinDays(Number(filters.posted_within_days || 0));
    setMinimumSalary(Number(filters.min_salary || 0));
    setMinimumScore(Number(filters.min_score || 0));
    setResult(savedSearchRun.result);
    setSaveMessage(
      savedSearchRun.saved_search.new_match_count > 0
        ? `${savedSearchRun.saved_search.new_match_count} new matches found.`
        : "Saved search checked. No new matches this time.",
    );

    api.post(
      `/job-library/searches/${savedSearchRun.saved_search.id}/acknowledge`,
    ).catch(() => {
      // The result is still usable if the alert badge cannot be acknowledged.
    });
    navigate(location.pathname, { replace: true, state: null });
  }, [location.pathname, location.state, navigate]);

  async function searchJobs(event) {
    event.preventDefault();
    await executeSearch(1);
  }

  async function executeSearch(pageNumber) {
    setLoading(true);
    setError("");

    try {
      const response = await api.get("/jobs/search", {
        params: {
          ...(targetRole.trim() && { keyword: targetRole.trim() }),
          ...(country.trim() && { country: country.trim() }),
          ...(city.trim() && { city: city.trim() }),
          ...(industry.trim() && { industry: industry.trim() }),
          ...(workMode && { work_mode: workMode }),
          ...(employmentType && { employment_type: employmentType }),
          ...(postedWithinDays > 0 && { posted_within_days: postedWithinDays }),
          ...(minimumSalary > 0 && { min_salary: minimumSalary }),
          ...(minimumScore > 0 && { min_score: minimumScore }),
          page: pageNumber,
          per_page: 50,
        },
      });

      setResult(response.data);
      setSaveMessage("");
    } catch (requestError) {
      setResult(null);
      setError(
        requestError.response?.data?.detail
          || "Job search is temporarily unavailable.",
      );
    } finally {
      setLoading(false);
    }
  }

  function getSavedJob(job) {
    const identity = jobIdentity(job);
    return savedJobs.find((item) => jobIdentity(item.job) === identity);
  }

  async function toggleSavedJob(job) {
    const identity = jobIdentity(job);
    const existing = getSavedJob(job);
    setSavingJobIdentity(identity);
    setError("");
    try {
      if (existing) {
        await api.delete(`/job-library/saved-jobs/${existing.id}`);
        setSavedJobs((current) =>
          current.filter((item) => item.id !== existing.id),
        );
      } else {
        const response = await api.post(
          "/job-library/saved-jobs",
          savedJobPayload(job),
        );
        setSavedJobs((current) => [
          response.data,
          ...current.filter(
            (item) => jobIdentity(item.job) !== identity,
          ),
        ]);
      }
    } catch (requestError) {
      setError(
        requestError.response?.data?.detail
          || "The saved job could not be updated.",
      );
    } finally {
      setSavingJobIdentity("");
    }
  }

  async function saveCurrentSearch(event) {
    event.preventDefault();
    setSavingSearch(true);
    setError("");
    setSaveMessage("");
    try {
      await api.post("/job-library/searches", {
        name: savedSearchName.trim(),
        filters: {
          keyword: targetRole.trim(),
          country: country.trim() || "Worldwide",
          city: city.trim(),
          industry: industry.trim(),
          work_mode: workMode,
          employment_type: employmentType,
          posted_within_days: postedWithinDays,
          min_salary: minimumSalary,
          min_score: minimumScore,
        },
      });
      setShowSaveSearch(false);
      setSavedSearchName("");
      setSaveMessage("Search saved. You can check it again from Job Library.");
    } catch (requestError) {
      setError(
        requestError.response?.data?.detail
          || "The search could not be saved.",
      );
    } finally {
      setSavingSearch(false);
    }
  }

  return (
    <div className="space-y-8">
      <section className="rounded-3xl bg-gradient-to-r from-blue-600 to-indigo-700 p-8 text-white shadow-xl">
        <div className="flex items-center gap-3">
          <Sparkles size={30} />
          <h1 className="text-3xl font-bold sm:text-4xl">Matched Jobs</h1>
        </div>
        <p className="mt-3 max-w-3xl text-lg text-blue-100">
          Search opportunities worldwide. Your profile and latest resume skills improve ranking when available.
        </p>
      </section>

      <form
        onSubmit={searchJobs}
        className="rounded-2xl border border-gray-800 bg-gray-900 p-6"
      >
        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
          <label className="block">
            <span className="mb-2 block text-sm font-medium text-gray-300">
              Target role
            </span>
            <input
              value={targetRole}
              onChange={(event) => setTargetRole(event.target.value)}
              placeholder="Site Reliability Engineer"
              required
              className="w-full rounded-xl border border-gray-700 bg-gray-950 px-4 py-3 text-white outline-none focus:border-blue-500"
            />
          </label>

          <label className="block">
            <span className="mb-2 block text-sm font-medium text-gray-300">
              Country
            </span>
            <select
              value={country}
              onChange={(event) => {
                const nextCountry = event.target.value;
                setCountry(nextCountry);
                if (nextCountry === "Worldwide") setCity("");
              }}
              className="w-full rounded-xl border border-gray-700 bg-gray-950 px-4 py-3 text-white outline-none focus:border-blue-500"
            >
              <option value="Worldwide">Worldwide</option>
              {countries.map((countryName) => (
                <option key={countryName} value={countryName}>
                  {countryName}
                </option>
              ))}
            </select>
          </label>

          <label className="block">
            <span className="mb-2 block text-sm font-medium text-gray-300">
              City
            </span>
            <input
              value={city}
              onChange={(event) => setCity(event.target.value)}
              placeholder={country === "Worldwide" ? "All cities" : "Queretaro"}
              disabled={country === "Worldwide"}
              className="w-full rounded-xl border border-gray-700 bg-gray-950 px-4 py-3 text-white outline-none focus:border-blue-500 disabled:cursor-not-allowed disabled:opacity-50"
            />
          </label>

          <label className="block">
            <span className="mb-2 block text-sm font-medium text-gray-300">
              Industry
            </span>
            <input
              value={industry}
              onChange={(event) => setIndustry(event.target.value)}
              placeholder="Technology, finance, healthcare..."
              className="w-full rounded-xl border border-gray-700 bg-gray-950 px-4 py-3 text-white outline-none focus:border-blue-500"
            />
          </label>

          <label className="block">
            <span className="mb-2 block text-sm font-medium text-gray-300">
              Work arrangement
            </span>
            <select
              value={workMode}
              onChange={(event) => setWorkMode(event.target.value)}
              className="w-full rounded-xl border border-gray-700 bg-gray-950 px-4 py-3 text-white outline-none focus:border-blue-500"
            >
              <option value="">Any arrangement</option>
              <option value="Remote">Remote</option>
              <option value="Hybrid">Hybrid</option>
              <option value="On-site">On-site</option>
            </select>
          </label>

          <label className="block">
            <span className="mb-2 block text-sm font-medium text-gray-300">Employment type</span>
            <select value={employmentType} onChange={(event) => setEmploymentType(event.target.value)} className="w-full rounded-xl border border-gray-700 bg-gray-950 px-4 py-3 text-white outline-none focus:border-blue-500">
              <option value="">Any type</option>
              <option value="Full Time">Full time</option>
              <option value="Part Time">Part time</option>
              <option value="Contract">Contract</option>
              <option value="Intern">Internship</option>
            </select>
          </label>

          <label className="block">
            <span className="mb-2 block text-sm font-medium text-gray-300">Date posted</span>
            <select value={postedWithinDays} onChange={(event) => setPostedWithinDays(Number(event.target.value))} className="w-full rounded-xl border border-gray-700 bg-gray-950 px-4 py-3 text-white outline-none focus:border-blue-500">
              <option value={0}>Any time</option>
              <option value={1}>Past 24 hours</option>
              <option value={7}>Past week</option>
              <option value={30}>Past month</option>
            </select>
          </label>

          <label className="block">
            <span className="mb-2 block text-sm font-medium text-gray-300">Minimum disclosed salary</span>
            <input type="number" min="0" step="5000" value={minimumSalary || ""} onChange={(event) => setMinimumSalary(Number(event.target.value))} placeholder="80000" className="w-full rounded-xl border border-gray-700 bg-gray-950 px-4 py-3 text-white outline-none focus:border-blue-500" />
          </label>

          <label className="block">
            <span className="mb-2 block text-sm font-medium text-gray-300">
              Minimum match
            </span>
            <select
              value={minimumScore}
              onChange={(event) => setMinimumScore(Number(event.target.value))}
              className="w-full rounded-xl border border-gray-700 bg-gray-950 px-4 py-3 text-white outline-none focus:border-blue-500"
            >
              <option value={0}>Any score</option>
              <option value={50}>50%+</option>
              <option value={70}>70%+</option>
              <option value={85}>85%+</option>
            </select>
          </label>

        </div>

        <div className="mt-5 flex flex-wrap items-center justify-between gap-4">
          <p className="text-sm text-gray-500">
            Searches cover worldwide opportunities by default. Choose a country and optional city to narrow the results.
          </p>
          <button
            type="submit"
            disabled={loading}
            className="flex items-center justify-center gap-2 rounded-xl bg-blue-600 px-6 py-3 font-semibold text-white transition hover:bg-blue-700 disabled:cursor-wait disabled:opacity-60"
          >
            <Search size={19} />
            {loading ? "Matching..." : "Find My Jobs"}
          </button>
        </div>
      </form>

      {error && (
        <div role="alert" className="rounded-2xl border border-red-500/30 bg-red-500/10 p-5 text-red-200">
          {error}
        </div>
      )}

      {saveMessage && (
        <div
          role="status"
          className="rounded-2xl border border-emerald-500/30 bg-emerald-500/10 p-5 text-emerald-200"
        >
          {saveMessage}
        </div>
      )}

      {result && (
        <section className="space-y-5">
          <div className="flex flex-wrap items-center justify-between gap-3">
            <div>
              <h2 className="text-2xl font-bold text-white">
                {result.count} {result.count === 1 ? "job" : "jobs"} shown
              </h2>
              <p className="mt-1 text-gray-400">
                {result.filters.keyword} - {result.filters.location}
              </p>
            </div>
            <button
              type="button"
              onClick={() => {
                setSavedSearchName(
                  `${targetRole.trim()} · ${country || "Worldwide"}`,
                );
                setShowSaveSearch(true);
              }}
              className="inline-flex items-center gap-2 rounded-xl border border-blue-500 bg-blue-500/10 px-4 py-2 font-semibold text-blue-200 hover:bg-blue-500/20"
            >
              <BellPlus size={18} />
              Save this search
            </button>
          </div>

          {showSaveSearch && (
            <form
              onSubmit={saveCurrentSearch}
              className="flex flex-col gap-3 rounded-2xl border border-blue-500/30 bg-blue-500/10 p-5 sm:flex-row sm:items-end"
            >
              <label className="min-w-0 flex-1">
                <span className="mb-2 block text-sm font-semibold text-blue-100">
                  Search name
                </span>
                <input
                  value={savedSearchName}
                  onChange={(event) => setSavedSearchName(event.target.value)}
                  required
                  maxLength={120}
                  className="w-full rounded-xl border border-blue-400/40 bg-gray-950 px-4 py-3 text-white outline-none focus:border-blue-400"
                />
              </label>
              <button
                type="button"
                onClick={() => setShowSaveSearch(false)}
                className="rounded-xl border border-gray-600 px-4 py-3 font-semibold text-gray-200 hover:bg-gray-800"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={savingSearch}
                className="rounded-xl bg-blue-600 px-5 py-3 font-semibold text-white hover:bg-blue-700 disabled:cursor-wait disabled:opacity-60"
              >
                {savingSearch ? "Saving..." : "Save search"}
              </button>
            </form>
          )}

          {result.providers?.length > 0 && (
            <div className="rounded-2xl border border-gray-800 bg-gray-900 p-5">
              <p className="text-sm font-semibold text-gray-300">Job sources</p>
              <div className="mt-3 flex flex-wrap gap-2">
                {result.providers.map((provider) => (
                  <ProviderStatus key={provider.name} provider={provider} />
                ))}
              </div>
            </div>
          )}

          {result.jobs.length === 0 ? (
            <div className="rounded-2xl border border-gray-800 bg-gray-900 p-8 text-center text-gray-300">
              No matching jobs were found. Try a broader role or location.
            </div>
          ) : (
            <div className="grid gap-5 xl:grid-cols-2">
              {result.jobs.map((job, index) => (
                <JobCard
                  key={`${job.source}-${job.title}-${index}`}
                  job={job}
                  onViewDetails={() => setSelectedJob(job)}
                  isSaved={Boolean(getSavedJob(job))}
                  saving={savingJobIdentity === jobIdentity(job)}
                  onToggleSaved={() => toggleSavedJob(job)}
                />
              ))}
            </div>
          )}

          <div className="flex items-center justify-center gap-4">
            <button
              type="button"
              disabled={loading || result.page <= 1}
              onClick={() => executeSearch(result.page - 1)}
              className="rounded-xl border border-gray-700 bg-gray-900 px-5 py-3 font-semibold text-white hover:border-blue-500 disabled:cursor-not-allowed disabled:opacity-40"
            >
              Previous
            </button>
            <span className="text-sm font-medium text-gray-400">
              Page {result.page}
            </span>
            <button
              type="button"
              disabled={loading || !result.has_more}
              onClick={() => executeSearch(result.page + 1)}
              className="rounded-xl border border-gray-700 bg-gray-900 px-5 py-3 font-semibold text-white hover:border-blue-500 disabled:cursor-not-allowed disabled:opacity-40"
            >
              Next
            </button>
          </div>
        </section>
      )}

      {selectedJob && (
        <JobDetailsDialog
          job={selectedJob}
          onClose={() => setSelectedJob(null)}
          isSaved={Boolean(getSavedJob(selectedJob))}
          saving={savingJobIdentity === jobIdentity(selectedJob)}
          onToggleSaved={() => toggleSavedJob(selectedJob)}
        />
      )}
    </div>
  );
}


function ProviderStatus({ provider }) {
  const styles = {
    active: "border-emerald-500/30 bg-emerald-500/10 text-emerald-300",
    no_results: "border-gray-700 bg-gray-800 text-gray-400",
    not_configured: "border-amber-500/30 bg-amber-500/10 text-amber-300",
    unavailable: "border-red-500/30 bg-red-500/10 text-red-300",
  };
  const labels = {
    active: `${provider.count} found`,
    no_results: "No matches",
    not_configured: "Not configured",
    unavailable: "Temporarily unavailable",
  };

  return (
    <a href={provider.homepage} target="_blank" rel="noreferrer" className={`rounded-full border px-3 py-1 text-xs font-medium ${styles[provider.status] || styles.no_results}`}>
      {provider.name}: {labels[provider.status] || "Unknown"}
    </a>
  );
}


function JobCard({
  job,
  onViewDetails,
  isSaved,
  saving,
  onToggleSaved,
}) {
  const score = job.analysis?.match_score;

  return (
    <article className="rounded-2xl border border-gray-800 bg-gray-900 p-6 shadow-lg">
      <div className="flex items-start justify-between gap-4">
        <div>
          <h3 className="text-xl font-bold text-white">{job.title || "Untitled role"}</h3>
        </div>

        {Number.isFinite(Number(score)) && (
          <div className="rounded-xl bg-blue-600/20 px-3 py-2 text-lg font-bold text-blue-300">
            {Number(score)}%
          </div>
        )}
      </div>

      <div className="mt-4 flex flex-wrap gap-4 text-sm text-gray-400">
        <span className="flex items-center gap-2">
          <Building2 size={17} />
          {job.company || "Company not listed"}
        </span>
        <span className="flex items-center gap-2">
          <MapPin size={17} />
          {job.location || "Location not listed"}
        </span>
        {job.job_type && (
          <span className="rounded-full bg-gray-800 px-3 py-1 text-gray-300">
            {job.job_type}
          </span>
        )}
        {job.salary && (
          <span className="rounded-full bg-emerald-500/10 px-3 py-1 text-emerald-300">
            {job.salary}
          </span>
        )}
      </div>

      {job.analysis?.recommendation && (
        <p className="mt-5 line-clamp-4 text-sm leading-6 text-gray-300">
          {job.analysis.recommendation}
        </p>
      )}

      <div className="mt-6 flex flex-wrap gap-2">
        <button
          type="button"
          onClick={onViewDetails}
          className="inline-flex items-center gap-2 rounded-lg bg-blue-600 px-4 py-2 font-semibold text-white transition hover:bg-blue-700"
        >
          View details
        </button>
        <button
          type="button"
          aria-pressed={isSaved}
          disabled={saving}
          onClick={onToggleSaved}
          className="inline-flex items-center gap-2 rounded-lg border border-gray-700 px-4 py-2 font-semibold text-gray-200 transition hover:border-blue-500 hover:text-white disabled:cursor-wait disabled:opacity-60"
        >
          {isSaved ? <BookmarkCheck size={18} /> : <Bookmark size={18} />}
          {saving ? "Updating..." : isSaved ? "Saved" : "Save job"}
        </button>
      </div>
      <div className="mt-4">
        <ProviderAttribution job={job} />
      </div>
    </article>
  );
}


function JobDetailsDialog({
  job,
  onClose,
  isSaved,
  saving,
  onToggleSaved,
}) {
  const score = job.analysis?.match_score;
  const fallbackDescription = job.description?.trim()
    || "This provider did not include a full description. Review the original listing before applying.";
  const [description, setDescription] = useState(fallbackDescription);
  const [descriptionLoading, setDescriptionLoading] = useState(false);
  const [descriptionEnriched, setDescriptionEnriched] = useState(false);
  const [showApplyAssistant, setShowApplyAssistant] = useState(false);
  const descriptionLooksPartial = (
    !job.description?.trim()
    || /(?:\.\.\.|…)$/.test(job.description.trim())
    || ["Jooble", "Adzuna"].includes(job.source)
  );

  useEffect(() => {
    let cancelled = false;
    setDescription(fallbackDescription);
    setDescriptionEnriched(false);

    if (!job.title || !descriptionLooksPartial) {
      setDescriptionLoading(false);
      return undefined;
    }

    setDescriptionLoading(true);
    api.post("/jobs/description", {
      title: job.title,
      company: job.company || "",
      location: job.location || "",
      listing_url: job.listing_url || null,
    }).then((response) => {
      if (cancelled || !response.data.enriched || !response.data.description) return;
      setDescription(response.data.description);
      setDescriptionEnriched(true);
    }).catch(() => {
      // Keep the provider excerpt when no trusted enrichment source is available.
    }).finally(() => {
      if (!cancelled) setDescriptionLoading(false);
    });

    return () => {
      cancelled = true;
    };
  }, [descriptionLooksPartial, fallbackDescription, job]);

  useEffect(() => {
    setShowApplyAssistant(false);
  }, [job]);

  useEffect(() => {
    const previousOverflow = document.body.style.overflow;
    document.body.style.overflow = "hidden";
    function closeOnEscape(event) {
      if (event.key === "Escape") {
        onClose();
      }
    }

    document.addEventListener("keydown", closeOnEscape);
    return () => {
      document.body.style.overflow = previousOverflow;
      document.removeEventListener("keydown", closeOnEscape);
    };
  }, [onClose]);

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/60 p-4 backdrop-blur-sm"
      role="presentation"
      onMouseDown={(event) => {
        if (event.target === event.currentTarget) onClose();
      }}
    >
      <section
        role="dialog"
        aria-modal="true"
        aria-labelledby="job-details-title"
        className="max-h-[90vh] w-full max-w-3xl overflow-y-auto rounded-3xl border border-slate-200 bg-white shadow-2xl"
      >
        <div className="sticky top-0 flex items-start justify-between gap-4 border-b border-slate-200 bg-white p-6">
          <div>
            <h2 id="job-details-title" className="text-2xl font-bold text-slate-950">
              {job.title || "Untitled role"}
            </h2>
            <p className="mt-2 text-slate-600">
              {job.company || "Company not listed"} · {job.location || "Location not listed"}
            </p>
          </div>
          <button
            type="button"
            onClick={onClose}
            aria-label="Close job details"
            className="rounded-full border border-slate-200 p-2 text-slate-600 transition hover:bg-slate-100 hover:text-slate-950"
          >
            <X size={20} />
          </button>
        </div>

        <div className="space-y-7 p-6">
          <div className="flex flex-wrap gap-3 text-sm">
            {Number.isFinite(Number(score)) && (
              <span className="rounded-full bg-blue-100 px-3 py-1 font-semibold text-blue-800">
                {Number(score)}% match
              </span>
            )}
            {job.job_type && (
              <span className="rounded-full bg-slate-100 px-3 py-1 text-slate-700">{job.job_type}</span>
            )}
            {job.salary && (
              <span className="rounded-full bg-emerald-100 px-3 py-1 text-emerald-800">{job.salary}</span>
            )}
            {job.updated && (
              <span className="rounded-full bg-slate-100 px-3 py-1 text-slate-700">Posted {job.updated}</span>
            )}
          </div>

          <div>
            <div className="flex flex-wrap items-center justify-between gap-3">
              <h3 className="text-lg font-bold text-slate-950">
                {descriptionLooksPartial && !descriptionEnriched
                  ? "Job description preview"
                  : "Job description"}
              </h3>
              {descriptionLoading && (
                <span className="text-xs font-medium text-blue-700" aria-live="polite">
                  Loading complete description...
                </span>
              )}
            </div>
            <p className="mt-3 whitespace-pre-line text-sm leading-7 text-slate-700">{description}</p>
            {!descriptionLoading && descriptionLooksPartial && !descriptionEnriched && (
              <p className="mt-3 text-xs text-amber-700">
                A complete description is not available from a supported employer source.
              </p>
            )}
          </div>

          {job.analysis?.recommendation && (
            <div className="rounded-2xl border border-blue-200 bg-blue-50 p-5">
              <h3 className="font-bold text-blue-950">Why this may fit you</h3>
              <p className="mt-2 text-sm leading-6 text-blue-900">{job.analysis.recommendation}</p>
            </div>
          )}

          {showApplyAssistant && (
            <ApplyAssistant
              job={job}
              onCancel={() => setShowApplyAssistant(false)}
            />
          )}

          <div className="flex flex-wrap items-center justify-between gap-4 border-t border-slate-200 pt-6">
            <ProviderAttribution job={job} />
            <div className="flex flex-wrap gap-2">
              <button
                type="button"
                aria-pressed={isSaved}
                disabled={saving}
                onClick={onToggleSaved}
                className="inline-flex items-center gap-2 rounded-xl border border-slate-300 px-5 py-3 font-semibold text-slate-700 transition hover:bg-slate-50 disabled:cursor-wait disabled:opacity-60"
              >
                {isSaved ? <BookmarkCheck size={18} /> : <Bookmark size={18} />}
                {saving ? "Updating..." : isSaved ? "Saved" : "Save job"}
              </button>
              {job.listing_url || job.apply_url ? (
                <button
                  type="button"
                  onClick={() => setShowApplyAssistant(true)}
                  className="inline-flex items-center gap-2 rounded-xl bg-blue-600 px-5 py-3 font-semibold text-white transition hover:bg-blue-700"
                >
                  {showApplyAssistant ? "Application package open" : "Prepare application"}
                  <ExternalLink size={17} />
                </button>
              ) : (
                <span className="text-sm text-slate-500">Application link unavailable</span>
              )}
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}

function ProviderAttribution({ job }) {
  if (job.source === "Adzuna") {
    return (
      <a
        href={job.source_homepage || "https://www.adzuna.com/"}
        target="_blank"
        rel="noreferrer"
        className="inline-flex min-h-[23px] min-w-[116px] items-center gap-1 text-xs text-slate-500"
        aria-label="Jobs by Adzuna"
      >
        <span>Jobs by</span>
        <img
          src="https://upload.wikimedia.org/wikipedia/commons/5/51/Adzuna_Logo.png"
          alt="Adzuna"
          className="h-[23px] w-auto"
        />
      </a>
    );
  }

  return (
    <p className="text-xs text-slate-500">
      Supplied by{" "}
      {job.source_homepage ? (
        <a
          href={job.source_homepage}
          target="_blank"
          rel="noreferrer"
          className="underline hover:text-slate-700"
        >
          {job.source || "the job provider"}
        </a>
      ) : (
        job.source || "the job provider"
      )}
      . Verify details with the provider before applying.
    </p>
  );
}


export default Jobs;
