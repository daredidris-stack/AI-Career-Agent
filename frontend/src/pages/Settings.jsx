import { useState } from "react";
import { useNavigate } from "react-router-dom";

import { useAuth } from "../hooks/useAuth";
import api from "../services/api";


function Settings() {
  const navigate = useNavigate();
  const { logout } = useAuth();
  const [password, setPassword] = useState("");
  const [confirmation, setConfirmation] = useState("");
  const [error, setError] = useState("");
  const [deleting, setDeleting] = useState(false);
  const [exporting, setExporting] = useState(false);

  async function exportAccountData() {
    setExporting(true);
    setError("");
    try {
      const response = await api.get("/users/me/export");
      const blob = new Blob(
        [JSON.stringify(response.data, null, 2)],
        { type: "application/json" },
      );
      const url = URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = "nexthire-data-export.json";
      link.click();
      URL.revokeObjectURL(url);
    } catch (requestError) {
      setError(requestError.response?.data?.detail || "Data export failed.");
    } finally {
      setExporting(false);
    }
  }

  async function deleteAccount(event) {
    event.preventDefault();
    if (confirmation !== "DELETE") {
      setError("Type DELETE to confirm account deletion.");
      return;
    }

    setDeleting(true);
    setError("");
    try {
      await api.delete("/users/me", { data: { password } });
      logout();
      navigate("/login", { replace: true });
    } catch (requestError) {
      setError(
        requestError.response?.data?.detail
          || "Account deletion failed. Please try again.",
      );
    } finally {
      setDeleting(false);
    }
  }

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-4xl font-bold text-white">Settings</h1>
        <p className="mt-2 text-gray-400">Manage your account and security.</p>
      </div>

      <section className="max-w-2xl rounded-2xl border border-gray-800 bg-gray-900 p-6">
        <h2 className="text-xl font-bold text-white">Your data</h2>
        <p className="mt-2 text-sm leading-6 text-gray-400">
          Download a JSON copy of your account, profile, resume analyses,
          documents, applications, revisions, and AI usage history.
        </p>
        <button type="button" onClick={exportAccountData} disabled={exporting} className="mt-5 rounded-xl bg-blue-600 px-5 py-3 font-semibold text-white hover:bg-blue-700 disabled:opacity-50">
          {exporting ? "Preparing export..." : "Download my data"}
        </button>
      </section>

      <section className="max-w-2xl rounded-2xl border border-red-500/30 bg-gray-900 p-6">
        <h2 className="text-xl font-bold text-white">Delete account</h2>
        <p className="mt-2 text-sm leading-6 text-gray-400">
          This permanently deletes your account, profile, resume analyses,
          documents and revisions, job applications, and AI usage history.
          This action cannot be undone.
        </p>

        <form onSubmit={deleteAccount} className="mt-6 space-y-4">
          {error && <p role="alert" className="text-sm text-red-300">{error}</p>}
          <label className="block">
            <span className="mb-2 block text-sm text-gray-300">Current password</span>
            <input type="password" value={password} onChange={(event) => setPassword(event.target.value)} required autoComplete="current-password" className="w-full rounded-xl border border-gray-700 bg-gray-950 px-4 py-3 text-white outline-none focus:border-red-500" />
          </label>
          <label className="block">
            <span className="mb-2 block text-sm text-gray-300">Type DELETE to confirm</span>
            <input value={confirmation} onChange={(event) => setConfirmation(event.target.value)} required className="w-full rounded-xl border border-gray-700 bg-gray-950 px-4 py-3 text-white outline-none focus:border-red-500" />
          </label>
          <button type="submit" disabled={deleting} className="rounded-xl bg-red-600 px-5 py-3 font-semibold text-white hover:bg-red-700 disabled:opacity-50">
            {deleting ? "Deleting..." : "Permanently delete account"}
          </button>
        </form>
      </section>
    </div>
  );
}

export default Settings;
