import { useEffect, useMemo, useState } from "react";
import {
  ArrowRight,
  BookOpen,
  MessageCircle,
  Search,
  Send,
} from "lucide-react";
import { Link } from "react-router-dom";

import { helpSections } from "../data/helpContent";
import api from "../services/api";

export default function HelpCenter() {
  const [query, setQuery] = useState("");
  const [tickets, setTickets] = useState([]);
  const [category, setCategory] = useState("feedback");
  const [subject, setSubject] = useState("");
  const [message, setMessage] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [supportError, setSupportError] = useState("");
  const [supportMessage, setSupportMessage] = useState("");
  const normalized = query.trim().toLowerCase();

  const visibleSections = useMemo(() => {
    if (!normalized) return helpSections;
    return helpSections
      .map((section) => ({
        ...section,
        articles: section.articles.filter((article) =>
          [
            article.title,
            article.summary,
            section.title,
            ...article.keywords,
          ].join(" ").toLowerCase().includes(normalized),
        ),
      }))
      .filter((section) => section.articles.length);
  }, [normalized]);

  useEffect(() => {
    if (!window.location.hash) return;
    const target = document.getElementById(window.location.hash.slice(1));
    target?.scrollIntoView({ block: "start" });
  }, []);

  useEffect(() => {
    let active = true;
    api.get("/support/tickets")
      .then((response) => {
        if (active) setTickets(response.data);
      })
      .catch(() => {
        // Help articles remain usable if support history cannot be loaded.
      });
    return () => {
      active = false;
    };
  }, []);

  async function submitSupportRequest(event) {
    event.preventDefault();
    setSubmitting(true);
    setSupportError("");
    setSupportMessage("");
    try {
      const response = await api.post("/support/tickets", {
        category,
        subject: subject.trim(),
        message: message.trim(),
      });
      setTickets((current) => [response.data, ...current]);
      setSubject("");
      setMessage("");
      setSupportMessage(
        "Your request was received. You can follow its status below.",
      );
    } catch (requestError) {
      setSupportError(
        requestError.response?.data?.detail
          || "Your support request could not be sent.",
      );
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="space-y-8">
      <section className="rounded-3xl bg-gradient-to-r from-blue-600 to-indigo-700 p-8 text-white shadow-xl">
        <div className="flex items-center gap-3">
          <BookOpen size={32} />
          <h1 className="text-3xl font-bold sm:text-4xl">Help Center</h1>
        </div>
        <p className="mt-3 max-w-3xl text-lg text-blue-100">
          Learn how to use every NextHire workflow and understand which
          production integrations affect availability.
        </p>

        <label className="mt-7 flex max-w-2xl items-center rounded-2xl bg-white px-4 py-3 text-slate-900 shadow-lg">
          <Search size={20} className="text-slate-500" />
          <span className="sr-only">Search help articles</span>
          <input
            type="search"
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            placeholder="Search account, resume, jobs, applications..."
            className="ml-3 w-full bg-transparent outline-none placeholder:text-slate-400"
          />
        </label>
      </section>

      <nav
        aria-label="Help categories"
        className="flex flex-wrap gap-2"
      >
        {helpSections.map((section) => (
          <a
            key={section.id}
            href={`#${section.id}`}
            className="rounded-full border border-slate-300 bg-white px-4 py-2 text-sm font-medium text-slate-700 hover:border-blue-500 hover:text-blue-600"
          >
            {section.title}
          </a>
        ))}
      </nav>

      {visibleSections.length ? (
        visibleSections.map((section) => (
          <section
            key={section.id}
            id={section.id}
            className="scroll-mt-24"
          >
            <h2 className="text-2xl font-bold text-slate-900">{section.title}</h2>
            <p className="mt-2 text-slate-600">{section.description}</p>
            <div className="mt-5 grid gap-5 lg:grid-cols-2">
              {section.articles.map((article) => (
                <article
                  key={article.id}
                  id={article.id}
                  className="scroll-mt-24 rounded-2xl border border-slate-200 bg-white p-6 shadow-sm"
                >
                  <h3 className="text-lg font-bold text-slate-900">
                    {article.title}
                  </h3>
                  <p className="mt-3 text-sm leading-6 text-slate-600">
                    {article.summary}
                  </p>
                  <div className="mt-5 flex flex-wrap gap-3">
                    {article.links.map((link) => (
                      <Link
                        key={`${article.id}:${link.to}`}
                        to={link.to}
                        className="inline-flex items-center gap-2 text-sm font-semibold text-blue-600 hover:text-blue-700"
                      >
                        {link.label}
                        <ArrowRight size={15} />
                      </Link>
                    ))}
                  </div>
                </article>
              ))}
            </div>
          </section>
        ))
      ) : (
        <section className="rounded-2xl border border-dashed border-slate-300 bg-white p-10 text-center">
          <h2 className="text-xl font-bold text-slate-900">No article found</h2>
          <p className="mt-2 text-slate-600">
            Try a feature name such as resume, Google, jobs, billing, or
            applications.
          </p>
          <button
            type="button"
            onClick={() => setQuery("")}
            className="mt-5 rounded-xl bg-blue-600 px-5 py-3 font-semibold text-white hover:bg-blue-700"
          >
            Show all help
          </button>
        </section>
      )}

      <section
        id="contact-support"
        className="scroll-mt-24 rounded-3xl border border-slate-200 bg-white p-6 shadow-sm md:p-8"
      >
        <div className="flex items-start gap-3">
          <span className="rounded-xl bg-blue-100 p-3 text-blue-700">
            <MessageCircle size={24} />
          </span>
          <div>
            <h2 className="text-2xl font-bold text-slate-900">
              Send feedback or ask for help
            </h2>
            <p className="mt-2 max-w-2xl text-slate-600">
              Describe what you were trying to do and what happened. Do not
              include passwords, payment details, government identifiers, or
              API keys.
            </p>
          </div>
        </div>

        <form
          onSubmit={submitSupportRequest}
          className="mt-6 grid gap-4 lg:grid-cols-2"
        >
          <label>
            <span className="mb-2 block text-sm font-semibold text-slate-700">
              Topic
            </span>
            <select
              value={category}
              onChange={(event) => setCategory(event.target.value)}
              className="w-full rounded-xl border border-slate-300 bg-white px-4 py-3 text-slate-950 outline-none focus:border-blue-500"
            >
              <option value="feedback">Product feedback</option>
              <option value="bug">Something is not working</option>
              <option value="account">Account or sign-in</option>
              <option value="jobs">Jobs or saved searches</option>
              <option value="documents">Resume or documents</option>
              <option value="applications">Applications</option>
              <option value="billing">Billing</option>
              <option value="other">Other</option>
            </select>
          </label>
          <label>
            <span className="mb-2 block text-sm font-semibold text-slate-700">
              Subject
            </span>
            <input
              value={subject}
              onChange={(event) => setSubject(event.target.value)}
              required
              minLength={3}
              maxLength={200}
              placeholder="Short description"
              className="w-full rounded-xl border border-slate-300 px-4 py-3 text-slate-950 outline-none focus:border-blue-500"
            />
          </label>
          <label className="lg:col-span-2">
            <span className="mb-2 block text-sm font-semibold text-slate-700">
              Details
            </span>
            <textarea
              value={message}
              onChange={(event) => setMessage(event.target.value)}
              required
              minLength={10}
              maxLength={10000}
              rows={5}
              placeholder="What did you expect, and what happened instead?"
              className="w-full rounded-xl border border-slate-300 px-4 py-3 text-slate-950 outline-none focus:border-blue-500"
            />
          </label>

          {supportError && (
            <p
              role="alert"
              className="rounded-xl border border-red-300 bg-red-50 p-4 text-red-700 lg:col-span-2"
            >
              {supportError}
            </p>
          )}
          {supportMessage && (
            <p
              role="status"
              className="rounded-xl border border-emerald-300 bg-emerald-50 p-4 text-emerald-800 lg:col-span-2"
            >
              {supportMessage}
            </p>
          )}

          <div className="lg:col-span-2">
            <button
              type="submit"
              disabled={submitting}
              className="inline-flex items-center gap-2 rounded-xl bg-blue-600 px-5 py-3 font-semibold text-white hover:bg-blue-700 disabled:cursor-wait disabled:opacity-60"
            >
              <Send size={17} />
              {submitting ? "Sending..." : "Send request"}
            </button>
          </div>
        </form>

        {tickets.length > 0 && (
          <div className="mt-8 border-t border-slate-200 pt-6">
            <h3 className="text-lg font-bold text-slate-900">
              Your recent requests
            </h3>
            <div className="mt-4 space-y-3">
              {tickets.slice(0, 5).map((ticket) => (
                <article
                  key={ticket.id}
                  className="flex flex-col gap-2 rounded-xl bg-slate-50 p-4 sm:flex-row sm:items-center sm:justify-between"
                >
                  <div>
                    <p className="font-semibold text-slate-900">
                      {ticket.subject}
                    </p>
                    <p className="mt-1 text-xs text-slate-500">
                      Sent {new Date(ticket.created_at).toLocaleDateString()}
                    </p>
                  </div>
                  <span className="w-fit rounded-full bg-white px-3 py-1 text-xs font-bold uppercase tracking-wide text-slate-600">
                    {ticket.status.replace("_", " ")}
                  </span>
                </article>
              ))}
            </div>
          </div>
        )}
      </section>
    </div>
  );
}
