import {
  LayoutDashboard,
  FileText,
  Briefcase,
  GraduationCap,
  MessageSquare,
  Settings,
  FileSignature,
  Target,
  Sparkles,
  UserRound,
  SearchCheck,
} from "lucide-react";

import { NavLink } from "react-router-dom";


const menuItems = [

  {
    name: "Dashboard",
    path: "/",
    icon: LayoutDashboard,
  },

  {
    name: "Skill Gap",
    path: "/skill-gap",
    icon: Briefcase,
  },

  {
    name: "Profile",
    path: "/profile",
    icon: UserRound,
  },

  {
    name: "Resume Studio",
    path: "/resume",
    icon: FileText,
  },

  {
    name: "Job Match",
    path: "/job-match",
    icon: Target,
  },

  {
    name: "Jobs",
    path: "/jobs",
    icon: SearchCheck,
  },

  {
    name: "Resume Tailor",
    path: "/resume-tailor",
    icon: Sparkles,
  },
  {
    name: "Cover Letter",
    path: "/cover-letter",
    icon: FileSignature,
  },

  {
    name: "Interview Center",
    path: "/interview",
    icon: MessageSquare,
  },

  {
    name: "Learning",
    path: "/learning",
    icon: GraduationCap,
  },

  {
    name: "Settings",
    path: "/settings",
    icon: Settings,
  },

];


function Sidebar() {

  return (

    <aside className="w-64 bg-gray-900 text-white min-h-screen border-r border-gray-800">

      <div className="p-6 border-b border-gray-800">

        <h1 className="text-2xl font-bold text-blue-400">
          CareerPilot AI
        </h1>

        <p className="text-sm text-gray-400 mt-1">
          AI Career Copilot
        </p>

      </div>


      <nav className="mt-6 px-3">

        {menuItems.map((item) => {

          const Icon = item.icon;

          return (

            <NavLink
              key={item.name}
              to={item.path}

              className={({ isActive }) =>
                `flex items-center gap-3 px-4 py-3 rounded-lg mb-2 transition ${
                  isActive
                    ? "bg-blue-600 text-white"
                    : "text-gray-300 hover:bg-gray-800"
                }`
              }
            >

              <Icon size={20} />

              <span>
                {item.name}
              </span>

            </NavLink>

          );

        })}

      </nav>

    </aside>

  );
}


export default Sidebar;
