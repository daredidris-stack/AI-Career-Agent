import { useEffect, useState } from "react";
import { Outlet } from "react-router-dom";
import { Link } from "react-router-dom";

import Sidebar from "../components/layout/Sidebar";
import Header from "../components/layout/Header";


export default function AppLayout() {

  const [mobileNavigationOpen, setMobileNavigationOpen] = useState(false);
  const [sidebarCollapsed, setSidebarCollapsed] = useState(() => {
    const saved = localStorage.getItem('sidebarCollapsed');
    return saved ? JSON.parse(saved) : false;
  });

  useEffect(() => {
    localStorage.setItem('sidebarCollapsed', JSON.stringify(sidebarCollapsed));
  }, [sidebarCollapsed]);

  useEffect(() => {
    if (!mobileNavigationOpen) return undefined;
    function closeOnEscape(event: KeyboardEvent) {
      if (event.key === "Escape") setMobileNavigationOpen(false);
    }
    document.addEventListener("keydown", closeOnEscape);
    return () => document.removeEventListener("keydown", closeOnEscape);
  }, [mobileNavigationOpen]);

  return (

    <div
      className="
        flex
        min-h-screen
        bg-gray-50
      "
    >
      <a
        href="#main-content"
        className="sr-only fixed left-4 top-4 z-[100] rounded-lg bg-blue-700 px-4 py-3 font-semibold text-white focus:not-sr-only"
      >
        Skip to main content
      </a>

      <Sidebar
        mobileOpen={mobileNavigationOpen}
        onClose={() => setMobileNavigationOpen(false)}
        collapsed={sidebarCollapsed}
        onToggleCollapse={setSidebarCollapsed}
      />


      <div
        className="
          min-w-0
          flex-1
          flex
          flex-col
        "
      >

        <Header
          onMenuOpen={() => setMobileNavigationOpen(true)}
          onToggleSidebar={() => setSidebarCollapsed(!sidebarCollapsed)}
          sidebarCollapsed={sidebarCollapsed}
        />


        <main
          id="main-content"
          tabIndex={-1}
          className="
            flex-1
            p-4
            sm:p-6
          "
        >

          <Outlet />

        </main>

        <footer className="flex flex-wrap justify-center gap-5 border-t border-slate-200 bg-white px-6 py-4 text-xs text-slate-500">
          <Link to="/help" className="hover:text-slate-900">Help Center</Link>
          <Link to="/terms" className="hover:text-slate-900">Terms</Link>
          <Link to="/privacy" className="hover:text-slate-900">Privacy</Link>
          <span>Job listings are supplied by identified third-party providers.</span>
        </footer>


      </div>


    </div>

  );
}
