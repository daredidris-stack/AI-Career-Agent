import { useEffect, useMemo, useState } from "react";
import {
  BriefcaseBusiness,
  CalendarDays,
  CalendarClock,
  ChevronLeft,
  ChevronRight,
  ExternalLink,
  FileCheck2,
  Mail,
  MapPin,
  List,
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

function dayKey(value) {
  const date = value instanceof Date ? value : new Date(value);
  if (Number.isNaN(date.getTime())) return "";
  return [
    date.getFullYear(),
    String(date.getMonth() + 1).padStart(2, "0"),
    String(date.getDate()).padStart(2, "0"),
  ].join("-");
}

function monthDays(monthDate) {
  const first = new Date(
    monthDate.getFullYear(),
    monthDate.getMonth(),
    1,
  );
  const start = new Date(first);
  start.setDate(first.getDate() - first.getDay());
  return Array.from({ length: 42 }, (_, index) => {
    const day = new Date(start);
    day.setDate(start.getDate() + index);
    return day;
  });
}

function applicationEvents(applications) {
  return applications.flatMap((application) => [
    application.deadline_at && {
      id: `deadline:${application.id}`,
      type: "deadline",
      label: "Deadline",
      eventAt: application.deadline_at,
      application,
    },
    application.follow_up_at && {
      id: `follow-up:${application.id}`,
      type: "follow-up",
      label: "Follow up",
      eventAt: application.follow_up_at,
      application,
    },
    application.applied_at && {
      id: `applied:${application.id}`,
      type: "applied",
      label: "Applied",
      eventAt: application.applied_at,
      application,
    },
  ].filter(Boolean));
}

function Applications() {
  const [applications, setApplications] = useState([]);
  const [documents, setDocuments] = useState([]);
  const [filter, setFilter] = useState("active");
  const [form, setForm] = useState(emptyForm);
  const [editingId, setEditingId] = useState(null);
  const [showForm, setShowForm] = useState(false);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");
  const [view, setView] = useState("pipeline");
  const [calendarMonth, setCalendarMonth] = useState(
    () => new Date(new Date().getFullYear(), new Date().getMonth(), 1),
  );

  async function loadApplications() {
    setLoading(true);
    setError("");
    try {
      const [applicationResponse, documentResponse] = await Promise.all([
        api.get("/applications"),
        api.get("/documents").catch(() => ({ data: [] })),
      ]);
      setApplications(applicationResponse.data);
      setDocuments(documentResponse.data);
    } catch (requestError) {
      setError(requestError.response?.data?.detail || "Applications could not be loaded.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadApplications();
  }, []);

  useEffect(() => {
    if (!showForm) return undefined;
    const previousOverflow = document.body.style.overflow;
    document.body.style.overflow = "hidden";
    function closeOnEscape(event) {
      if (event.key === "Escape") setShowForm(false);
    }
    document.addEventListener("keydown", closeOnEscape);
    return () => {
      document.body.style.overflow = previousOverflow;
      document.removeEventListener("keydown", closeOnEscape);
    };
  }, [showForm]);

  const counts = useMemo(() => Object.fromEntries(
    statuses.map(([value]) => [
      value,
      applications.filter((application) => application.status === value).length,
    ]),
  ), [applications]);
  const documentsById = useMemo(
    () => new Map(documents.map((document) => [document.id, document])),
    [documents],
  );

  const visibleApplications = applications.filter((application) => {
    if (filter === "all") return true;
    if (filter === "active") return !["rejected", "archived"].includes(application.status);
    return application.status === filter;
  });
  const events = applicationEvents(visibleApplications);

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
            <h1 className="text-3xl font-bold sm:text-4xl">Application Tracker</h1>
          </div>
          <p className="mt-3 text-blue-100">Keep every opportunity, deadline, and follow-up in one place.</p>
        </div>
        <button type="button" onClick={openCreateForm} className="flex items-center justify-center gap-2 rounded-xl bg-white px-5 py-3 font-semibold text-blue-700 transition hover:bg-blue-50">
          <Plus size={19} /> Add application
        </button>
      </section>

      <section className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4 xl:grid-cols-7">
        {statuses.map(([value, label]) => (
          <button type="button" key={value} onClick={() => setFilter(value)} className={`rounded-2xl border p-4 text-left transition ${filter === value ? "border-blue-500 bg-blue-500/10" : "border-gray-800 bg-gray-900 hover:border-gray-700"}`}>
            <span className="text-sm text-gray-400">{label}</span>
            <span className="mt-1 block text-2xl font-bold text-white">{counts[value] || 0}</span>
          </button>
        ))}
      </section>

      <div className="flex flex-wrap gap-2">
        {["active", "all"].map((value) => (
          <button type="button" key={value} onClick={() => setFilter(value)} className={`rounded-full px-4 py-2 text-sm font-medium ${filter === value ? "bg-blue-600 text-white" : "bg-gray-800 text-gray-300"}`}>
            {value === "active" ? "Active pipeline" : "All applications"}
          </button>
        ))}
        <span className="mx-1 hidden border-l border-gray-700 sm:block" />
        <button
          type="button"
          onClick={() => setView("pipeline")}
          className={`inline-flex items-center gap-2 rounded-full px-4 py-2 text-sm font-medium ${
            view === "pipeline"
              ? "bg-blue-600 text-white"
              : "bg-gray-800 text-gray-300"
          }`}
        >
          <List size={16} />
          Pipeline
        </button>
        <button
          type="button"
          onClick={() => setView("calendar")}
          className={`inline-flex items-center gap-2 rounded-full px-4 py-2 text-sm font-medium ${
            view === "calendar"
              ? "bg-blue-600 text-white"
              : "bg-gray-800 text-gray-300"
          }`}
        >
          <CalendarDays size={16} />
          Calendar
        </button>
      </div>

      {error && <div className="rounded-xl border border-red-800 bg-red-950/50 p-4 text-red-300">{error}</div>}

      {loading ? (
        <div className="rounded-2xl border border-gray-800 bg-gray-900 p-10 text-center text-gray-400">Loading your applications...</div>
      ) : view === "calendar" ? (
        <ApplicationCalendar
          month={calendarMonth}
          events={events}
          onPrevious={() =>
            setCalendarMonth(
              new Date(
                calendarMonth.getFullYear(),
                calendarMonth.getMonth() - 1,
                1,
              ),
            )
          }
          onNext={() =>
            setCalendarMonth(
              new Date(
                calendarMonth.getFullYear(),
                calendarMonth.getMonth() + 1,
                1,
              ),
            )
          }
          onToday={() =>
            setCalendarMonth(
              new Date(
                new Date().getFullYear(),
                new Date().getMonth(),
                1,
              ),
            )
          }
          onOpenApplication={openEditForm}
        />
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
                    <button type="button" onClick={() => openEditForm(application)} aria-label="Edit application" className="rounded-lg bg-gray-800 p-2 text-gray-300 hover:text-white"><Pencil size={16} /></button>
                    <button type="button" onClick={() => deleteApplication(application)} aria-label="Delete application" className="rounded-lg bg-gray-800 p-2 text-gray-300 hover:text-red-400"><Trash2 size={16} /></button>
                  </div>
                </div>

                {application.location && <p className="mt-4 flex items-center gap-2 text-sm text-gray-400"><MapPin size={16} />{application.location}</p>}
                {application.contact_email && <p className="mt-2 flex items-center gap-2 text-sm text-gray-400"><Mail size={16} />{application.contact_email}</p>}
                {application.follow_up_at && <p className={`mt-2 flex items-center gap-2 text-sm ${followUpDue ? "text-amber-300" : "text-gray-400"}`}><CalendarClock size={16} />Follow up {dateLabel(application.follow_up_at)}</p>}
                {application.package_reviewed_at && (
                  <div className="mt-4 rounded-xl border border-emerald-900/70 bg-emerald-950/30 p-3 text-sm text-emerald-200">
                    <p className="flex items-center gap-2 font-semibold">
                      <FileCheck2 size={16} /> Reviewed application package
                    </p>
                    <p className="mt-2 text-xs leading-5 text-emerald-300">
                      Resume: {documentsById.get(application.resume_document_id)?.title || "Selected resume"}
                      {application.cover_letter_document_id && (
                        <> · Cover letter: {documentsById.get(application.cover_letter_document_id)?.title || "Selected cover letter"}</>
                      )}
                    </p>
                  </div>
                )}
                {application.notes && <p className="mt-4 line-clamp-3 border-t border-gray-800 pt-4 text-sm leading-6 text-gray-400">{application.notes}</p>}
                {application.job_url && <a href={application.job_url} target="_blank" rel="noreferrer" className="mt-5 flex items-center gap-2 text-sm font-medium text-blue-400 hover:text-blue-300">View job posting <ExternalLink size={15} /></a>}
              </article>
            );
          })}
        </section>
      )}

      {showForm && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 p-4" role="presentation">
          <form onSubmit={saveApplication} role="dialog" aria-modal="true" aria-labelledby="application-form-title" className="max-h-[92vh] w-full max-w-3xl overflow-y-auto rounded-2xl border border-gray-700 bg-gray-900 p-6 shadow-2xl">
            <div className="flex items-center justify-between">
              <h2 id="application-form-title" className="text-2xl font-bold text-white">{editingId ? "Edit application" : "Add application"}</h2>
              <button type="button" onClick={() => setShowForm(false)} aria-label="Close application form" className="text-gray-400 hover:text-white"><X /></button>
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

function ApplicationCalendar({
  month,
  events,
  onPrevious,
  onNext,
  onToday,
  onOpenApplication,
}) {
  const days = monthDays(month);
  const eventsByDay = new Map();
  for (const event of events) {
    const key = dayKey(event.eventAt);
    if (!key) continue;
    eventsByDay.set(key, [...(eventsByDay.get(key) || []), event]);
  }
  const styles = {
    deadline: "border-red-400/40 bg-red-500/15 text-red-200",
    "follow-up": "border-amber-400/40 bg-amber-500/15 text-amber-200",
    applied: "border-emerald-400/40 bg-emerald-500/15 text-emerald-200",
  };

  return (
    <section className="rounded-2xl border border-gray-800 bg-gray-900 p-4 shadow-lg sm:p-6">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold text-white">
            {month.toLocaleDateString([], {
              month: "long",
              year: "numeric",
            })}
          </h2>
          <div className="mt-2 flex flex-wrap gap-3 text-xs text-gray-400">
            <span className="text-red-300">● Deadline</span>
            <span className="text-amber-300">● Follow up</span>
            <span className="text-emerald-300">● Applied</span>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <button
            type="button"
            onClick={onPrevious}
            aria-label="Previous month"
            className="rounded-lg border border-gray-700 p-2 text-gray-300 hover:border-blue-500 hover:text-white"
          >
            <ChevronLeft size={18} />
          </button>
          <button
            type="button"
            onClick={onToday}
            className="rounded-lg border border-gray-700 px-3 py-2 text-sm font-semibold text-gray-200 hover:border-blue-500"
          >
            Today
          </button>
          <button
            type="button"
            onClick={onNext}
            aria-label="Next month"
            className="rounded-lg border border-gray-700 p-2 text-gray-300 hover:border-blue-500 hover:text-white"
          >
            <ChevronRight size={18} />
          </button>
        </div>
      </div>

      <div className="mt-5 overflow-x-auto">
        <div className="min-w-[760px]">
          <div className="grid grid-cols-7 border-b border-gray-700">
            {["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"].map((day) => (
              <div
                key={day}
                className="px-2 py-3 text-center text-xs font-bold uppercase tracking-wide text-gray-500"
              >
                {day}
              </div>
            ))}
          </div>
          <div className="grid grid-cols-7 overflow-hidden rounded-b-xl border-l border-gray-800">
            {days.map((day) => {
              const key = dayKey(day);
              const dayEvents = eventsByDay.get(key) || [];
              const isCurrentMonth = day.getMonth() === month.getMonth();
              const isToday = key === dayKey(new Date());
              return (
                <div
                  key={key}
                  className={`min-h-32 border-b border-r border-gray-800 p-2 ${
                    isCurrentMonth ? "bg-gray-950" : "bg-gray-950/40"
                  }`}
                >
                  <span className={`inline-flex h-7 w-7 items-center justify-center rounded-full text-xs font-semibold ${
                    isToday
                      ? "bg-blue-600 text-white"
                      : isCurrentMonth
                        ? "text-gray-300"
                        : "text-gray-600"
                  }`}>
                    {day.getDate()}
                  </span>
                  <div className="mt-1 space-y-1">
                    {dayEvents.slice(0, 4).map((event) => (
                      <button
                        key={event.id}
                        type="button"
                        onClick={() => onOpenApplication(event.application)}
                        className={`w-full rounded-lg border px-2 py-1 text-left text-[11px] leading-4 ${styles[event.type]}`}
                        title={`${event.label}: ${event.application.role} at ${event.application.company}`}
                      >
                        <span className="block font-bold">{event.label}</span>
                        <span className="block truncate">
                          {event.application.company}
                        </span>
                      </button>
                    ))}
                    {dayEvents.length > 4 && (
                      <p className="px-1 text-[10px] text-gray-500">
                        +{dayEvents.length - 4} more
                      </p>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </section>
  );
}

export default Applications;
