import { useEffect, useState } from "react";
import { Bell, Moon, Search } from "lucide-react";
import { useLocation } from "react-router-dom";

import { getCurrentUser } from "../../services/api";
import UserMenu from "../header/UserMenu";

function Header() {

  const location = useLocation();

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
    "/job-match": "Job Match",
    "/interview": "Interview Center",
    "/learning": "Learning",
    "/settings": "Settings",
    "/skill-gap": "Skill Gap Analysis",
  };

  const pageTitle =
    titles[location.pathname] || "NextHire AI";

  return (

    <header className="h-16 bg-gray-900 border-b border-gray-800 flex items-center justify-between px-6">

      {/* Left Side */}

      <div className="flex items-center gap-4">

        <h2 className="text-xl font-semibold text-white">

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

      <div className="flex items-center gap-5">

        <Bell
          className="text-gray-300 cursor-pointer"
          size={20}
        />

        <Moon
          className="text-gray-300 cursor-pointer"
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
            localStorage.removeItem("access_token");
            window.location.href = "/";
          }}
        />

      </div>

    </header>

  );

}

export default Header;
