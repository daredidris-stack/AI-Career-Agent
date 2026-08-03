import { useState } from "react";
import { Link, useSearchParams } from "react-router-dom";

import api from "../services/api";
import { AuthCard } from "./auth/ForgotPassword";


export default function EmailPreferences() {
  const [params] = useSearchParams();
  const [message, setMessage] = useState("");
  const [failed, setFailed] = useState(false);
  const [loading, setLoading] = useState(false);
  const token = params.get("token") || "";

  async function unsubscribe() {
    setLoading(true);
    setMessage("");
    setFailed(false);
    try {
      const response = await api.post(
        "/job-library/email-alerts/unsubscribe",
        { token },
      );
      setMessage(response.data.message);
    } catch (requestError) {
      setFailed(true);
      setMessage(
        requestError.response?.data?.detail
          || "This email preference could not be changed.",
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <AuthCard
      title="Email alert preferences"
      description="This link controls one saved-search alert. Opening the page does not change your preference."
    >
      <div className="space-y-4">
        {message && (
          <p
            role={failed ? "alert" : "status"}
            className={`rounded-xl p-3 text-sm ${
              failed
                ? "bg-red-500/10 text-red-200"
                : "bg-emerald-500/10 text-emerald-200"
            }`}
          >
            {message}
          </p>
        )}
        {!message || failed ? (
          <button
            type="button"
            onClick={unsubscribe}
            disabled={loading || !token}
            className="w-full rounded-xl bg-red-600 px-4 py-3 font-semibold text-white disabled:cursor-not-allowed disabled:opacity-50"
          >
            {loading ? "Updating..." : "Turn off this email alert"}
          </button>
        ) : null}
        <Link
          to="/login"
          className="block text-center text-sm font-semibold text-blue-400"
        >
          Sign in to manage all saved searches
        </Link>
      </div>
    </AuthCard>
  );
}
