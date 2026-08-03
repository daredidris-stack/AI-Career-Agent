import { useEffect, useState } from "react";
import { Bell } from "lucide-react";
import { useLocation, useNavigate } from "react-router-dom";

import api from "../../services/api";
import {
  buildApplicationNotifications,
  buildSavedSearchNotifications,
  getReadNotificationIds,
} from "../../utils/notifications";

export default function NotificationButton({ userId }) {
  const location = useLocation();
  const navigate = useNavigate();
  const [unreadCount, setUnreadCount] = useState(0);

  useEffect(() => {
    let active = true;

    async function refresh() {
      if (!userId) {
        setUnreadCount(0);
        return;
      }
      try {
        const [applicationResponse, searchResponse] = await Promise.all([
          api.get("/applications"),
          api.get("/job-library/searches"),
        ]);
        if (!active) return;
        const readIds = getReadNotificationIds(userId);
        setUnreadCount(
          [
            ...buildApplicationNotifications(applicationResponse.data),
            ...buildSavedSearchNotifications(searchResponse.data),
          ]
            .filter((notification) => !readIds.has(notification.id))
            .length,
        );
      } catch {
        if (active) setUnreadCount(0);
      }
    }

    refresh();
    window.addEventListener("nexthire-notifications-read", refresh);
    return () => {
      active = false;
      window.removeEventListener("nexthire-notifications-read", refresh);
    };
  }, [location.pathname, userId]);

  return (
    <button
      type="button"
      aria-label={
        unreadCount
          ? `Open notifications, ${unreadCount} unread`
          : "Open notifications"
      }
      onClick={() => navigate("/notifications")}
      className="relative hidden rounded-lg p-2 text-slate-500 hover:bg-slate-100 hover:text-slate-900 sm:block"
    >
      <Bell size={20} />
      {unreadCount > 0 && (
        <span className="absolute right-0 top-0 flex h-5 min-w-5 items-center justify-center rounded-full bg-red-500 px-1 text-[10px] font-bold text-white">
          {unreadCount > 9 ? "9+" : unreadCount}
        </span>
      )}
    </button>
  );
}
