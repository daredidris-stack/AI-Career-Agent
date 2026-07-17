import { useEffect, useMemo, useState } from "react";
import {
  BriefcaseBusiness,
  CalendarClock,
  ExternalLink,
  Mail,
  MapPin,
  Pencil,
  Plus,
  Trash2,
  X,
} from "lucide-react";

import api from "../services/api";

const statuses = [
  ["saved", "Saved"],
  ["preparing", "Preparing"],
  ["applied", "Applied"],
  ["interview", "Interview"],
  ["offer", "Offer"],
  ["rejected", "Rejected"],
  ["archived", "Archived"],
];

const emptyForm = {
  company: "",
  role: "",
  job_url: "",
  location: "",
  status: "saved",
  notes: "",
  contact_name: "",
  contact_email: "",
  deadline_at: "",
  follow_up_at: "",
  applied_at: "",
};

function toInputDate(value) {
  return value ? value.slice(0, 16) : "";
}

function toPayload(form) {
  return Object.fromEntries(
    Object.entries(form).map(([key, value]) => [key, value || null]),
  );
}

function dateLabel(value) {
  return new Date(value).toLocaleString([], {
    dateStyle: "medium",
    timeStyle: "short",
  });
}

function Applications() {
  const [applications, setApplications] = useState([]);
  const [filter, setFilter] = useState("active");
  const [form, setForm] = useState(emptyForm);
  const [editingId, setEditingId] = useState(null);
  const [showForm, setShowForm] = useState(false);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");

  async function loadApplications() {
    setLoading(true);
    setError("");
    try {
      const response = await api.get("/applications");
      setApplications(response.data);
    } catch (requestError) {
      setError(requestError.response?.data?.detail || "Applications could not be loaded.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadApplications();
  }, []);

  const counts = useMemo(() => Object.fromEntries(
    statuses.map(([value]) => [
      value,
      applications.filter((application) => application.status === value).length,
    ]),
  ), [applications]);

  const visibleApplications = applications.filter((application) => {
    if (filter === "all") return true;
    if (filter === "active") return !["rejected", "archived"].includes(application.status);
    return application.status === filter;
  });

  function openCreateForm() {
    setEditingId(null);
    setForm(emptyForm);
    setShowForm(true);
    setError("");
  }

  function openEditForm(application) {
    setEditingId(application.id);
    setForm({
      ...emptyForm,
      ...application,
      deadline_at: toInputDate(application.deadline_at),
      follow_up_at: toInputDate(application.follow_up_at),
      applied_at: toInputDate(application.applied_at),
    });
    setShowForm(true);
    setError("");
  }

  async function saveApplication(event) {
    event.preventDefault();
    setSaving(true);
    setError("");
    try {
      const payload = toPayload(form);
      if (editingId) {
        await api.put(`/applications/${editingId}`, payload);
      } else {
        await api.post("/applications", payload);
      }
      setShowForm(false);
      await loadApplications();
    } catch (requestError) {
      setError(requestError.response?.data?.detail || "The application could not be saved.");
    } finally {
      setSaving(false);
    }
  }

  async function deleteApplication(application) {
    if (!window.confirm(`Delete ${application.role} at ${application.company}?`)) return;
    try {
      await api.delete(`/applications/${application.id}`);
      setApplications((current) => current.filter((item) => item.id !== application.id));
    } catch (requestError) {
      setError(requestError.response?.data?.detail || "The application could not be deleted.");
    }
  }

  return (
    <div className="space-y-7">
      <section className="flex flex-col justify-between gap-5 rounded-3xl bg-gradient-to-r from-blue-600 to-indigo-700 p-8 text-white shadow-xl md:flex-row md:items-center">
        <div>
          <div className="flex items-center gap-3">
            <BriefcaseBusiness size={30} />
            <h1 className="text-4xl font-bold">Application Tracker</h1>
          </div>
          <p className="mt-3 text-blue-100">Keep every opportunity, deadline, and follow-up in one place.</p>
        </div>
        <button onClick={openCreateForm} className="flex items-center justify-center gap-2 rounded-xl bg-white px-5 py-3 font-semibold text-blue-700 transition hover:bg-blue-50">
          <Plus size={19} /> Add application
        </button>
      </section>

      <section className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4 xl:grid-cols-7">
        {statuses.map(([value, label]) => (
          <button key={value} onClick={() => setFilter(value)} className={`rounded-2xl border p-4 text-left transition ${filter === value ? "border-blue-500 bg-blue-500/10" : "border-gray-800 bg-gray-900 hover:border-gray-700"}`}>
            <span className="text-sm text-gray-400">{label}</span>
            <span className="mt-1 block text-2xl font-bold text-white">{counts[value] || 0}</span>
          </button>
        ))}
      </section>

      <div className="flex flex-wrap gap-2">
        {["active", "all"].map((value) => (
          <button key={value} onClick={() => setFilter(value)} className={`rounded-full px-4 py-2 text-sm font-medium ${filter === value ? "bg-blue-600 text-white" : "bg-gray-800 text-gray-300"}`}>
            {value === "active" ? "Active pipeline" : "All applications"}
          </button>
        ))}
      </div>

      {error && <div className="rounded-xl border border-red-800 bg-red-950/50 p-4 text-red-300">{error}</div>}

      {loading ? (
        <div className="rounded-2xl border border-gray-800 bg-gray-900 p-10 text-center text-gray-400">Loading your applications...</div>
      ) : visibleApplications.length === 0 ? (
        <div className="rounded-2xl border border-dashed border-gray-700 bg-gray-900 p-12 text-center">
          <BriefcaseBusiness className="mx-auto text-gray-500" size={42} />
          <h2 className="mt-4 text-xl font-semibold text-white">No applications in this view</h2>
          <p className="mt-2 text-gray-400">Add an opportunity or choose another status.</p>
        </div>
      ) : (
        <section className="grid gap-5 lg:grid-cols-2 xl:grid-cols-3">
          {visibleApplications.map((application) => {
            const followUpDue = application.follow_up_at && new Date(application.follow_up_at) < new Date();
            return (
              <article key={application.id} className="rounded-2xl border border-gray-800 bg-gray-900 p-6 shadow-lg">
                <div className="flex items-start justify-between gap-4">
                  <div>
                    <span className="rounded-full bg-blue-500/10 px-3 py-1 text-xs font-semibold uppercase tracking-wide text-blue-300">{application.status}</span>
                    <h2 className="mt-3 text-xl font-bold text-white">{application.role}</h2>
                    <p className="mt-1 text-gray-300">{application.company}</p>
                  </div>
                  <div className="flex gap-2">
                    <button onClick={() => openEditForm(application)} aria-label="Edit application" className="rounded-lg bg-gray-800 p-2 text-gray-300 hover:text-white"><Pencil size={16} /></button>
                    <button onClick={() => deleteApplication(application)} aria-label="Delete application" className="rounded-lg bg-gray-800 p-2 text-gray-300 hover:text-red-400"><Trash2 size={16} /></button>
                  </div>
                </div>

                {application.location && <p className="mt-4 flex items-center gap-2 text-sm text-gray-400"><MapPin size={16} />{application.location}</p>}
                {application.contact_email && <p className="mt-2 flex items-center gap-2 text-sm text-gray-400"><Mail size={16} />{application.contact_email}</p>}
                {application.follow_up_at && <p className={`mt-2 flex items-center gap-2 text-sm ${followUpDue ? "text-amber-300" : "text-gray-400"}`}><CalendarClock size={16} />Follow up {dateLabel(application.follow_up_at)}</p>}
                {application.notes && <p className="mt-4 line-clamp-3 border-t border-gray-800 pt-4 text-sm leading-6 text-gray-400">{application.notes}</p>}
                {application.job_url && <a href={application.job_url} target="_blank" rel="noreferrer" className="mt-5 flex items-center gap-2 text-sm font-medium text-blue-400 hover:text-blue-300">View job posting <ExternalLink size={15} /></a>}
              </article>
            );
          })}
        </section>
      )}

      {showForm && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 p-4">
          <form onSubmit={saveApplication} className="max-h-[92vh] w-full max-w-3xl overflow-y-auto rounded-2xl border border-gray-700 bg-gray-900 p-6 shadow-2xl">
            <div className="flex items-center justify-between">
              <h2 className="text-2xl font-bold text-white">{editingId ? "Edit application" : "Add application"}</h2>
              <button type="button" onClick={() => setShowForm(false)} className="text-gray-400 hover:text-white"><X /></button>
            </div>
            <div className="mt-6 grid gap-4 md:grid-cols-2">
              {[['company', 'Company', true], ['role', 'Role', true], ['location', 'Location'], ['job_url', 'Job URL'], ['contact_name', 'Contact name'], ['contact_email', 'Contact email']].map(([name, label, required]) => (
                <label key={name} className="block"><span className="mb-2 block text-sm text-gray-300">{label}</span><input required={required} type={name === 'contact_email' ? 'email' : name === 'job_url' ? 'url' : 'text'} value={form[name] || ''} onChange={(event) => setForm({ ...form, [name]: event.target.value })} className="w-full rounded-xl border border-gray-700 bg-gray-950 px-4 py-3 text-white outline-none focus:border-blue-500" /></label>
              ))}
              <label className="block"><span className="mb-2 block text-sm text-gray-300">Status</span><select value={form.status} onChange={(event) => setForm({ ...form, status: event.target.value })} className="w-full rounded-xl border border-gray-700 bg-gray-950 px-4 py-3 text-white">{statuses.map(([value, label]) => <option key={value} value={value}>{label}</option>)}</select></label>
              {[['deadline_at', 'Application deadline'], ['follow_up_at', 'Follow-up reminder'], ['applied_at', 'Applied date']].map(([name, label]) => (
                <label key={name} className="block"><span className="mb-2 block text-sm text-gray-300">{label}</span><input type="datetime-local" value={form[name] || ''} onChange={(event) => setForm({ ...form, [name]: event.target.value })} className="w-full rounded-xl border border-gray-700 bg-gray-950 px-4 py-3 text-white" /></label>
              ))}
              <label className="block md:col-span-2"><span className="mb-2 block text-sm text-gray-300">Notes</span><textarea rows="4" value={form.notes || ''} onChange={(event) => setForm({ ...form, notes: event.target.value })} className="w-full rounded-xl border border-gray-700 bg-gray-950 px-4 py-3 text-white outline-none focus:border-blue-500" /></label>
            </div>
            <div className="mt-6 flex justify-end gap-3"><button type="button" onClick={() => setShowForm(false)} className="rounded-xl bg-gray-800 px-5 py-3 text-gray-200">Cancel</button><button disabled={saving} className="rounded-xl bg-blue-600 px-5 py-3 font-semibold text-white disabled:opacity-60">{saving ? "Saving..." : "Save application"}</button></div>
          </form>
        </div>
      )}
    </div>
  );
}

export default Applications;
