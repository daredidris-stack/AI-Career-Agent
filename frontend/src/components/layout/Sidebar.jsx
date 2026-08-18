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
  LibraryBig,
  ClipboardList,
  ListChecks,
  X,
} from "lucide-react";

import { NavLink } from "react-router-dom";


const menuItems = [

  {
    name: "Dashboard",
    path: "/dashboard",
    icon: LayoutDashboard,
  },

  {
    name: "Getting Started",
    path: "/onboarding",
    icon: ListChecks,
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
    name: "Job Library",
    path: "/job-library",
    icon: LibraryBig,
  },

  {
    name: "Application Tracker",
    path: "/applications",
    icon: ClipboardList,
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


function Sidebar({ mobileOpen = false, onClose, collapsed = false, onToggleCollapse }) {

  return (

    <>
    {mobileOpen && (
      <button
        type="button"
        aria-label="Close navigation"
        onClick={onClose}
        className="fixed inset-0 z-40 bg-black/60 md:hidden"
      />
    )}
    <aside className={`fixed inset-y-0 left-0 z-50 ${collapsed ? 'w-16' : 'w-72'} max-w-[85vw] overflow-y-auto border-r border-slate-200 bg-white text-slate-900 shadow-xl transition-transform duration-200 md:sticky md:top-0 md:z-auto md:block md:h-screen md:shrink-0 md:translate-x-0 md:shadow-none ${mobileOpen ? "translate-x-0" : "-translate-x-full"}`}>

      <div className="flex items-start justify-between border-b border-slate-200 p-4">

        <div className="flex items-center gap-3">

          {!collapsed && (
            <>
            <h1 className="text-xl font-bold text-blue-400">
              NextHire AI
            </h1>

            <p className="mt-0 text-xs text-slate-500">
              AI Career Copilot
            </p>
            </>
          )}

          {collapsed && (
            <button
              type="button"
              aria-label="Open sidebar"
              onClick={onToggleCollapse}
              className="rounded-lg p-3 text-slate-500 hover:bg-slate-100 hover:text-slate-900"
            >
              <LayoutDashboard size={24} />
            </button>
          )}

        </div>

        <button
          type="button"
          aria-label="Close navigation"
          onClick={onClose}
          className="rounded-lg p-2 text-slate-500 hover:bg-slate-100 hover:text-slate-900 md:hidden"
        >
          <X size={20} />
        </button>

      </div>


      <nav className="mt-4 px-2">

        {menuItems.map((item) => {

          const Icon = item.icon;

          return (

            <NavLink
              key={item.name}
              to={item.path}
              onClick={onClose}

              className={({ isActive }) =>
                `flex items-center gap-2 px-3 py-2 rounded-md mb-1 transition ${
                  isActive
                    ? "bg-blue-600 text-white"
                    : "text-slate-600 hover:bg-slate-100 hover:text-slate-900"
                }`
              }
            >

              <Icon size={20} />

              {!collapsed && (
                <span>{item.name}</span>
              )}

            </NavLink>

          );

        })}

      </nav>

    </aside>
    </>

  );
}


export default Sidebar;
