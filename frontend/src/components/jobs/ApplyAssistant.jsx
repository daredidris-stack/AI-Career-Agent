import { useEffect, useMemo, useState } from "react";
import {
  Check,
  Clipboard,
  Download,
  ExternalLink,
  FileCheck2,
  ShieldCheck,
} from "lucide-react";
import { Link } from "react-router-dom";

import api from "../../services/api";


function documentLabel(document) {
  if (!document) return "";
  const kind = document.kind === "tailored_resume"
    ? "Tailored resume"
    : document.kind === "cover_letter"
      ? "Cover letter"
      : "Resume";
  return `${document.title} · ${kind}`;
}


export default function ApplyAssistant({ job, onCancel }) {
  const [documents, setDocuments] = useState([]);
  const [profile, setProfile] = useState(null);
  const [user, setUser] = useState(null);
  const [resumeId, setResumeId] = useState("");
  const [coverLetterId, setCoverLetterId] = useState("");
  const [reviewConfirmed, setReviewConfirmed] = useState(false);
  const [manualSubmissionConfirmed, setManualSubmissionConfirmed] = useState(false);
  const [preparedApplication, setPreparedApplication] = useState(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");
  const [copiedField, setCopiedField] = useState("");

  useEffect(() => {
    let cancelled = false;

    Promise.all([
      api.get("/documents"),
      api.get("/profile").catch(() => ({ data: null })),
      api.get("/users/me"),
    ]).then(([documentResponse, profileResponse, userResponse]) => {
      if (cancelled) return;
      const available = documentResponse.data || [];
      const preferredResume = available.find(
        (document) => document.kind === "tailored_resume",
      ) || available.find((document) => document.kind === "resume");
      setDocuments(available);
      setProfile(profileResponse.data);
      setUser(userResponse.data);
      setResumeId(preferredResume ? String(preferredResume.id) : "");
    }).catch((requestError) => {
      if (!cancelled) {
        setError(
          requestError.response?.data?.detail
          || "Your documents could not be loaded.",
        );
      }
    }).finally(() => {
      if (!cancelled) setLoading(false);
    });

    return () => {
      cancelled = true;
    };
  }, []);

  const resumes = useMemo(
    () => documents.filter(
      (document) => ["resume", "tailored_resume"].includes(document.kind),
    ),
    [documents],
  );
  const coverLetters = useMemo(
    () => documents.filter((document) => document.kind === "cover_letter"),
    [documents],
  );
  const selectedResume = resumes.find(
    (document) => String(document.id) === resumeId,
  );
  const selectedCoverLetter = coverLetters.find(
    (document) => String(document.id) === coverLetterId,
  );
  const applicationFields = useMemo(() => {
    const fullName = [user?.first_name, user?.last_name]
      .filter(Boolean)
      .join(" ");
    const location = [profile?.city, profile?.state, profile?.country]
      .filter(Boolean)
      .join(", ");
    return [
      ["Full name", fullName],
      ["Email", user?.email],
      ["Phone", profile?.phone],
      ["Location", location],
      ["Current role", profile?.current_role],
      ["Target role", profile?.target_role],
      [
        "Years of experience",
        profile?.years_experience !== null
          && profile?.years_experience !== undefined
          && Number.isFinite(Number(profile.years_experience))
          ? String(profile.years_experience)
          : "",
      ],
      ["LinkedIn", profile?.linkedin],
      ["GitHub", profile?.github],
      ["Portfolio", profile?.portfolio],
    ].filter(([, value]) => value);
  }, [profile, user]);

  async function copyValue(label, value) {
    try {
      await navigator.clipboard.writeText(value);
      setCopiedField(label);
      window.setTimeout(() => setCopiedField(""), 1800);
    } catch {
      setError("Your browser did not allow copying this information.");
    }
  }

  async function copyAllFields() {
    const content = applicationFields
      .map(([label, value]) => `${label}: ${value}`)
      .join("\n");
    await copyValue("all", content);
  }

  async function prepareApplication(event) {
    event.preventDefault();
    setSaving(true);
    setError("");
    try {
      const sourceJobId = job.source_job_id ?? job.id ?? null;
      const response = await api.post("/applications/prepare", {
        company: job.company || "Company not listed",
        role: job.title || "Untitled role",
        job_url: job.listing_url || job.apply_url,
        location: job.location || null,
        source: job.source || null,
        source_job_id: sourceJobId === null ? null : String(sourceJobId),
        resume_document_id: Number(resumeId),
        cover_letter_document_id: coverLetterId
          ? Number(coverLetterId)
          : null,
        review_confirmed: reviewConfirmed,
        manual_submission_confirmed: manualSubmissionConfirmed,
      });
      setPreparedApplication(response.data);
    } catch (requestError) {
      setError(
        requestError.response?.data?.detail
        || "The application package could not be prepared.",
      );
    } finally {
      setSaving(false);
    }
  }

  async function downloadDocument(document, format) {
    try {
      const response = await api.get(`/documents/${document.id}/export`, {
        params: { format },
        responseType: "blob",
      });
      const url = URL.createObjectURL(response.data);
      const link = window.document.createElement("a");
      link.href = url;
      link.download = `${document.title.replace(/[^a-z0-9]+/gi, "-").toLowerCase() || "document"}.${format}`;
      link.click();
      URL.revokeObjectURL(url);
    } catch (requestError) {
      setError(
        requestError.response?.data?.detail
        || "The document could not be downloaded.",
      );
    }
  }

  if (loading) {
    return (
      <div className="rounded-2xl border border-blue-200 bg-blue-50 p-5 text-sm text-blue-900">
        Loading your application documents...
      </div>
    );
  }

  if (resumes.length === 0) {
    return (
      <div className="rounded-2xl border border-amber-200 bg-amber-50 p-5">
        <h3 className="font-bold text-amber-950">A resume is required</h3>
        <p className="mt-2 text-sm leading-6 text-amber-900">
          Create or tailor a resume before preparing this application.
        </p>
        <div className="mt-4 flex flex-wrap gap-3">
          <Link to="/resume" className="rounded-lg bg-amber-900 px-4 py-2 text-sm font-semibold text-white">
            Open Resume Studio
          </Link>
          <Link to="/resume-tailor" className="rounded-lg border border-amber-300 px-4 py-2 text-sm font-semibold text-amber-950">
            Tailor a resume
          </Link>
          <button type="button" onClick={onCancel} className="px-3 py-2 text-sm font-semibold text-slate-600">
            Back to job
          </button>
        </div>
      </div>
    );
  }

  if (preparedApplication) {
    return (
      <div className="rounded-2xl border border-emerald-200 bg-emerald-50 p-5">
        <div className="flex items-start gap-3">
          <FileCheck2 className="mt-0.5 text-emerald-700" size={22} />
          <div>
            <h3 className="font-bold text-emerald-950">
              Application package saved
            </h3>
            <p className="mt-1 text-sm leading-6 text-emerald-900">
              This opportunity is tracked as {preparedApplication.status}.
              NextHire has not submitted anything to the employer.
            </p>
          </div>
        </div>

        <div className="mt-4 rounded-xl bg-white/70 p-4 text-sm text-slate-700">
          <p><strong>Resume:</strong> {documentLabel(selectedResume)}</p>
          {selectedCoverLetter && (
            <p className="mt-1">
              <strong>Cover letter:</strong> {documentLabel(selectedCoverLetter)}
            </p>
          )}
        </div>

        <div className="mt-4 flex flex-wrap gap-3">
          <a
            href={preparedApplication.job_url}
            target="_blank"
            rel="noreferrer"
            className="inline-flex items-center gap-2 rounded-xl bg-blue-600 px-5 py-3 font-semibold text-white hover:bg-blue-700"
          >
            Continue to listing on {preparedApplication.source || "provider"}
            <ExternalLink size={17} />
          </a>
          <Link
            to="/applications"
            className="rounded-xl border border-emerald-300 px-5 py-3 font-semibold text-emerald-950"
          >
            Open application tracker
          </Link>
        </div>
        <p className="mt-3 text-xs leading-5 text-emerald-900">
          Complete the employer form yourself, then mark the application as
          Applied in the tracker.
        </p>
      </div>
    );
  }

  return (
    <form
      onSubmit={prepareApplication}
      className="rounded-2xl border border-blue-200 bg-blue-50 p-5"
    >
      <div className="flex items-start gap-3">
        <ShieldCheck className="mt-0.5 text-blue-700" size={22} />
        <div>
          <h3 className="font-bold text-blue-950">Review your application package</h3>
          <p className="mt-1 text-sm leading-6 text-blue-900">
            NextHire prepares and tracks your documents. You remain in control
            of the employer form and its final submission.
          </p>
        </div>
      </div>

      {error && (
        <p role="alert" className="mt-4 rounded-lg border border-red-200 bg-red-50 p-3 text-sm text-red-800">
          {error}
        </p>
      )}

      <div className="mt-5 grid gap-4 md:grid-cols-2">
        <label className="block">
          <span className="mb-2 block text-sm font-semibold text-slate-800">
            Resume
          </span>
          <select
            required
            value={resumeId}
            onChange={(event) => setResumeId(event.target.value)}
            className="w-full rounded-xl border border-slate-300 bg-white px-4 py-3 text-slate-950"
          >
            {resumes.map((document) => (
              <option key={document.id} value={document.id}>
                {documentLabel(document)}
              </option>
            ))}
          </select>
        </label>

        <label className="block">
          <span className="mb-2 block text-sm font-semibold text-slate-800">
            Cover letter (optional)
          </span>
          <select
            value={coverLetterId}
            onChange={(event) => setCoverLetterId(event.target.value)}
            className="w-full rounded-xl border border-slate-300 bg-white px-4 py-3 text-slate-950"
          >
            <option value="">No cover letter</option>
            {coverLetters.map((document) => (
              <option key={document.id} value={document.id}>
                {documentLabel(document)}
              </option>
            ))}
          </select>
        </label>
      </div>

      {applicationFields.length > 0 && (
        <section className="mt-5 rounded-xl border border-blue-200 bg-white/80 p-4">
          <div className="flex flex-wrap items-start justify-between gap-3">
            <div>
              <h4 className="font-bold text-slate-950">
                Application information pack
              </h4>
              <p className="mt-1 text-xs leading-5 text-slate-600">
                Copy factual profile fields into the employer form. NextHire
                does not infer work authorization, salary, demographic,
                disability, or other sensitive answers.
              </p>
            </div>
            <button
              type="button"
              onClick={copyAllFields}
              className="inline-flex items-center gap-2 rounded-lg border border-blue-200 px-3 py-2 text-xs font-semibold text-blue-800 hover:bg-blue-50"
            >
              {copiedField === "all"
                ? <Check size={15} />
                : <Clipboard size={15} />}
              {copiedField === "all" ? "Copied" : "Copy all"}
            </button>
          </div>
          <dl className="mt-4 grid gap-2 sm:grid-cols-2">
            {applicationFields.map(([label, value]) => (
              <div
                key={label}
                className="flex items-center justify-between gap-3 rounded-lg bg-slate-50 p-3"
              >
                <div className="min-w-0">
                  <dt className="text-[10px] font-bold uppercase tracking-wide text-slate-500">
                    {label}
                  </dt>
                  <dd className="mt-1 truncate text-sm text-slate-800">
                    {value}
                  </dd>
                </div>
                <button
                  type="button"
                  onClick={() => copyValue(label, value)}
                  aria-label={`Copy ${label}`}
                  className="shrink-0 rounded-lg p-2 text-blue-700 hover:bg-blue-100"
                >
                  {copiedField === label
                    ? <Check size={16} />
                    : <Clipboard size={16} />}
                </button>
              </div>
            ))}
          </dl>
        </section>
      )}

      <div className="mt-4 flex flex-wrap gap-3">
        <button
          type="button"
          onClick={() => downloadDocument(selectedResume, "pdf")}
          className="inline-flex items-center gap-2 rounded-lg border border-blue-200 bg-white px-3 py-2 text-sm font-semibold text-blue-800"
        >
          <Download size={15} /> Resume PDF
        </button>
        {selectedCoverLetter && (
          <button
            type="button"
            onClick={() => downloadDocument(selectedCoverLetter, "pdf")}
            className="inline-flex items-center gap-2 rounded-lg border border-blue-200 bg-white px-3 py-2 text-sm font-semibold text-blue-800"
          >
            <Download size={15} /> Cover letter PDF
          </button>
        )}
      </div>

      <div className="mt-5 space-y-3">
        <label className="flex items-start gap-3 text-sm leading-6 text-slate-800">
          <input
            required
            type="checkbox"
            checked={reviewConfirmed}
            onChange={(event) => setReviewConfirmed(event.target.checked)}
            className="mt-1"
          />
          I reviewed this job and the selected documents for accuracy.
        </label>
        <label className="flex items-start gap-3 text-sm leading-6 text-slate-800">
          <input
            required
            type="checkbox"
            checked={manualSubmissionConfirmed}
            onChange={(event) => setManualSubmissionConfirmed(event.target.checked)}
            className="mt-1"
          />
          I will complete and submit the employer form myself, including all
          work-authorization, sponsorship, salary, and voluntary demographic
          answers.
        </label>
      </div>

      <div className="mt-5 flex flex-wrap justify-end gap-3">
        <button
          type="button"
          onClick={onCancel}
          className="rounded-xl px-4 py-3 font-semibold text-slate-600"
        >
          Cancel
        </button>
        <button
          disabled={saving || !reviewConfirmed || !manualSubmissionConfirmed}
          className="rounded-xl bg-blue-600 px-5 py-3 font-semibold text-white disabled:cursor-not-allowed disabled:opacity-50"
        >
          {saving ? "Saving package..." : "Save reviewed package"}
        </button>
      </div>
    </form>
  );
}
