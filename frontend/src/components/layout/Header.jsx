import { useEffect, useState } from "react";
import { Menu } from "lucide-react";
import { useLocation, useNavigate } from "react-router-dom";

import { useAuth } from "../../hooks/useAuth";
import { getCurrentUser } from "../../services/api";
import UserMenu from "../header/UserMenu";
import GlobalSearch from "../header/GlobalSearch";
import NotificationButton from "../header/NotificationButton";

function Header({ onMenuOpen }) {

  const location = useLocation();
  const navigate = useNavigate();
  const { logout } = useAuth();

  const [user, setUser] = useState(null);

  useEffect(() => {

    async function fetchUser() {

      try {

        const response = await getCurrentUser();

        setUser(response.data);

      } catch {

      }

    }

    fetchUser();

  }, []);

  const titles = {
    "/": "Dashboard",
    "/dashboard": "Dashboard",
    "/resume": "Resume Studio",
    "/resume-tailor": "Resume Tailor",
    "/cover-letter": "Cover Letter",
    "/jobs": "Jobs",
    "/job-library": "Job Library",
    "/applications": "Application Tracker",
    "/job-match": "Job Match",
    "/interview": "Interview Center",
    "/learning": "Learning",
    "/settings": "Settings",
    "/profile": "Profile",
    "/skill-gap": "Skill Gap Analysis",
    "/notifications": "Notifications",
    "/onboarding": "Getting Started",
    "/help": "Help Center",
    "/admin/operations": "Operations",
  };

  const pageTitle =
    titles[location.pathname] || "NextHire AI";

  return (

    <header className="flex min-h-16 items-center justify-between gap-3 border-b border-slate-200 bg-white px-3 shadow-sm sm:px-6">

      {/* Left Side */}

      <div className="flex min-w-0 items-center gap-3 sm:gap-4">

        <button
          type="button"
          aria-label="Open navigation"
          onClick={onMenuOpen}
          className="shrink-0 rounded-lg p-2 text-slate-600 hover:bg-slate-100 hover:text-slate-900 md:hidden"
        >
          <Menu size={22} />
        </button>

        <h2 className="truncate text-base font-semibold text-slate-900 sm:text-xl">

          {pageTitle}

        </h2>

        <GlobalSearch />

      </div>

      {/* Right Side */}

      <div className="flex shrink-0 items-center gap-1 sm:gap-4">

        <NotificationButton userId={user?.id} />

        <UserMenu
          firstName={user?.first_name || "User"}
          fullName={
            user
              ? [user.first_name, user.last_name]
                .filter(Boolean)
                .join(" ") || user.email
              : "User"
          }
          isAdmin={Boolean(user?.is_admin)}
          onLogout={() => {
            logout();
            navigate("/login", { replace: true });
          }}
        />

      </div>

    </header>

  );

}

export default Header;
