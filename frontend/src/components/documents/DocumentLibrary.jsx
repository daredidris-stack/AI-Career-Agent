import { useEffect, useState } from "react";
import { Download, FileText, History, Pencil, Trash2, X } from "lucide-react";

import api from "../../services/api";


const kindLabels = {
  resume: "Resume",
  tailored_resume: "Tailored resume",
  cover_letter: "Cover letter",
  job_match: "Job match",
};


export default function DocumentLibrary({ refreshToken }) {
  const [documents, setDocuments] = useState([]);
  const [editing, setEditing] = useState(null);
  const [versionDocument, setVersionDocument] = useState(null);
  const [versions, setVersions] = useState([]);
  const [error, setError] = useState("");

  useEffect(() => {
    loadDocuments();
  }, [refreshToken]);

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

  async function deleteDocument(document) {
    if (!window.confirm(`Delete “${document.title}”?`)) return;
    await api.delete(`/documents/${document.id}`);
    await loadDocuments();
  }

  async function showVersions(document) {
    const response = await api.get(`/documents/${document.id}/versions`);
    setVersionDocument(document);
    setVersions(response.data);
  }

  async function restoreVersion(revision) {
    await api.post(
      `/documents/${versionDocument.id}/versions/${revision.id}/restore`,
    );
    setVersionDocument(null);
    setVersions([]);
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

  return (
    <section className="rounded-2xl border border-gray-800 bg-gray-900 p-6">
      <div>
        <h2 className="text-2xl font-bold text-white">Document library</h2>
        <p className="mt-1 text-sm text-gray-400">Your resumes and generated career documents are saved privately.</p>
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
              <button onClick={() => setEditing({ ...document })} className="flex items-center gap-1 text-blue-400"><Pencil size={15} /> Edit</button>
              <button onClick={() => showVersions(document)} className="flex items-center gap-1 text-violet-400"><History size={15} /> History</button>
              <button onClick={() => downloadDocument(document, "pdf")} className="flex items-center gap-1 text-emerald-400"><Download size={15} /> PDF</button>
              <button onClick={() => downloadDocument(document, "docx")} className="flex items-center gap-1 text-emerald-400"><Download size={15} /> DOCX</button>
              <button onClick={() => deleteDocument(document)} className="flex items-center gap-1 text-red-400"><Trash2 size={15} /> Delete</button>
            </div>
          </article>
        ))}
      </div>

      {editing && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 p-4">
          <form onSubmit={saveDocument} className="w-full max-w-3xl rounded-2xl border border-gray-700 bg-gray-900 p-6 shadow-2xl">
            <div className="flex items-center justify-between">
              <h3 className="text-xl font-bold text-white">Edit document</h3>
              <button type="button" onClick={() => setEditing(null)} aria-label="Close"><X className="text-gray-400" /></button>
            </div>
            <input value={editing.title} onChange={(event) => setEditing({ ...editing, title: event.target.value })} required className="mt-5 w-full rounded-xl border border-gray-700 bg-gray-950 px-4 py-3 text-white" />
            <textarea rows={18} value={editing.content} onChange={(event) => setEditing({ ...editing, content: event.target.value })} required className="mt-4 w-full rounded-xl border border-gray-700 bg-gray-950 px-4 py-3 font-mono text-sm text-white" />
            <div className="mt-4 flex justify-end gap-3"><button type="button" onClick={() => setEditing(null)} className="px-4 py-2 text-gray-300">Cancel</button><button className="rounded-xl bg-blue-600 px-5 py-2 font-semibold text-white">Save changes</button></div>
          </form>
        </div>
      )}

      {versionDocument && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 p-4">
          <section className="max-h-[80vh] w-full max-w-2xl overflow-y-auto rounded-2xl border border-gray-700 bg-gray-900 p-6 shadow-2xl">
            <div className="flex items-center justify-between"><div><h3 className="text-xl font-bold text-white">Version history</h3><p className="mt-1 text-sm text-gray-400">{versionDocument.title}</p></div><button onClick={() => setVersionDocument(null)} aria-label="Close"><X className="text-gray-400" /></button></div>
            {versions.length === 0 ? <p className="mt-6 text-gray-400">No earlier versions yet.</p> : <div className="mt-6 space-y-3">{versions.map((revision) => <article key={revision.id} className="rounded-xl border border-gray-700 bg-gray-950 p-4"><p className="font-medium text-white">{revision.title}</p><p className="mt-1 text-xs text-gray-500">{new Date(revision.created_at).toLocaleString()}</p><p className="mt-3 line-clamp-3 whitespace-pre-wrap text-sm text-gray-400">{revision.content}</p><button onClick={() => restoreVersion(revision)} className="mt-4 text-sm font-semibold text-blue-400">Restore this version</button></article>)}</div>}
          </section>
        </div>
      )}
    </section>
  );
}
