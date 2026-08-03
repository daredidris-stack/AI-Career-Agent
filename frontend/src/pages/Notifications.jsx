import { useEffect, useMemo, useState } from "react";
import {
  Bell,
  CalendarClock,
  CheckCheck,
  FileCheck2,
  SearchCheck,
  Timer,
} from "lucide-react";
import { Link } from "react-router-dom";

import api from "../services/api";
import {
  buildApplicationNotifications,
  buildSavedSearchNotifications,
  getReadNotificationIds,
  saveReadNotificationIds,
} from "../utils/notifications";

const icons = {
  deadline: CalendarClock,
  "follow-up": Timer,
  package: FileCheck2,
  "saved-search": SearchCheck,
};

function dateLabel(value) {
  return new Date(value).toLocaleString([], {
    dateStyle: "medium",
    timeStyle: "short",
  });
}

export default function Notifications() {
  const [applications, setApplications] = useState([]);
  const [savedSearches, setSavedSearches] = useState([]);
  const [userId, setUserId] = useState(null);
  const [readIds, setReadIds] = useState(() => new Set());
  const [filter, setFilter] = useState("unread");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    let active = true;
    Promise.all([
      api.get("/applications"),
      api.get("/job-library/searches"),
      api.get("/users/me"),
    ])
      .then(([applicationResponse, searchResponse, userResponse]) => {
        if (active) {
          setApplications(applicationResponse.data);
          setSavedSearches(searchResponse.data);
          setUserId(userResponse.data.id);
          setReadIds(getReadNotificationIds(userResponse.data.id));
        }
      })
      .catch((requestError) => {
        if (active) {
          setError(
            requestError.response?.data?.detail
              || "Notifications could not be loaded.",
          );
        }
      })
      .finally(() => {
        if (active) setLoading(false);
      });
    return () => {
      active = false;
    };
  }, []);

  const notifications = useMemo(
    () => [
      ...buildApplicationNotifications(applications),
      ...buildSavedSearchNotifications(savedSearches),
    ].sort(
      (left, right) => {
        if (left.overdue !== right.overdue) return left.overdue ? -1 : 1;
        return new Date(left.eventAt).getTime()
          - new Date(right.eventAt).getTime();
      },
    ),
    [applications, savedSearches],
  );
  const unreadCount = notifications
    .filter((notification) => !readIds.has(notification.id))
    .length;
  const visibleNotifications = filter === "unread"
    ? notifications.filter((notification) => !readIds.has(notification.id))
    : notifications;

  function markRead(notificationId) {
    const next = new Set(readIds);
    next.add(notificationId);
    setReadIds(next);
    saveReadNotificationIds(userId, next);
  }

  function markAllRead() {
    const next = new Set(readIds);
    notifications.forEach((notification) => next.add(notification.id));
    setReadIds(next);
    saveReadNotificationIds(userId, next);
  }

  return (
    <div className="space-y-7">
      <section className="flex flex-col justify-between gap-5 rounded-3xl bg-gradient-to-r from-violet-600 to-blue-700 p-8 text-white shadow-xl md:flex-row md:items-center">
        <div>
          <div className="flex items-center gap-3">
            <Bell size={30} />
            <h1 className="text-3xl font-bold sm:text-4xl">Notifications</h1>
          </div>
          <p className="mt-3 text-blue-100">
            Application deadlines, follow-up reminders, and reviewed packages
            that need your attention, plus new results from saved searches.
          </p>
        </div>
        <button
          type="button"
          onClick={markAllRead}
          disabled={!unreadCount}
          className="inline-flex items-center justify-center gap-2 rounded-xl bg-white px-5 py-3 font-semibold text-blue-700 disabled:cursor-not-allowed disabled:opacity-60"
        >
          <CheckCheck size={18} />
          Mark all as read
        </button>
      </section>

      <div className="flex items-center justify-between gap-4">
        <div className="flex gap-2">
          {[
            ["unread", `Unread (${unreadCount})`],
            ["all", `All (${notifications.length})`],
          ].map(([value, label]) => (
            <button
              key={value}
              type="button"
              onClick={() => setFilter(value)}
              className={`rounded-full px-4 py-2 text-sm font-semibold ${
                filter === value
                  ? "bg-blue-600 text-white"
                  : "border border-slate-300 bg-white text-slate-700"
              }`}
            >
              {label}
            </button>
          ))}
        </div>
        <Link
          to="/job-library"
          className="text-sm font-semibold text-blue-600 hover:text-blue-700"
        >
          Manage job alerts
        </Link>
      </div>

      {error && (
        <div role="alert" className="rounded-xl border border-red-300 bg-red-50 p-4 text-red-700">
          {error}
        </div>
      )}

      {loading ? (
        <div className="rounded-2xl border border-slate-200 bg-white p-10 text-center text-slate-500">
          Loading notifications...
        </div>
      ) : visibleNotifications.length ? (
        <section className="space-y-3">
          {visibleNotifications.map((notification) => {
            const Icon = icons[notification.type] || Bell;
            const isRead = readIds.has(notification.id);
            return (
              <article
                key={notification.id}
                className={`flex flex-col gap-4 rounded-2xl border bg-white p-5 shadow-sm sm:flex-row sm:items-center ${
                  isRead ? "border-slate-200" : "border-blue-300"
                }`}
              >
                <div className={`rounded-xl p-3 ${
                  notification.overdue
                    ? "bg-amber-100 text-amber-700"
                    : "bg-blue-100 text-blue-700"
                }`}>
                  <Icon size={22} />
                </div>
                <div className="min-w-0 flex-1">
                  <div className="flex flex-wrap items-center gap-2">
                    <h2 className="font-bold text-slate-900">
                      {notification.title}
                    </h2>
                    {!isRead && (
                      <span className="rounded-full bg-blue-100 px-2 py-1 text-[10px] font-bold uppercase tracking-wide text-blue-700">
                        New
                      </span>
                    )}
                  </div>
                  <p className="mt-1 text-sm text-slate-600">
                    {notification.message}
                  </p>
                  <p className={`mt-2 text-xs font-medium ${
                    notification.overdue ? "text-amber-700" : "text-slate-500"
                  }`}>
                    {dateLabel(notification.eventAt)}
                  </p>
                </div>
                <Link
                  to={notification.to}
                  onClick={() => markRead(notification.id)}
                  className="rounded-xl bg-slate-900 px-4 py-2 text-center text-sm font-semibold text-white hover:bg-slate-800"
                >
                  Review
                </Link>
              </article>
            );
          })}
        </section>
      ) : (
        <section className="rounded-2xl border border-dashed border-slate-300 bg-white p-12 text-center">
          <CheckCheck className="mx-auto text-emerald-600" size={42} />
          <h2 className="mt-4 text-xl font-bold text-slate-900">
            {filter === "unread" ? "You are all caught up" : "No reminders yet"}
          </h2>
          <p className="mx-auto mt-2 max-w-xl text-slate-600">
            Add an application deadline or follow-up reminder in Application
            Tracker, or run a saved job search, and it will appear here when it
            needs attention.
          </p>
          <Link
            to="/applications"
            className="mt-5 inline-flex rounded-xl bg-blue-600 px-5 py-3 font-semibold text-white hover:bg-blue-700"
          >
            Open Application Tracker
          </Link>
        </section>
      )}
    </div>
  );
}
