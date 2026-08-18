import { useEffect, useState } from "react";
import { Menu, Moon, Sun, Sidebar } from "lucide-react";
import { useLocation, useNavigate, NavLink } from "react-router-dom";

import { useAuth } from "../../hooks/useAuth";
import { getCurrentUser } from "../../services/api";
import UserMenu from "../header/UserMenu";
import GlobalSearch from "../header/GlobalSearch";
import NotificationButton from "../header/NotificationButton";

function Header({ _onMenuOpen, onToggleSidebar, sidebarCollapsed }) {

  const location = useLocation();
  const navigate = useNavigate();
  const { logout } = useAuth();

  const [user, setUser] = useState(null);
  const [theme, setTheme] = useState(() => {
    const saved = localStorage.getItem('theme');
    return saved || (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');
  });

  useEffect(() => {
    if (theme === 'dark') {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
    localStorage.setItem('theme', theme);
  }, [theme]);

  useEffect(() => {
    async function fetchUser() {
      try {
        const response = await getCurrentUser();
        setUser(response.data);
      } catch (err) {
        console.error('Failed to fetch user:', err);
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

  const pageTitle = titles[location.pathname] || "NextHire AI";

  // Breadcrumb items (simplified: just show the current page title for now)
  // In a more complex app, we would generate a hierarchy from the route.
  const breadcrumbItems = [
    { name: "Dashboard", path: "/" },
    { name: pageTitle, path: location.pathname, isCurrent: true },
  ];

  return (
    <header className="flex min-h-16 items-center justify-between gap-3 border-b border-slate-200 bg-white px-3 shadow-sm sm:px-6 dark:bg-slate-900 dark:border-slate-700">
      {/* Left Side */}
      <div className="flex min-w-0 items-center gap-3 sm:gap-4">
        {/* Sidebar toggle button (for desktop) */}
        <button
          type="button"
          aria-label={sidebarCollapsed ? 'Open sidebar' : 'Collapse sidebar'}
          onClick={onToggleSidebar}
          className="shrink-0 rounded-lg p-3 text-slate-600 hover:bg-slate-100 hover:text-slate-900 hidden md:inline-flex"
        >
          {sidebarCollapsed ? (
            <Sidebar size={22} />
          ) : (
            <Menu size={22} />
          )}
        </button>

        <h2 className="truncate text-base font-semibold text-slate-900 sm:text-xl dark:text-slate-100">
          {pageTitle}
        </h2>

        <GlobalSearch />
      </div>

      {/* Center: Breadcrumb */}
      <nav className="flex items-center gap-1 overflow-hidden rounded-md px-2 py-1 text-slate-500 dark:text-slate-400">
        {breadcrumbItems.map((item, index) => (
          <>
            {!item.isCurrent && (
              <NavLink
                to={item.path}
                className="hover:text-slate-700 dark:hover:text-slate-200"
              >
                {item.name}
              </NavLink>
            )}
            {item.isCurrent && (
              <span className="text-slate-700 dark:text-slate-300 font-medium">
                {item.name}
              </span>
            )}
            {!item.isCurrent && index < breadcrumbItems.length - 1 && (
              <span className="mx-2">/</span>
            )}
          </>
        ))}
      </nav>

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

        {/* Theme toggle */}
        <button
          type="button"
          aria-label="Toggle theme"
          onClick={() => setTheme(theme === 'light' ? 'dark' : 'light')}
          className="rounded-lg p-2 text-slate-500 hover:bg-slate-100 hover:text-slate-900"
        >
          {theme === 'light' ? <Moon size={20} /> : <Sun size={20} />}
        </button>
      </div>
    </header>
  );
}

export default Header;
