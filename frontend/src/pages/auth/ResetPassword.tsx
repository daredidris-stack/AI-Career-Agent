import { useState, type FormEvent } from "react";
import { Link, useSearchParams } from "react-router-dom";

import api from "../../services/api";
import { AuthCard } from "./ForgotPassword";


export default function ResetPassword() {
  const [params] = useSearchParams();
  const [password, setPassword] = useState("");
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  async function submit(event: FormEvent) {
    event.preventDefault();
    setError("");
    try {
      const response = await api.post("/auth/password/reset", {
        token: params.get("token") || "",
        new_password: password,
      });
      setMessage(response.data.message);
    } catch (requestError: any) {
      setError(requestError.response?.data?.detail || "Password reset failed.");
    }
  }

  return (
    <AuthCard title="Choose a new password" description="Use at least eight characters and keep it unique to this account.">
      <form onSubmit={submit} className="space-y-5">
        {message && <p className="text-emerald-300">{message}</p>}
        {error && <p role="alert" className="text-red-300">{error}</p>}
        {!message && <><input type="password" minLength={8} maxLength={128} value={password} onChange={(event) => setPassword(event.target.value)} required autoComplete="new-password" className="w-full rounded-xl border border-gray-700 bg-gray-950 px-4 py-3 text-white outline-none focus:border-blue-500" /><button className="w-full rounded-xl bg-blue-600 px-4 py-3 font-semibold text-white">Reset password</button></>}
        <Link to="/login" className="block text-center text-sm text-blue-400">Return to login</Link>
      </form>
    </AuthCard>
  );
}
