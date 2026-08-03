import { ArrowLeft, CircleHelp } from "lucide-react";
import { Link } from "react-router-dom";

export default function NotFound() {
  return (
    <section className="mx-auto max-w-2xl rounded-3xl border border-slate-200 bg-white p-10 text-center shadow-sm">
      <p className="text-sm font-bold uppercase tracking-[0.3em] text-blue-600">
        404
      </p>
      <h1 className="mt-3 text-3xl font-bold text-slate-900">
        This page does not exist
      </h1>
      <p className="mt-3 text-slate-600">
        The address may be outdated, or the page may have moved to another
        part of NextHire.
      </p>
      <div className="mt-7 flex flex-wrap justify-center gap-3">
        <Link
          to="/dashboard"
          className="inline-flex items-center gap-2 rounded-xl bg-blue-600 px-5 py-3 font-semibold text-white hover:bg-blue-700"
        >
          <ArrowLeft size={17} />
          Back to Dashboard
        </Link>
        <Link
          to="/help"
          className="inline-flex items-center gap-2 rounded-xl border border-slate-300 px-5 py-3 font-semibold text-slate-700 hover:border-blue-500 hover:text-blue-600"
        >
          <CircleHelp size={17} />
          Open Help Center
        </Link>
      </div>
    </section>
  );
}
