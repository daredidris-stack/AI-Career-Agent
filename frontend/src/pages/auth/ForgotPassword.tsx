import { useState, type FormEvent, type ReactNode } from "react";
import { Link } from "react-router-dom";

import api from "../../services/api";


export default function ForgotPassword() {
  const [email, setEmail] = useState("");
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(false);

  async function submit(event: FormEvent) {
    event.preventDefault();
    setLoading(true);
    try {
      const response = await api.post("/auth/password/forgot", { email });
      setMessage(response.data.message);
    } catch {
      setMessage("Unable to request a reset right now. Please try again.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <AuthCard title="Reset your password" description="Enter your account email and we will send a secure reset link.">
      <form onSubmit={submit} className="space-y-5">
        {message && <p role="status" className="rounded-xl bg-blue-500/10 p-3 text-sm text-blue-200">{message}</p>}
        <input type="email" value={email} onChange={(event) => setEmail(event.target.value)} required autoComplete="email" placeholder="you@example.com" className="w-full rounded-xl border border-gray-700 bg-gray-950 px-4 py-3 text-white outline-none focus:border-blue-500" />
        <button disabled={loading} className="w-full rounded-xl bg-blue-600 px-4 py-3 font-semibold text-white disabled:opacity-50">{loading ? "Sending..." : "Send reset link"}</button>
        <Link to="/login" className="block text-center text-sm text-blue-400">Back to login</Link>
      </form>
    </AuthCard>
  );
}


export function AuthCard({
  title,
  description,
  children,
}: {
  title: string;
  description: string;
  children: ReactNode;
}) {
  return (
    <main className="flex min-h-screen items-center justify-center bg-gray-950 px-4">
      <section className="w-full max-w-md rounded-3xl border border-gray-800 bg-gray-900 p-8 shadow-2xl">
        <p className="text-sm font-semibold uppercase tracking-widest text-blue-400">NextHire AI</p>
        <h1 className="mt-5 text-3xl font-bold text-white">{title}</h1>
        <p className="mt-3 mb-8 text-sm leading-6 text-gray-400">{description}</p>
        {children}
      </section>
    </main>
  );
}
