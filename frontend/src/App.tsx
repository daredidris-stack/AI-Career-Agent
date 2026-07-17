import { lazy, Suspense } from "react";
import { Routes, Route } from "react-router-dom";

import AppLayout from "./layouts/AppLayout";
import ProtectedRoute from "./routes/ProtectedRoute";

const Dashboard = lazy(() => import("./pages/Dashboard"));
const SkillGap = lazy(() => import("./pages/SkillGap"));
const Resume = lazy(() => import("./pages/Resume"));
const Jobs = lazy(() => import("./pages/Jobs"));
const Interview = lazy(() => import("./pages/Interview"));
const Learning = lazy(() => import("./pages/Learning"));
const Settings = lazy(() => import("./pages/Settings"));
const JobMatch = lazy(() => import("./pages/JobMatch"));
const ResumeTailor = lazy(() => import("./pages/ResumeTailor"));
const CoverLetter = lazy(() => import("./pages/CoverLetter"));
const Applications = lazy(() => import("./pages/Applications"));
const Terms = lazy(() => import("./pages/Terms"));
const PrivacyNotice = lazy(() => import("./pages/PrivacyNotice"));
const Login = lazy(() => import("./pages/auth/Login"));
const Register = lazy(() => import("./pages/auth/Register"));
const ForgotPassword = lazy(() => import("./pages/auth/ForgotPassword"));
const ResetPassword = lazy(() => import("./pages/auth/ResetPassword"));
const VerifyEmail = lazy(() => import("./pages/auth/VerifyEmail"));
const Profile = lazy(() => import("./pages/Profile"));

function RouteFallback() {
  return (
    <div
      role="status"
      className="flex min-h-screen items-center justify-center bg-gray-950 text-gray-300"
    >
      Loading NextHire AI...
    </div>
  );
}


export default function App() {

  return (

    <Suspense fallback={<RouteFallback />}>
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
      <Route path="/terms" element={<Terms />} />
      <Route path="/privacy" element={<PrivacyNotice />} />


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
    </Suspense>

  );
}
