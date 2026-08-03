import { useMemo, useState } from "react";
import { Search } from "lucide-react";
import { useNavigate } from "react-router-dom";

import { searchableHelpArticles } from "../../data/helpContent";

const destinations = [
  { title: "Dashboard", to: "/dashboard", keywords: "overview progress analytics" },
  { title: "Getting Started", to: "/onboarding", keywords: "onboarding setup guide checklist first steps" },
  { title: "Profile", to: "/profile", keywords: "career personal skills target role" },
  { title: "Resume Studio", to: "/resume", keywords: "resume ats upload documents" },
  { title: "Job Match", to: "/job-match", keywords: "compare score description" },
  { title: "Jobs", to: "/jobs", keywords: "search worldwide remote visa salary" },
  { title: "Job Library", to: "/job-library", keywords: "saved jobs searches alerts bookmarks" },
  { title: "Application Tracker", to: "/applications", keywords: "pipeline deadline follow up apply" },
  { title: "Resume Tailor", to: "/resume-tailor", keywords: "template targeted resume" },
  { title: "Cover Letter", to: "/cover-letter", keywords: "letter generate" },
  { title: "Skill Gap", to: "/skill-gap", keywords: "missing skills target role" },
  { title: "Interview Center", to: "/interview", keywords: "questions preparation practice" },
  { title: "Learning", to: "/learning", keywords: "plan course study skill" },
  { title: "Notifications", to: "/notifications", keywords: "reminder deadline follow up" },
  { title: "Settings and Billing", to: "/settings", keywords: "account export delete plan stripe" },
  { title: "Help Center", to: "/help", keywords: "support faq documentation" },
];

const searchItems = [
  ...destinations.map((item) => ({ ...item, kind: "Page" })),
  ...searchableHelpArticles.map((article) => ({
    title: article.title,
    to: `/help#${article.id}`,
    keywords: `${article.summary} ${article.keywords.join(" ")}`,
    kind: "Help",
  })),
];

export default function GlobalSearch() {
  const navigate = useNavigate();
  const [query, setQuery] = useState("");
  const normalized = query.trim().toLowerCase();

  const results = useMemo(() => {
    if (!normalized) return [];
    return searchItems
      .filter((item) =>
        `${item.title} ${item.keywords}`.toLowerCase().includes(normalized),
      )
      .slice(0, 7);
  }, [normalized]);

  function chooseResult(result) {
    setQuery("");
    navigate(result.to);
  }

  function submit(event) {
    event.preventDefault();
    if (results[0]) chooseResult(results[0]);
  }

  return (
    <form onSubmit={submit} className="relative hidden md:block">
      <div className="flex items-center rounded-lg border border-slate-200 bg-slate-50 px-3 py-2 focus-within:border-blue-500 focus-within:bg-white">
        <Search size={18} className="text-slate-500" />
        <input
          type="search"
          value={query}
          onChange={(event) => setQuery(event.target.value)}
          onKeyDown={(event) => {
            if (event.key === "Escape") setQuery("");
          }}
          aria-label="Search NextHire"
          placeholder="Search NextHire..."
          className="ml-2 w-52 bg-transparent text-slate-900 outline-none placeholder:text-slate-400"
        />
      </div>

      {normalized && (
        <div className="absolute left-0 top-full z-50 mt-2 w-80 overflow-hidden rounded-xl border border-slate-200 bg-white shadow-xl">
          {results.length ? (
            <ul>
              {results.map((result) => (
                <li key={`${result.kind}:${result.to}`}>
                  <button
                    type="button"
                    onClick={() => chooseResult(result)}
                    className="flex w-full items-center justify-between gap-3 border-b border-slate-100 px-4 py-3 text-left text-sm text-slate-700 last:border-0 hover:bg-slate-50"
                  >
                    <span className="font-medium">{result.title}</span>
                    <span className="text-xs uppercase tracking-wide text-slate-400">
                      {result.kind}
                    </span>
                  </button>
                </li>
              ))}
            </ul>
          ) : (
            <p className="px-4 py-4 text-sm text-slate-500">
              No matching page or help article.
            </p>
          )}
        </div>
      )}
    </form>
  );
}
