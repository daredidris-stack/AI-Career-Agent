import { Routes, Route } from "react-router-dom";

import AppLayout from "./layouts/AppLayout";
import ProtectedRoute from "./routes/ProtectedRoute";

import Dashboard from "./pages/Dashboard";
import SkillGap from "./pages/SkillGap";
import Resume from "./pages/Resume";
import Jobs from "./pages/Jobs";
import Interview from "./pages/Interview";
import Learning from "./pages/Learning";
import Settings from "./pages/Settings";
import JobMatch from "./pages/JobMatch";
import ResumeTailor from "./pages/ResumeTailor";
import CoverLetter from "./pages/CoverLetter";
import Applications from "./pages/Applications";

import Login from "./pages/auth/Login";
import Register from "./pages/auth/Register";
import ForgotPassword from "./pages/auth/ForgotPassword";
import ResetPassword from "./pages/auth/ResetPassword";
import VerifyEmail from "./pages/auth/VerifyEmail";
import Profile from "./pages/Profile";


export default function App() {

  return (

    <Routes>

      {/* Public routes */}

      <Route
        path="/login"
        element={<Login />}
      />


      <Route
        path="/register"
        element={<Register />}
      />

      <Route path="/forgot-password" element={<ForgotPassword />} />
      <Route path="/reset-password" element={<ResetPassword />} />
      <Route path="/verify-email" element={<VerifyEmail />} />


      {/* Application routes */}

      <Route
        element={
          <ProtectedRoute>
            <AppLayout />
          </ProtectedRoute>
        }
      >

        <Route
          path="/"
          element={<Dashboard />}
        />

        <Route
          path="/dashboard"
          element={<Dashboard />}
        />

        <Route
          path="/resume"
          element={<Resume />}
        />

        <Route
          path="/jobs"
          element={<Jobs />}
        />

        <Route
          path="/skill-gap"
          element={<SkillGap />}
        />

        <Route
          path="/interview"
          element={<Interview />}
        />

        <Route
          path="/learning"
          element={<Learning />}
        />

        <Route
          path="/settings"
          element={<Settings />}
        />

        <Route
          path="/job-match"
          element={<JobMatch />}
        />

        <Route
          path="/resume-tailor"
          element={<ResumeTailor />}
        />

        <Route
          path="/cover-letter"
          element={<CoverLetter />}
        />

        <Route
          path="/profile"
          element={<Profile />}
        />

        <Route
          path="/applications"
          element={<Applications />}
        />

      </Route>


    </Routes>

  );
}
