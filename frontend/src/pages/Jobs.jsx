import { useEffect, useState } from "react";
import {
  BriefcaseBusiness,
  Building2,
  ExternalLink,
  MapPin,
  Search,
  Sparkles,
} from "lucide-react";

import api from "../services/api";
import { getProfile } from "../services/api";
import { countries } from "../data/countries";
import { buildLinkedInJobSearchUrl } from "../utils/linkedinJobSearch";


function Jobs() {
  const [targetRole, setTargetRole] = useState("");
  const [country, setCountry] = useState("");
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

  useEffect(() => {
    async function loadProfileDefaults() {
      try {
        const response = await getProfile();
        setTargetRole(response.data.target_role || "");
        setCountry(response.data.country || "");
        setCity(response.data.city || "");
        setWorkMode(response.data.preferred_work_mode || "");
      } catch {
        // A profile is optional; the user can enter search filters directly.
      }
    }

    loadProfileDefaults();
  }, []);

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
          per_page: 20,
        },
      });

      setResult(response.data);
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

  function searchLinkedIn() {
    const url = buildLinkedInJobSearchUrl({
      targetRole,
      country,
      city,
      industry,
      workMode,
      employmentType,
      postedWithinDays,
    });

    if (!url) {
      setError("Enter a target role before searching LinkedIn.");
      return;
    }

    setError("");
    window.open(url, "_blank", "noopener,noreferrer");
  }

  return (
    <div className="space-y-8">
      <section className="rounded-3xl bg-gradient-to-r from-blue-600 to-indigo-700 p-8 text-white shadow-xl">
        <div className="flex items-center gap-3">
          <Sparkles size={30} />
          <h1 className="text-4xl font-bold">Matched Jobs</h1>
        </div>
        <p className="mt-3 max-w-3xl text-lg text-blue-100">
          Search opportunities directly. Your profile and latest resume skills improve ranking when available.
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
              onChange={(event) => setCountry(event.target.value)}
              className="w-full rounded-xl border border-gray-700 bg-gray-950 px-4 py-3 text-white outline-none focus:border-blue-500"
            >
              <option value="">Any country</option>
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
              placeholder="Queretaro"
              className="w-full rounded-xl border border-gray-700 bg-gray-950 px-4 py-3 text-white outline-none focus:border-blue-500"
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

        <div className="mt-5 flex flex-wrap items-end justify-between gap-4">
          <div>
            <p className="text-sm text-gray-500">
              Profile values are prefilled and can be adjusted for this search.
            </p>
            <p className="mt-1 text-xs text-gray-400">
              LinkedIn searches open on LinkedIn and are subject to its availability and terms.
            </p>
          </div>
          <div className="flex flex-wrap gap-3">
            <button
              type="button"
              onClick={searchLinkedIn}
              className="flex items-center justify-center gap-2 rounded-xl border border-blue-600 bg-white px-6 py-3 font-semibold text-blue-700 transition hover:bg-blue-50"
            >
              <BriefcaseBusiness size={19} />
              Search LinkedIn
              <ExternalLink size={16} />
            </button>
            <button
              type="submit"
              disabled={loading}
              className="flex items-center justify-center gap-2 rounded-xl bg-blue-600 px-6 py-3 font-semibold text-white transition hover:bg-blue-700 disabled:cursor-wait disabled:opacity-60"
            >
              <Search size={19} />
              {loading ? "Matching..." : "Find My Jobs"}
            </button>
          </div>
        </div>
      </form>

      {error && (
        <div role="alert" className="rounded-2xl border border-red-500/30 bg-red-500/10 p-5 text-red-200">
          {error}
        </div>
      )}

      {result && (
        <section className="space-y-5">
          <div className="flex flex-wrap items-center justify-between gap-3">
            <div>
              <h2 className="text-2xl font-bold text-white">
                {result.count} matched {result.count === 1 ? "job" : "jobs"}
              </h2>
              <p className="mt-1 text-gray-400">
                {result.filters.keyword} - {result.filters.location}
              </p>
            </div>
          </div>

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
                <JobCard key={`${job.source}-${job.title}-${index}`} job={job} />
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


function JobCard({ job }) {
  const score = job.analysis?.match_score;
  const url = job.listing_url;

  return (
    <article className="rounded-2xl border border-gray-800 bg-gray-900 p-6 shadow-lg">
      <div className="flex items-start justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 text-blue-400">
            <BriefcaseBusiness size={20} />
            <span className="text-sm font-semibold">{job.source || "Job listing"}</span>
          </div>
          <h3 className="mt-3 text-xl font-bold text-white">{job.title || "Untitled role"}</h3>
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

      {url && (
        <a
          href={url}
          target="_blank"
          rel="noreferrer"
          className="mt-6 inline-flex items-center gap-2 font-semibold text-blue-400 hover:text-blue-300"
        >
          View on {job.source || "provider"}
          <ExternalLink size={17} />
        </a>
      )}
      {job.source_homepage && (
        <p className="mt-4 text-xs text-gray-500">
          Listing supplied by <a href={job.source_homepage} target="_blank" rel="noreferrer" className="underline hover:text-gray-300">{job.source}</a>. Verify details on the provider site before applying.
        </p>
      )}
    </article>
  );
}


export default Jobs;
