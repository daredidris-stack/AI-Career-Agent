import { useEffect, useMemo, useState } from "react";
import {
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
  const [resumeId, setResumeId] = useState("");
  const [coverLetterId, setCoverLetterId] = useState("");
  const [reviewConfirmed, setReviewConfirmed] = useState(false);
  const [manualSubmissionConfirmed, setManualSubmissionConfirmed] = useState(false);
  const [preparedApplication, setPreparedApplication] = useState(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    let cancelled = false;

    api.get("/documents").then((response) => {
      if (cancelled) return;
      const available = response.data || [];
      const preferredResume = available.find(
        (document) => document.kind === "tailored_resume",
      ) || available.find((document) => document.kind === "resume");
      setDocuments(available);
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

  async function prepareApplication(event) {
    event.preventDefault();
    setSaving(true);
    setError("");
    try {
      const sourceJobId = job.source_job_id ?? job.id ?? null;
      const response = await api.post("/applications/prepare", {
        company: job.company || "Company not listed",
        role: job.title || "Untitled role",
        job_url: job.listing_url,
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
