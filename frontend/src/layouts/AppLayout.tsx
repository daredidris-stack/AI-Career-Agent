import { useState } from "react";
import { Outlet } from "react-router-dom";
import { Link } from "react-router-dom";

import Sidebar from "../components/layout/Sidebar";
import Header from "../components/layout/Header";


export default function AppLayout() {

  const [mobileNavigationOpen, setMobileNavigationOpen] = useState(false);


  return (

    <div
      className="
        flex
        min-h-screen
        bg-gray-50
      "
    >

      <Sidebar
        mobileOpen={mobileNavigationOpen}
        onClose={() => setMobileNavigationOpen(false)}
      />


      <div
        className="
          min-w-0
          flex-1
          flex
          flex-col
        "
      >

        <Header onMenuOpen={() => setMobileNavigationOpen(true)} />


        <main
          className="
            flex-1
            p-4
            sm:p-6
          "
        >

          <Outlet />

        </main>

        <footer className="flex flex-wrap justify-center gap-5 border-t border-gray-800 bg-gray-950 px-6 py-4 text-xs text-gray-500">
          <Link to="/terms" className="hover:text-gray-300">Terms</Link>
          <Link to="/privacy" className="hover:text-gray-300">Privacy</Link>
          <span>Job listings are supplied by identified third-party providers.</span>
        </footer>


      </div>


    </div>

  );

}
