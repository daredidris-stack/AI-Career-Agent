import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import {
  ArrowRight,
  BriefcaseBusiness,
  Check,
  Circle,
  FileText,
  LoaderCircle,
  RotateCcw,
  SlidersHorizontal,
  UserRound,
} from "lucide-react";

import api from "../services/api";

const stepDefinitions = [
  {
    id: "profile",
    title: "Build your career profile",
    description: (
      "Add your current role, target role, location, and skills so NextHire "
      + "can personalize the rest of the app."
    ),
    action: "Complete profile",
    to: "/profile",
    Icon: UserRound,
  },
  {
    id: "resume",
    title: "Add your resume",
    description: (
      "Upload a genuine PDF or DOCX resume to receive an analysis and create "
      + "the evidence used by matching and document tools."
    ),
    action: "Open Resume Studio",
    to: "/resume",
    Icon: FileText,
  },
  {
    id: "preferences",
    title: "Set your job preferences",
    description: (
      "Choose a country, work mode, or employment type in your profile so "
      + "job discovery starts with the right context."
    ),
    action: "Set preferences",
    to: "/profile",
    Icon: SlidersHorizontal,
  },
  {
    id: "application",
    title: "Find and track an opportunity",
    description: (
      "Search worldwide jobs, review the provider listing, and save a role "
      + "to Application Tracker when you are ready."
    ),
    action: "Search jobs",
    to: "/jobs",
    Icon: BriefcaseBusiness,
  },
];

function fallbackOnboarding(data) {
  const steps = {
    profile: !data.profile_missing,
    resume: data.resume_score != null,
    preferences: Boolean(
      data.profile?.preferred_job_type
      || data.profile?.preferred_work_mode
      || data.profile?.country,
    ),
    application: (
      Object.values(data.application_pipeline || {})
        .reduce((total, count) => total + count, 0) > 0
    ),
  };

  return {
    steps,
    completed_steps: Object.values(steps).filter(Boolean).length,
    total_steps: stepDefinitions.length,
    complete: Object.values(steps).every(Boolean),
  };
}

export default function Onboarding() {
  const [data, setData] = useState(null);
  const [error, setError] = useState("");
  const [reloadKey, setReloadKey] = useState(0);

  useEffect(() => {
    let active = true;

    async function loadProgress() {
      try {
        setError("");
        const response = await api.get("/dashboard", { timeout: 10000 });
        if (active) setData(response.data);
      } catch (requestError) {
        if (!active) return;
        if (requestError.code === "ECONNABORTED") {
          setError("Onboarding progress took too long to load. Please retry.");
        } else {
          setError(
            "Onboarding progress could not be loaded. Please try again.",
          );
        }
      }
    }

    loadProgress();
    return () => {
      active = false;
    };
  }, [reloadKey]);

  const onboarding = useMemo(() => {
    if (!data) return null;
    return data.onboarding || fallbackOnboarding(data);
  }, [data]);

  const nextStep = onboarding
    ? stepDefinitions.find((step) => !onboarding.steps[step.id])
    : null;
  const progress = onboarding
    ? Math.round(
      (onboarding.completed_steps / onboarding.total_steps) * 100,
    )
    : 0;

  if (!onboarding) {
    return (
      <div className="flex min-h-[60vh] items-center justify-center">
        {error ? (
          <div className="max-w-lg rounded-2xl border border-red-200 bg-white p-8 text-center shadow-sm">
            <h1 className="text-2xl font-bold text-slate-900">
              Getting started is unavailable
            </h1>
            <p className="mt-3 text-slate-600">{error}</p>
            <button
              type="button"
              onClick={() => setReloadKey((value) => value + 1)}
              className="mt-6 inline-flex items-center gap-2 rounded-xl bg-blue-600 px-5 py-3 font-semibold text-white hover:bg-blue-700"
            >
              <RotateCcw size={18} />
              Retry
            </button>
          </div>
        ) : (
          <div role="status" className="flex items-center gap-3 text-slate-600">
            <LoaderCircle size={22} className="animate-spin" />
            Loading your getting-started plan...
          </div>
        )}
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-5xl space-y-6">
      <section className="overflow-hidden rounded-3xl bg-gradient-to-br from-blue-700 via-indigo-700 to-violet-700 p-7 text-white shadow-xl sm:p-10">
        <div className="flex flex-col gap-7 lg:flex-row lg:items-end lg:justify-between">
          <div className="max-w-2xl">
            <p className="text-sm font-semibold uppercase tracking-[0.24em] text-blue-100">
              Getting started
            </p>
            <h1 className="mt-3 text-3xl font-bold sm:text-4xl">
              Build a stronger job-search foundation
            </h1>
            <p className="mt-4 max-w-xl text-base leading-7 text-blue-100 sm:text-lg">
              Complete these four steps in order. Your progress comes from
              saved account data, so it follows you whenever you return.
            </p>
          </div>

          <div className="min-w-56 rounded-2xl border border-white/20 bg-white/10 p-5 backdrop-blur">
            <div className="flex items-end justify-between gap-4">
              <span className="text-sm text-blue-100">Your progress</span>
              <strong className="text-3xl">{progress}%</strong>
            </div>
            <div
              role="progressbar"
              aria-label="Onboarding progress"
              aria-valuemin="0"
              aria-valuemax="100"
              aria-valuenow={progress}
              className="mt-4 h-2 overflow-hidden rounded-full bg-white/20"
            >
              <div
                className="h-full rounded-full bg-white transition-all"
                style={{ width: `${progress}%` }}
              />
            </div>
            <p className="mt-3 text-sm text-blue-100">
              {onboarding.completed_steps} of {onboarding.total_steps} steps complete
            </p>
          </div>
        </div>
      </section>

      {onboarding.complete ? (
        <section className="flex flex-col gap-5 rounded-2xl border border-emerald-200 bg-emerald-50 p-6 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h2 className="text-xl font-bold text-emerald-950">
              Your foundation is ready
            </h2>
            <p className="mt-2 text-emerald-800">
              Continue from the dashboard or revisit any step below.
            </p>
          </div>
          <Link
            to="/dashboard"
            className="inline-flex items-center justify-center gap-2 rounded-xl bg-emerald-700 px-5 py-3 font-semibold text-white hover:bg-emerald-800"
          >
            Open dashboard
            <ArrowRight size={18} />
          </Link>
        </section>
      ) : (
        <section className="flex flex-col gap-5 rounded-2xl border border-blue-200 bg-blue-50 p-6 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h2 className="text-xl font-bold text-blue-950">
              Next: {nextStep?.title}
            </h2>
            <p className="mt-2 text-blue-800">
              You can return to this guide from the sidebar at any time.
            </p>
          </div>
          {nextStep && (
            <Link
              to={nextStep.to}
              className="inline-flex items-center justify-center gap-2 rounded-xl bg-blue-700 px-5 py-3 font-semibold text-white hover:bg-blue-800"
            >
              {nextStep.action}
              <ArrowRight size={18} />
            </Link>
          )}
        </section>
      )}

      <ol className="grid gap-4">
        {stepDefinitions.map((step, index) => {
          const complete = Boolean(onboarding.steps[step.id]);
          const { Icon } = step;

          return (
            <li
              key={step.id}
              className={`rounded-2xl border bg-white p-6 shadow-sm ${
                complete ? "border-emerald-200" : "border-slate-200"
              }`}
            >
              <div className="flex flex-col gap-5 sm:flex-row sm:items-center">
                <div
                  className={`flex h-12 w-12 shrink-0 items-center justify-center rounded-2xl ${
                    complete
                      ? "bg-emerald-100 text-emerald-700"
                      : "bg-blue-100 text-blue-700"
                  }`}
                >
                  <Icon size={24} />
                </div>

                <div className="min-w-0 flex-1">
                  <div className="flex flex-wrap items-center gap-3">
                    <span className="text-sm font-semibold text-slate-400">
                      Step {index + 1}
                    </span>
                    <span
                      className={`inline-flex items-center gap-1 rounded-full px-2.5 py-1 text-xs font-semibold ${
                        complete
                          ? "bg-emerald-100 text-emerald-800"
                          : "bg-slate-100 text-slate-600"
                      }`}
                    >
                      {complete ? <Check size={14} /> : <Circle size={12} />}
                      {complete ? "Complete" : "Not complete"}
                    </span>
                  </div>
                  <h2 className="mt-2 text-xl font-bold text-slate-900">
                    {step.title}
                  </h2>
                  <p className="mt-2 max-w-2xl leading-6 text-slate-600">
                    {step.description}
                  </p>
                </div>

                <Link
                  to={step.to}
                  className="inline-flex shrink-0 items-center justify-center gap-2 rounded-xl border border-slate-300 px-4 py-2.5 font-semibold text-slate-700 hover:border-blue-300 hover:bg-blue-50 hover:text-blue-700"
                >
                  {complete ? "Review" : step.action}
                  <ArrowRight size={17} />
                </Link>
              </div>
            </li>
          );
        })}
      </ol>

      <p className="text-center text-sm text-slate-500">
        NextHire records progress only when the related account data is saved.
        Opening a page alone does not complete a step.
      </p>
    </div>
  );
}
