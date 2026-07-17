import { useEffect, useState } from "react";
import { Bell, Menu, Moon, Search } from "lucide-react";
import { useLocation, useNavigate } from "react-router-dom";

import { useAuth } from "../../hooks/useAuth";
import { getCurrentUser } from "../../services/api";
import UserMenu from "../header/UserMenu";

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
    "/applications": "Application Tracker",
    "/job-match": "Job Match",
    "/interview": "Interview Center",
    "/learning": "Learning",
    "/settings": "Settings",
    "/profile": "Profile",
    "/skill-gap": "Skill Gap Analysis",
  };

  const pageTitle =
    titles[location.pathname] || "NextHire AI";

  return (

    <header className="flex min-h-16 items-center justify-between gap-3 border-b border-gray-800 bg-gray-900 px-3 sm:px-6">

      {/* Left Side */}

      <div className="flex min-w-0 items-center gap-3 sm:gap-4">

        <button
          type="button"
          aria-label="Open navigation"
          onClick={onMenuOpen}
          className="shrink-0 rounded-lg p-2 text-gray-300 hover:bg-gray-800 hover:text-white md:hidden"
        >
          <Menu size={22} />
        </button>

        <h2 className="truncate text-base font-semibold text-white sm:text-xl">

          {pageTitle}

        </h2>

        <div className="hidden md:flex items-center bg-gray-800 rounded-lg px-3 py-2">

          <Search
            size={18}
            className="text-gray-400"
          />

          <input
            type="text"
            placeholder="Search..."
            className="bg-transparent outline-none text-white ml-2 placeholder-gray-500"
          />

        </div>

      </div>

      {/* Right Side */}

      <div className="flex shrink-0 items-center gap-1 sm:gap-4">

        <Bell
          className="hidden cursor-pointer text-gray-300 sm:block"
          size={20}
        />

        <Moon
          className="hidden cursor-pointer text-gray-300 sm:block"
          size={20}
        />

        <UserMenu
          firstName={user?.first_name || "User"}
          fullName={
              user
            ? `${user.first_name} ${user.last_name || ""}`.trim()
            : "User"
          }
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
