const READ_STORAGE_PREFIX = "nexthire-read-notifications-v1";
const DAY_MS = 24 * 60 * 60 * 1000;

function notificationId(type, application, value) {
  return `${type}:${application.id}:${value || "current"}`;
}

function validDate(value) {
  if (!value) return null;
  const parsed = new Date(value);
  return Number.isNaN(parsed.getTime()) ? null : parsed;
}

export function buildApplicationNotifications(applications, now = new Date()) {
  const notifications = [];
  const upcomingLimit = now.getTime() + (7 * DAY_MS);

  for (const application of applications) {
    if (["rejected", "archived"].includes(application.status)) continue;

    const followUp = validDate(application.follow_up_at);
    if (followUp && followUp.getTime() <= upcomingLimit) {
      const overdue = followUp.getTime() < now.getTime();
      notifications.push({
        id: notificationId("follow-up", application, application.follow_up_at),
        type: "follow-up",
        title: overdue ? "Follow-up overdue" : "Follow-up coming up",
        message: `${application.role} at ${application.company}`,
        eventAt: followUp.toISOString(),
        overdue,
        to: "/applications",
      });
    }

    const deadline = validDate(application.deadline_at);
    if (deadline && deadline.getTime() <= upcomingLimit) {
      const overdue = deadline.getTime() < now.getTime();
      notifications.push({
        id: notificationId("deadline", application, application.deadline_at),
        type: "deadline",
        title: overdue ? "Application deadline passed" : "Application deadline approaching",
        message: `${application.role} at ${application.company}`,
        eventAt: deadline.toISOString(),
        overdue,
        to: "/applications",
      });
    }

    if (application.status === "preparing" && application.package_reviewed_at) {
      notifications.push({
        id: notificationId(
          "package",
          application,
          application.package_reviewed_at,
        ),
        type: "package",
        title: "Application package ready",
        message: `Review the employer form for ${application.role} at ${application.company}`,
        eventAt: application.package_reviewed_at,
        overdue: false,
        to: "/applications",
      });
    }
  }

  return notifications.sort((left, right) => {
    if (left.overdue !== right.overdue) return left.overdue ? -1 : 1;
    return new Date(left.eventAt).getTime() - new Date(right.eventAt).getTime();
  });
}

export function buildSavedSearchNotifications(savedSearches) {
  return savedSearches
    .filter(
      (savedSearch) =>
        Number(savedSearch.new_match_count || 0) > 0
        && validDate(savedSearch.last_run_at),
    )
    .map((savedSearch) => ({
      id: `saved-search:${savedSearch.id}:${savedSearch.last_run_at}`,
      type: "saved-search",
      title: "New job matches found",
      message: `${savedSearch.name} found ${savedSearch.new_match_count} new ${
        Number(savedSearch.new_match_count) === 1 ? "role" : "roles"
      }.`,
      eventAt: new Date(savedSearch.last_run_at).toISOString(),
      overdue: false,
      to: "/job-library",
    }))
    .sort(
      (left, right) =>
        new Date(right.eventAt).getTime() - new Date(left.eventAt).getTime(),
    );
}

function storageKey(userId) {
  return `${READ_STORAGE_PREFIX}:${userId}`;
}

export function getReadNotificationIds(userId) {
  if (!userId) return new Set();
  try {
    const stored = JSON.parse(
      localStorage.getItem(storageKey(userId)) || "[]",
    );
    return new Set(Array.isArray(stored) ? stored : []);
  } catch {
    return new Set();
  }
}

export function saveReadNotificationIds(userId, ids) {
  if (!userId) return;
  localStorage.setItem(storageKey(userId), JSON.stringify([...ids]));
  window.dispatchEvent(new Event("nexthire-notifications-read"));
}
