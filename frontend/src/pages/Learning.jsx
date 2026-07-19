import { useEffect, useState } from "react";
import {
  BookOpen,
  CheckCircle2,
  Circle,
  Clock3,
  Code2,
  GraduationCap,
  Rocket,
  Target,
} from "lucide-react";

import { getProfile } from "../services/api";


const POPULAR_SKILLS = [
  "AWS",
  "Docker",
  "Kubernetes",
  "Terraform",
  "CI/CD",
  "Python",
  "Linux",
  "System Design",
];

function buildRoadmap(skill, targetRole, weeks, weeklyHours) {
  const phases = [
    {
      title: "Learn the foundations",
      outcome: `Understand the core concepts, terminology, and common workflows used with ${skill}.`,
      tasks: [
        `Complete an introductory ${skill} course or official getting-started guide.`,
        "Create concise notes covering the most important concepts.",
        "Complete small exercises without copying the solution.",
      ],
    },
    {
      title: "Build practical confidence",
      outcome: `Use ${skill} to solve realistic tasks expected from a ${targetRole}.`,
      tasks: [
        "Reproduce two common workplace scenarios in a safe practice environment.",
        "Document errors, troubleshooting steps, and the final solution.",
        "Explain the solution aloud as if presenting it to a teammate.",
      ],
    },
    {
      title: "Create a portfolio project",
      outcome: `Produce visible evidence that demonstrates applied ${skill} ability.`,
      tasks: [
        `Build one end-to-end ${skill} project aligned with ${targetRole} work.`,
        "Add a README with architecture, setup steps, decisions, and results.",
        "Add tests, monitoring, security, or automation where appropriate.",
      ],
    },
    {
      title: "Validate and communicate",
      outcome: `Be ready to discuss ${skill} confidently in applications and interviews.`,
      tasks: [
        "Review weak areas and repeat exercises without notes.",
        "Prepare three interview answers based on the project.",
        "Add the verified skill and project evidence to your resume and profile.",
      ],
    },
  ];

  return phases.map((phase, index) => {
    const start = Math.floor((index * weeks) / phases.length) + 1;
    const end = Math.max(start, Math.floor(((index + 1) * weeks) / phases.length));
    return {
      ...phase,
      id: `${index}-${phase.title}`,
      schedule: start === end ? `Week ${start}` : `Weeks ${start}-${end}`,
      hours: Math.max(1, Math.round(((end - start + 1) * weeklyHours))),
    };
  });
}

function Learning() {
  const [targetRole, setTargetRole] = useState("");
  const [skill, setSkill] = useState(POPULAR_SKILLS[0]);
  const [customSkill, setCustomSkill] = useState("");
  const [weeks, setWeeks] = useState(8);
  const [weeklyHours, setWeeklyHours] = useState(6);
  const [roadmap, setRoadmap] = useState(null);
  const [completed, setCompleted] = useState(new Set());

  useEffect(() => {
    async function loadRole() {
      try {
        const response = await getProfile();
        setTargetRole(response.data.target_role || "");
      } catch {
        // A profile is optional; the role can be entered directly.
      }
    }
    loadRole();
  }, []);

  const selectedSkill = customSkill.trim() || skill;
  const totalTasks = roadmap ? roadmap.length * 3 : 0;
  const progress = totalTasks ? Math.round((completed.size / totalTasks) * 100) : 0;

  const createRoadmap = (event) => {
    event.preventDefault();
    const role = targetRole.trim();
    if (!role || !selectedSkill) {
      return;
    }
    setRoadmap(buildRoadmap(selectedSkill, role, Number(weeks), Number(weeklyHours)));
    setCompleted(new Set());
  };

  const toggleTask = (taskKey) => {
    setCompleted((current) => {
      const next = new Set(current);
      if (next.has(taskKey)) {
        next.delete(taskKey);
      } else {
        next.add(taskKey);
      }
      return next;
    });
  };

  return (
    <div className="space-y-8">
      <section className="rounded-2xl bg-gradient-to-r from-emerald-600 to-blue-700 p-8 shadow-xl">
        <div className="flex items-start gap-4">
          <GraduationCap className="mt-1 text-emerald-100" size={42} />
          <div>
            <h1 className="text-3xl font-bold text-white sm:text-4xl">Learning Center</h1>
            <p className="mt-3 max-w-3xl text-lg text-emerald-50">
              Turn a career skill into a focused roadmap with practical exercises, a portfolio project, and measurable progress.
            </p>
          </div>
        </div>
      </section>

      <form onSubmit={createRoadmap} className="rounded-2xl border border-gray-800 bg-gray-900 p-6 shadow-lg sm:p-8">
        <div className="flex items-center gap-3">
          <Target className="text-emerald-400" />
          <h2 className="text-2xl font-bold text-white">Create a learning roadmap</h2>
        </div>
        <div className="mt-6 grid gap-5 md:grid-cols-2 xl:grid-cols-4">
          <label className="block">
            <span className="mb-2 block text-sm font-medium text-gray-300">Target role</span>
            <input
              required
              value={targetRole}
              onChange={(event) => setTargetRole(event.target.value)}
              placeholder="Site Reliability Engineer"
              className="w-full rounded-xl border border-gray-700 bg-gray-950 px-4 py-3 text-white outline-none focus:border-emerald-500"
            />
          </label>
          <label className="block">
            <span className="mb-2 block text-sm font-medium text-gray-300">Focus skill</span>
            <select
              value={skill}
              onChange={(event) => setSkill(event.target.value)}
              disabled={Boolean(customSkill)}
              className="w-full rounded-xl border border-gray-700 bg-gray-950 px-4 py-3 text-white outline-none focus:border-emerald-500 disabled:opacity-50"
            >
              {POPULAR_SKILLS.map((item) => <option key={item}>{item}</option>)}
            </select>
          </label>
          <label className="block">
            <span className="mb-2 block text-sm font-medium text-gray-300">Plan length</span>
            <select value={weeks} onChange={(event) => setWeeks(Number(event.target.value))} className="w-full rounded-xl border border-gray-700 bg-gray-950 px-4 py-3 text-white outline-none focus:border-emerald-500">
              {[4, 6, 8, 12, 16].map((value) => <option key={value} value={value}>{value} weeks</option>)}
            </select>
          </label>
          <label className="block">
            <span className="mb-2 block text-sm font-medium text-gray-300">Hours each week</span>
            <input type="number" min="1" max="40" value={weeklyHours} onChange={(event) => setWeeklyHours(Number(event.target.value))} className="w-full rounded-xl border border-gray-700 bg-gray-950 px-4 py-3 text-white outline-none focus:border-emerald-500" />
          </label>
        </div>
        <label className="mt-5 block max-w-xl">
          <span className="mb-2 block text-sm font-medium text-gray-300">Or enter another skill</span>
          <input value={customSkill} onChange={(event) => setCustomSkill(event.target.value)} placeholder="For example: Prometheus" className="w-full rounded-xl border border-gray-700 bg-gray-950 px-4 py-3 text-white outline-none focus:border-emerald-500" />
        </label>
        <button className="mt-6 w-full rounded-xl bg-emerald-600 px-5 py-3 font-semibold text-white transition hover:bg-emerald-500 sm:w-auto">
          Build learning roadmap
        </button>
      </form>

      {!roadmap && (
        <section className="rounded-2xl border border-dashed border-gray-700 bg-gray-900/60 p-10 text-center">
          <BookOpen className="mx-auto text-gray-500" size={44} />
          <h2 className="mt-4 text-xl font-semibold text-white">Your roadmap will appear here</h2>
          <p className="mt-2 text-gray-400">Choose a skill, timeframe, and weekly commitment to begin.</p>
        </section>
      )}

      {roadmap && (
        <>
          <section className="rounded-2xl border border-gray-800 bg-gray-900 p-6">
            <div className="flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
              <div>
                <p className="text-sm font-semibold uppercase tracking-wider text-emerald-400">Current roadmap</p>
                <h2 className="mt-1 text-2xl font-bold text-white">{selectedSkill} for {targetRole}</h2>
                <p className="mt-1 text-gray-400">{weeks} weeks - approximately {Number(weeks) * Number(weeklyHours)} hours</p>
              </div>
              <p className="text-2xl font-bold text-emerald-400">{progress}% complete</p>
            </div>
            <div className="mt-5 h-3 overflow-hidden rounded-full bg-gray-800">
              <div className="h-full rounded-full bg-emerald-500 transition-all" style={{ width: `${progress}%` }} />
            </div>
          </section>

          <div className="space-y-5">
            {roadmap.map((phase) => (
              <section key={phase.id} className="rounded-2xl border border-gray-800 bg-gray-900 p-6">
                <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
                  <div>
                    <p className="text-sm font-semibold text-emerald-400">{phase.schedule}</p>
                    <h3 className="mt-1 text-xl font-bold text-white">{phase.title}</h3>
                    <p className="mt-2 max-w-3xl text-gray-400">{phase.outcome}</p>
                  </div>
                  <div className="flex shrink-0 items-center gap-2 text-sm text-gray-400"><Clock3 size={17} />{phase.hours} hours</div>
                </div>
                <div className="mt-5 grid gap-3 lg:grid-cols-3">
                  {phase.tasks.map((task, index) => {
                    const taskKey = `${phase.id}-${index}`;
                    const isComplete = completed.has(taskKey);
                    return (
                      <button key={taskKey} type="button" onClick={() => toggleTask(taskKey)} className={`flex items-start gap-3 rounded-xl border p-4 text-left transition ${isComplete ? "border-emerald-500/50 bg-emerald-950/30 text-gray-400" : "border-gray-800 bg-gray-950 text-gray-300 hover:border-gray-700"}`}>
                        {isComplete ? <CheckCircle2 className="mt-0.5 shrink-0 text-emerald-400" size={20} /> : <Circle className="mt-0.5 shrink-0 text-gray-500" size={20} />}
                        <span className={isComplete ? "line-through" : ""}>{task}</span>
                      </button>
                    );
                  })}
                </div>
              </section>
            ))}
          </div>

          <section className="grid gap-5 md:grid-cols-2">
            <div className="rounded-2xl border border-gray-800 bg-gray-900 p-6"><Code2 className="text-blue-400" /><h2 className="mt-3 text-xl font-bold text-white">Portfolio outcome</h2><p className="mt-2 text-gray-400">Finish with a documented project that demonstrates how you applied {selectedSkill}, handled problems, and measured the result.</p></div>
            <div className="rounded-2xl border border-gray-800 bg-gray-900 p-6"><Rocket className="text-purple-400" /><h2 className="mt-3 text-xl font-bold text-white">Career outcome</h2><p className="mt-2 text-gray-400">Convert the completed tasks into resume evidence, interview examples, and a stronger application for {targetRole} roles.</p></div>
          </section>
        </>
      )}
    </div>
  );
}

export default Learning;
