import { useEffect, useState } from "react";
import {
  CalendarDays,
  CheckCircle2,
  ClipboardCheck,
  MessageSquare,
  Sparkles,
  Target,
} from "lucide-react";

import { getProfile } from "../services/api";


const INTERVIEW_TYPES = [
  "General interview",
  "Technical interview",
  "Behavioral interview",
  "System design interview",
];

const QUESTION_SETS = {
  "Technical interview": [
    "Explain a difficult technical problem you solved and the tradeoffs you considered.",
    "How would you diagnose a production service that suddenly became slow?",
    "Describe how you test and safely deploy a change.",
    "Which tools in your current stack do you understand most deeply?",
  ],
  "Behavioral interview": [
    "Tell me about a time you handled a high-pressure incident.",
    "Describe a disagreement with a teammate and how you resolved it.",
    "Give an example of a process you improved.",
    "Tell me about a mistake and what you changed afterward.",
  ],
  "System design interview": [
    "Design a reliable service that can handle sudden traffic growth.",
    "How would you remove single points of failure from a production system?",
    "Explain your choices for storage, caching, monitoring, and scaling.",
    "How would you estimate capacity and test the design before launch?",
  ],
  "General interview": [
    "Walk me through your background and why this role is your next step.",
    "Why are you interested in this company and position?",
    "Which accomplishment best demonstrates your fit for this role?",
    "What would you aim to accomplish in your first 90 days?",
  ],
};

function buildPlan(role, interviewType, days) {
  const availableDays = Math.max(1, Number(days) || 1);
  const phases = [
    {
      title: "Understand the opportunity",
      description: `Study the ${role} requirements, research the company, and identify the five qualifications the interviewer is most likely to test.`,
    },
    {
      title: "Build your evidence",
      description: "Prepare concise STAR examples for impact, teamwork, problem solving, ownership, and learning from failure.",
    },
    {
      title: `Practice the ${interviewType.toLowerCase()}`,
      description: "Answer questions aloud, time your responses, and improve answers that lack a clear action or measurable result.",
    },
    {
      title: "Run a final rehearsal",
      description: "Complete a mock interview, prepare thoughtful questions, test your setup, and review only brief notes before the interview.",
    },
  ];

  return phases.map((phase, index) => {
    const start = Math.floor((index * availableDays) / phases.length) + 1;
    const end = Math.max(
      start,
      Math.floor(((index + 1) * availableDays) / phases.length),
    );
    return {
      ...phase,
      schedule: start === end ? `Day ${start}` : `Days ${start}-${end}`,
    };
  });
}

function Interview() {
  const [targetRole, setTargetRole] = useState("");
  const [interviewType, setInterviewType] = useState(INTERVIEW_TYPES[0]);
  const [days, setDays] = useState(7);
  const [plan, setPlan] = useState(null);

  useEffect(() => {
    async function loadRole() {
      try {
        const response = await getProfile();
        setTargetRole(response.data.target_role || "");
      } catch {
        // A profile is optional; the user can enter a role directly.
      }
    }

    loadRole();
  }, []);

  const createPlan = (event) => {
    event.preventDefault();
    const role = targetRole.trim();
    if (!role) {
      return;
    }
    setPlan({
      role,
      timeline: buildPlan(role, interviewType, days),
      questions: QUESTION_SETS[interviewType],
    });
  };

  return (
    <div className="space-y-8">
      <section className="rounded-2xl bg-gradient-to-r from-blue-600 to-indigo-700 p-8 shadow-xl">
        <div className="flex items-start gap-4">
          <MessageSquare className="mt-1 text-blue-100" size={38} />
          <div>
            <h1 className="text-3xl font-bold text-white sm:text-4xl">Interview Center</h1>
            <p className="mt-3 max-w-3xl text-lg text-blue-100">
              Create a focused preparation plan, practice relevant questions, and arrive with a clear interview-day checklist.
            </p>
          </div>
        </div>
      </section>

      <form onSubmit={createPlan} className="rounded-2xl border border-gray-800 bg-gray-900 p-6 shadow-lg sm:p-8">
        <div className="flex items-center gap-3">
          <Sparkles className="text-blue-400" />
          <h2 className="text-2xl font-bold text-white">Build your interview plan</h2>
        </div>
        <div className="mt-6 grid gap-5 md:grid-cols-3">
          <label className="block">
            <span className="mb-2 block text-sm font-medium text-gray-300">Target role</span>
            <input
              value={targetRole}
              onChange={(event) => setTargetRole(event.target.value)}
              placeholder="Site Reliability Engineer"
              required
              className="w-full rounded-xl border border-gray-700 bg-gray-950 px-4 py-3 text-white outline-none focus:border-blue-500"
            />
          </label>
          <label className="block">
            <span className="mb-2 block text-sm font-medium text-gray-300">Interview type</span>
            <select
              value={interviewType}
              onChange={(event) => setInterviewType(event.target.value)}
              className="w-full rounded-xl border border-gray-700 bg-gray-950 px-4 py-3 text-white outline-none focus:border-blue-500"
            >
              {INTERVIEW_TYPES.map((type) => <option key={type}>{type}</option>)}
            </select>
          </label>
          <label className="block">
            <span className="mb-2 block text-sm font-medium text-gray-300">Days to prepare</span>
            <input
              type="number"
              min="1"
              max="60"
              value={days}
              onChange={(event) => setDays(event.target.value)}
              className="w-full rounded-xl border border-gray-700 bg-gray-950 px-4 py-3 text-white outline-none focus:border-blue-500"
            />
          </label>
        </div>
        <button className="mt-6 w-full rounded-xl bg-blue-600 px-5 py-3 font-semibold text-white transition hover:bg-blue-500 sm:w-auto">
          Create interview plan
        </button>
      </form>

      {!plan && (
        <section className="rounded-2xl border border-dashed border-gray-700 bg-gray-900/60 p-10 text-center">
          <Target className="mx-auto text-gray-500" size={42} />
          <h2 className="mt-4 text-xl font-semibold text-white">Your plan will appear here</h2>
          <p className="mt-2 text-gray-400">Enter a role and choose the interview format to get started.</p>
        </section>
      )}

      {plan && (
        <>
          <section className="rounded-2xl border border-gray-800 bg-gray-900 p-6 sm:p-8">
            <div className="flex items-center gap-3">
              <CalendarDays className="text-blue-400" />
              <div>
                <h2 className="text-2xl font-bold text-white">Preparation timeline</h2>
                <p className="text-gray-400">{plan.role} - {days} day plan</p>
              </div>
            </div>
            <div className="mt-6 grid gap-4 md:grid-cols-2">
              {plan.timeline.map((item) => (
                <article key={item.title} className="rounded-xl border border-gray-800 bg-gray-950 p-5">
                  <p className="text-sm font-semibold text-blue-400">{item.schedule}</p>
                  <h3 className="mt-2 text-lg font-bold text-white">{item.title}</h3>
                  <p className="mt-2 leading-6 text-gray-400">{item.description}</p>
                </article>
              ))}
            </div>
          </section>

          <div className="grid gap-6 lg:grid-cols-2">
            <section className="rounded-2xl border border-gray-800 bg-gray-900 p-6">
              <div className="flex items-center gap-3">
                <MessageSquare className="text-purple-400" />
                <h2 className="text-xl font-bold text-white">Practice questions</h2>
              </div>
              <ol className="mt-5 space-y-4">
                {plan.questions.map((question, index) => (
                  <li key={question} className="flex gap-3 text-gray-300">
                    <span className="flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-purple-500/20 text-sm font-bold text-purple-300">{index + 1}</span>
                    <span>{question}</span>
                  </li>
                ))}
              </ol>
            </section>

            <section className="rounded-2xl border border-gray-800 bg-gray-900 p-6">
              <div className="flex items-center gap-3">
                <ClipboardCheck className="text-green-400" />
                <h2 className="text-xl font-bold text-white">Interview-day checklist</h2>
              </div>
              <ul className="mt-5 space-y-4">
                {[
                  "Review the job description and your three strongest examples.",
                  "Prepare two thoughtful questions for the interviewer.",
                  "Keep your resume and brief achievement notes available.",
                  "Test your camera, microphone, connection, route, and timing.",
                  "Join or arrive 10 minutes early.",
                ].map((item) => (
                  <li key={item} className="flex gap-3 text-gray-300">
                    <CheckCircle2 className="mt-0.5 shrink-0 text-green-400" size={20} />
                    <span>{item}</span>
                  </li>
                ))}
              </ul>
            </section>
          </div>
        </>
      )}
    </div>
  );
}

export default Interview;
