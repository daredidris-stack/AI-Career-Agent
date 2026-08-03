import { useEffect, useMemo, useState } from "react";
import {
  ArrowLeftRight,
  Download,
  FileText,
  History,
  Pencil,
  Trash2,
  X,
} from "lucide-react";

import api from "../../services/api";


const kindLabels = {
  resume: "Resume",
  tailored_resume: "Tailored resume",
  cover_letter: "Cover letter",
  job_match: "Job match",
};

function readableContent(value) {
  try {
    return JSON.stringify(JSON.parse(value), null, 2);
  } catch {
    return value;
  }
}

function compareContent(previousValue, currentValue) {
  const previous = readableContent(previousValue).split("\n").slice(0, 500);
  const current = readableContent(currentValue).split("\n").slice(0, 500);
  const width = Math.max(previous.length, current.length);
  return Array.from({ length: width }, (_, index) => ({
    previous: previous[index] ?? "",
    current: current[index] ?? "",
    changed: previous[index] !== current[index],
  }));
}


export default function DocumentLibrary({ refreshToken }) {
  const [documents, setDocuments] = useState([]);
  const [editing, setEditing] = useState(null);
  const [structuredResume, setStructuredResume] = useState(null);
  const [versionDocument, setVersionDocument] = useState(null);
  const [versions, setVersions] = useState([]);
  const [compareRevision, setCompareRevision] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    loadDocuments();
  }, [refreshToken]);

  useEffect(() => {
    if (!editing && !versionDocument) return undefined;
    const previousOverflow = document.body.style.overflow;
    document.body.style.overflow = "hidden";
    function closeOnEscape(event) {
      if (event.key !== "Escape") return;
      setEditing(null);
      setVersionDocument(null);
      setCompareRevision(null);
    }
    document.addEventListener("keydown", closeOnEscape);
    return () => {
      document.body.style.overflow = previousOverflow;
      document.removeEventListener("keydown", closeOnEscape);
    };
  }, [editing, versionDocument]);

  async function loadDocuments() {
    try {
      const response = await api.get("/documents");
      setDocuments(response.data);
      setError("");
    } catch {
      setError("Your document library could not be loaded.");
    }
  }

  async function saveDocument(event) {
    event.preventDefault();
    await api.put(`/documents/${editing.id}`, {
      title: editing.title,
      content: editing.content,
    });
    setEditing(null);
    await loadDocuments();
  }

  async function createResume() {
    const content = JSON.stringify({
      template_id: "ats-professional",
      full_name: "",
      contact_line: "",
      target_role: "",
      summary: "",
      skills: [],
      experience: [],
      education: [],
      certifications: [],
      projects: [],
    }, null, 2);
    const response = await api.post("/documents", {
      kind: "resume",
      title: "Untitled Resume",
      content,
    });
    await loadDocuments();
    beginEdit(response.data);
  }

  function beginEdit(document) {
    const draft = { ...document };
    setEditing(draft);
    try {
      const parsed = JSON.parse(document.content);
      if (parsed && typeof parsed === "object" && Array.isArray(parsed.skills)) {
        setStructuredResume({
          template_id: String(parsed.template_id || "ats-professional"),
          full_name: String(parsed.full_name || ""),
          contact_line: String(parsed.contact_line || ""),
          target_role: String(parsed.target_role || ""),
          summary: String(parsed.summary || ""),
          skills: parsed.skills.map(String),
          experience: Array.isArray(parsed.experience) ? parsed.experience : [],
          education: Array.isArray(parsed.education) ? parsed.education.map(String) : [],
          certifications: Array.isArray(parsed.certifications) ? parsed.certifications.map(String) : [],
          projects: Array.isArray(parsed.projects) ? parsed.projects.map(String) : [],
        });
        return;
      }
    } catch {
      // Imported resumes remain available in the raw text editor.
    }
    setStructuredResume(null);
  }

  function updateStructured(field, value) {
    const next = { ...structuredResume, [field]: value };
    setStructuredResume(next);
    setEditing({ ...editing, content: JSON.stringify(next, null, 2) });
  }

  function experienceToText(experience) {
    return experience.map((entry) => {
      if (entry && typeof entry === "object") {
        const heading = [entry.role, entry.company, entry.dates]
          .filter(Boolean)
          .join(" | ");
        const bullets = Array.isArray(entry.bullets)
          ? entry.bullets.map((value) => `- ${value}`).join("\n")
          : "";
        return [heading, bullets].filter(Boolean).join("\n");
      }
      return String(entry || "");
    }).filter(Boolean).join("\n\n");
  }

  function textToExperience(value) {
    return value.split(/\n\s*\n/).map((block) => {
      const lines = block.split("\n").map((line) => line.trim()).filter(Boolean);
      const heading = lines[0] || "";
      const parts = heading.split("|").map((part) => part.trim());
      return {
        role: parts[0] || "",
        company: parts[1] || "",
        dates: parts[2] || "",
        bullets: lines.slice(1).map((line) => line.replace(/^-\s*/, "")),
      };
    }).filter((entry) => entry.role || entry.company || entry.dates || entry.bullets.length);
  }

  async function deleteDocument(document) {
    if (!window.confirm(`Delete “${document.title}”?`)) return;
    await api.delete(`/documents/${document.id}`);
    await loadDocuments();
  }

  async function showVersions(document) {
    const response = await api.get(`/documents/${document.id}/versions`);
    setVersionDocument(document);
    setVersions(response.data);
    setCompareRevision(null);
  }

  async function restoreVersion(revision) {
    await api.post(
      `/documents/${versionDocument.id}/versions/${revision.id}/restore`,
    );
    setVersionDocument(null);
    setVersions([]);
    setCompareRevision(null);
    await loadDocuments();
  }

  async function downloadDocument(document, format) {
    const response = await api.get(`/documents/${document.id}/export`, {
      params: { format },
      responseType: "blob",
    });
    const blob = response.data;
    const url = URL.createObjectURL(blob);
    const link = window.document.createElement("a");
    link.href = url;
    link.download = `${document.title.replace(/[^a-z0-9]+/gi, "-").toLowerCase() || "document"}.${format}`;
    link.click();
    URL.revokeObjectURL(url);
  }

  const comparison = useMemo(
    () => compareRevision && versionDocument
      ? compareContent(compareRevision.content, versionDocument.content)
      : [],
    [compareRevision, versionDocument],
  );
  const changedLineCount = comparison.filter((line) => line.changed).length;

  return (
    <section className="rounded-2xl border border-gray-800 bg-gray-900 p-6">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
        <h2 className="text-2xl font-bold text-white">Document library</h2>
        <p className="mt-1 text-sm text-gray-400">Your resumes and generated career documents are saved privately.</p>
        </div>
        <button type="button" onClick={createResume} className="rounded-xl bg-blue-600 px-4 py-2 font-semibold text-white hover:bg-blue-700">New resume</button>
      </div>

      {error && <p role="alert" className="mt-4 text-red-300">{error}</p>}
      {!error && documents.length === 0 && <p className="mt-6 text-gray-400">Analyze or tailor a resume to create your first saved document.</p>}

      <div className="mt-6 grid gap-4 lg:grid-cols-2">
        {documents.map((document) => (
          <article key={document.id} className="rounded-xl border border-gray-700 bg-gray-950 p-5">
            <div className="flex items-start justify-between gap-4">
              <div>
                <p className="text-xs font-semibold uppercase tracking-wide text-blue-400">{kindLabels[document.kind] || document.kind}</p>
                <h3 className="mt-2 font-semibold text-white">{document.title}</h3>
                <p className="mt-1 text-xs text-gray-500">Updated {new Date(document.updated_at).toLocaleString()}</p>
              </div>
              <FileText className="text-gray-600" />
            </div>
            <p className="mt-4 line-clamp-3 whitespace-pre-wrap text-sm text-gray-400">{document.content}</p>
            <div className="mt-5 flex gap-4 text-sm">
              <button type="button" onClick={() => beginEdit(document)} className="flex items-center gap-1 text-blue-400"><Pencil size={15} /> Edit</button>
              <button type="button" onClick={() => showVersions(document)} className="flex items-center gap-1 text-violet-400"><History size={15} /> History</button>
              <button type="button" onClick={() => downloadDocument(document, "pdf")} className="flex items-center gap-1 text-emerald-400"><Download size={15} /> PDF</button>
              <button type="button" onClick={() => downloadDocument(document, "docx")} className="flex items-center gap-1 text-emerald-400"><Download size={15} /> DOCX</button>
              <button type="button" onClick={() => deleteDocument(document)} className="flex items-center gap-1 text-red-400"><Trash2 size={15} /> Delete</button>
            </div>
          </article>
        ))}
      </div>

      {editing && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 p-4" role="presentation">
          <form onSubmit={saveDocument} role="dialog" aria-modal="true" aria-labelledby="edit-document-title" className="max-h-[92vh] w-full max-w-3xl overflow-y-auto rounded-2xl border border-gray-700 bg-gray-900 p-6 shadow-2xl">
            <div className="flex items-center justify-between">
              <h3 id="edit-document-title" className="text-xl font-bold text-white">Edit document</h3>
              <button type="button" onClick={() => setEditing(null)} aria-label="Close"><X className="text-gray-400" /></button>
            </div>
            <input value={editing.title} onChange={(event) => setEditing({ ...editing, title: event.target.value })} required className="mt-5 w-full rounded-xl border border-gray-700 bg-gray-950 px-4 py-3 text-white" />
            {structuredResume ? (
              <div className="mt-4 grid max-h-[60vh] gap-4 overflow-y-auto pr-2">
                <label><span className="mb-1 block text-sm text-gray-300">Full name</span><input value={structuredResume.full_name} onChange={(event) => updateStructured("full_name", event.target.value)} className="w-full rounded-xl border border-gray-700 bg-gray-950 px-4 py-3 text-white" /></label>
                <label><span className="mb-1 block text-sm text-gray-300">Contact line</span><input value={structuredResume.contact_line} onChange={(event) => updateStructured("contact_line", event.target.value)} placeholder="Email | Phone | Location | LinkedIn" className="w-full rounded-xl border border-gray-700 bg-gray-950 px-4 py-3 text-white" /></label>
                <label><span className="mb-1 block text-sm text-gray-300">Target role</span><input value={structuredResume.target_role} onChange={(event) => updateStructured("target_role", event.target.value)} className="w-full rounded-xl border border-gray-700 bg-gray-950 px-4 py-3 text-white" /></label>
                <label><span className="mb-1 block text-sm text-gray-300">Professional summary</span><textarea rows={4} value={structuredResume.summary} onChange={(event) => updateStructured("summary", event.target.value)} className="w-full rounded-xl border border-gray-700 bg-gray-950 px-4 py-3 text-white" /></label>
                <label><span className="mb-1 block text-sm text-gray-300">Skills (comma separated)</span><input value={structuredResume.skills.join(", ")} onChange={(event) => updateStructured("skills", event.target.value.split(",").map((value) => value.trim()).filter(Boolean))} className="w-full rounded-xl border border-gray-700 bg-gray-950 px-4 py-3 text-white" /></label>
                <label><span className="mb-1 block text-sm text-gray-300">Experience (role | company | dates, then bullets)</span><textarea rows={9} value={experienceToText(structuredResume.experience)} onChange={(event) => updateStructured("experience", textToExperience(event.target.value))} className="w-full rounded-xl border border-gray-700 bg-gray-950 px-4 py-3 text-white" /></label>
                <label><span className="mb-1 block text-sm text-gray-300">Education (one entry per line)</span><textarea rows={5} value={structuredResume.education.join("\n")} onChange={(event) => updateStructured("education", event.target.value.split("\n"))} className="w-full rounded-xl border border-gray-700 bg-gray-950 px-4 py-3 text-white" /></label>
                <label><span className="mb-1 block text-sm text-gray-300">Certifications (one entry per line)</span><textarea rows={4} value={structuredResume.certifications.join("\n")} onChange={(event) => updateStructured("certifications", event.target.value.split("\n").filter(Boolean))} className="w-full rounded-xl border border-gray-700 bg-gray-950 px-4 py-3 text-white" /></label>
                <label><span className="mb-1 block text-sm text-gray-300">Projects (one entry per line)</span><textarea rows={4} value={structuredResume.projects.join("\n")} onChange={(event) => updateStructured("projects", event.target.value.split("\n").filter(Boolean))} className="w-full rounded-xl border border-gray-700 bg-gray-950 px-4 py-3 text-white" /></label>
              </div>
            ) : (
              <textarea rows={18} value={editing.content} onChange={(event) => setEditing({ ...editing, content: event.target.value })} required className="mt-4 w-full rounded-xl border border-gray-700 bg-gray-950 px-4 py-3 font-mono text-sm text-white" />
            )}
            <div className="mt-4 flex justify-end gap-3"><button type="button" onClick={() => setEditing(null)} className="px-4 py-2 text-gray-300">Cancel</button><button className="rounded-xl bg-blue-600 px-5 py-2 font-semibold text-white">Save changes</button></div>
          </form>
        </div>
      )}

      {versionDocument && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 p-4" role="presentation">
          <section role="dialog" aria-modal="true" aria-labelledby="version-history-title" className="max-h-[88vh] w-full max-w-2xl overflow-y-auto rounded-2xl border border-gray-700 bg-gray-900 p-6 shadow-2xl">
            <div className="flex items-center justify-between"><div><h3 id="version-history-title" className="text-xl font-bold text-white">Version history</h3><p className="mt-1 text-sm text-gray-400">{versionDocument.title}</p></div><button type="button" onClick={() => setVersionDocument(null)} aria-label="Close"><X className="text-gray-400" /></button></div>
            {compareRevision && (
              <section className="mt-6 rounded-xl border border-blue-500/40 bg-blue-500/10 p-4">
                <div className="flex flex-wrap items-start justify-between gap-3">
                  <div>
                    <h4 className="flex items-center gap-2 font-bold text-white">
                      <ArrowLeftRight size={18} />
                      Compare with current version
                    </h4>
                    <p className="mt-1 text-xs text-blue-200">
                      {new Date(compareRevision.created_at).toLocaleString()} ·{" "}
                      {changedLineCount} changed {changedLineCount === 1 ? "line" : "lines"}
                    </p>
                  </div>
                  <button
                    type="button"
                    onClick={() => setCompareRevision(null)}
                    className="text-sm font-semibold text-blue-300 hover:text-white"
                  >
                    Close comparison
                  </button>
                </div>
                <div className="mt-4 overflow-x-auto">
                  <div className="grid min-w-[760px] grid-cols-2 gap-px overflow-hidden rounded-lg border border-gray-700 bg-gray-700">
                    <div className="bg-gray-900 px-4 py-2 text-xs font-bold uppercase tracking-wide text-gray-300">
                      Earlier version
                    </div>
                    <div className="bg-gray-900 px-4 py-2 text-xs font-bold uppercase tracking-wide text-gray-300">
                      Current version
                    </div>
                    {comparison.map((line, index) => (
                      <div key={`previous-${index}`} className={`contents ${line.changed ? "text-amber-100" : "text-gray-400"}`}>
                        <pre className={`whitespace-pre-wrap break-words px-3 py-1 text-xs ${line.changed ? "bg-amber-950/50" : "bg-gray-950"}`}>
                          {line.previous || " "}
                        </pre>
                        <pre className={`whitespace-pre-wrap break-words px-3 py-1 text-xs ${line.changed ? "bg-emerald-950/40" : "bg-gray-950"}`}>
                          {line.current || " "}
                        </pre>
                      </div>
                    ))}
                  </div>
                </div>
              </section>
            )}
            {versions.length === 0 ? <p className="mt-6 text-gray-400">No earlier versions yet.</p> : <div className="mt-6 space-y-3">{versions.map((revision) => <article key={revision.id} className="rounded-xl border border-gray-700 bg-gray-950 p-4"><p className="font-medium text-white">{revision.title}</p><p className="mt-1 text-xs text-gray-500">{new Date(revision.created_at).toLocaleString()}</p><p className="mt-3 line-clamp-3 whitespace-pre-wrap text-sm text-gray-400">{revision.content}</p><div className="mt-4 flex flex-wrap gap-4"><button type="button" onClick={() => setCompareRevision(revision)} className="flex items-center gap-1 text-sm font-semibold text-violet-400"><ArrowLeftRight size={15} /> Compare with current</button><button type="button" onClick={() => restoreVersion(revision)} className="text-sm font-semibold text-blue-400">Restore this version</button></div></article>)}</div>}
          </section>
        </div>
      )}
    </section>
  );
}
