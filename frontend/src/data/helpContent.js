export const helpSections = [
  {
    id: "getting-started",
    title: "Getting started",
    description: "Set up the information NextHire uses across the app.",
    articles: [
      {
        id: "create-profile",
        title: "Create your career profile",
        summary:
          "Open Profile and add your current role, target role, location, skills, and career summary. You can upload a PDF or DOCX resume to fill empty fields, then review and save the result.",
        links: [{ label: "Open Profile", to: "/profile" }],
        keywords: ["profile", "setup", "skills", "target role", "autofill"],
      },
      {
        id: "first-resume",
        title: "Analyze your first resume",
        summary:
          "Resume Studio accepts genuine PDF and DOCX files. Upload a resume to receive resume and ATS scores, extracted skills, and improvement guidance. Empty, oversized, spoofed, and unsupported files are rejected.",
        links: [{ label: "Open Resume Studio", to: "/resume" }],
        keywords: ["resume", "pdf", "docx", "ats", "upload", "score"],
      },
      {
        id: "career-workflow",
        title: "Recommended workflow",
        summary:
          "Complete your profile, analyze a resume, search or match jobs, tailor your documents, prepare a reviewed application package, and track the final submission in Application Tracker.",
        links: [
          { label: "Open Getting Started", to: "/onboarding" },
          { label: "Find jobs", to: "/jobs" },
          { label: "Track applications", to: "/applications" },
        ],
        keywords: [
          "workflow",
          "start",
          "onboarding",
          "jobs",
          "application",
          "career",
        ],
      },
    ],
  },
  {
    id: "account-security",
    title: "Account and security",
    description: "Sign in, recover access, and control your account data.",
    articles: [
      {
        id: "sign-in",
        title: "Sign in options",
        summary:
          "Email and password sign-in is always available. Sign in with Google appears only when the deployment has a matching Google OAuth client ID configured in the frontend and backend.",
        links: [{ label: "Account settings", to: "/settings" }],
        keywords: ["login", "sign in", "google", "gmail", "password", "oauth"],
      },
      {
        id: "password-reset",
        title: "Reset a password",
        summary:
          "Choose Forgot password on the sign-in page and enter your account email. A reset link is sent when production email delivery is configured. Reset links expire after 30 minutes.",
        links: [{ label: "Reset password", to: "/forgot-password" }],
        keywords: ["forgot", "password", "reset", "email"],
      },
      {
        id: "data-control",
        title: "Export or delete your data",
        summary:
          "Settings lets you download a JSON copy of your account data. Account deletion requires your current password and the DELETE confirmation and permanently removes owner-scoped career data.",
        links: [{ label: "Manage account data", to: "/settings" }],
        keywords: ["privacy", "export", "download", "delete", "account"],
      },
    ],
  },
  {
    id: "resumes-documents",
    title: "Resumes and documents",
    description: "Analyze, tailor, save, revise, and export career documents.",
    articles: [
      {
        id: "resume-studio",
        title: "Resume Studio and document history",
        summary:
          "Resume Studio stores analyses and career documents for your account. Saved documents can be edited, compared with earlier versions, restored, and exported to PDF or DOCX from the document library.",
        links: [{ label: "Open Resume Studio", to: "/resume" }],
        keywords: ["document", "history", "revision", "restore", "export"],
      },
      {
        id: "tailor-resume",
        title: "Tailor a resume",
        summary:
          "Paste a job description and choose an ATS-safe template. NextHire uses your saved resume and profile as evidence and will not invent unsupported experience or credentials.",
        links: [{ label: "Tailor a resume", to: "/resume-tailor" }],
        keywords: ["tailor", "template", "ats", "job description"],
      },
      {
        id: "cover-letter",
        title: "Create a cover letter",
        summary:
          "Paste the target job description to generate a grounded cover letter from your profile and saved resume. Review the result before saving, exporting, or including it in an application package.",
        links: [{ label: "Create cover letter", to: "/cover-letter" }],
        keywords: ["cover letter", "generate", "document"],
      },
    ],
  },
  {
    id: "jobs-applications",
    title: "Jobs and applications",
    description: "Discover opportunities and keep the final submission under your control.",
    articles: [
      {
        id: "worldwide-search",
        title: "Search jobs worldwide",
        summary:
          "Jobs searches worldwide by default and supports country, city, remote, salary, industry, experience, employment type, date, and visa-sponsorship filters. Results identify their source and link to the provider listing.",
        links: [{ label: "Search jobs", to: "/jobs" }],
        keywords: ["worldwide", "search", "provider", "remote", "visa", "salary"],
      },
      {
        id: "provider-status",
        title: "Understand provider status",
        summary:
          "Not configured means a provider needs deployment credentials or an approved source identifier. Unavailable means a configured provider failed. No results means the provider completed successfully but found no matching jobs.",
        links: [{ label: "View job sources", to: "/jobs" }],
        keywords: ["provider", "not configured", "unavailable", "no results"],
      },
      {
        id: "saved-jobs-searches",
        title: "Saved jobs and search alerts",
        summary:
          "Save a promising role directly from job results. You can save the current filters, rerun them from Job Library, and receive an in-app notification when a later check finds new roles. If production email delivery is available and your account email is verified, each saved search also offers an off-by-default daily or weekly email alert. Every alert email includes a link that turns off only that saved-search alert.",
        links: [
          { label: "Open Job Library", to: "/job-library" },
          { label: "Search jobs", to: "/jobs" },
        ],
        keywords: ["saved job", "bookmark", "saved search", "alert", "new match"],
      },
      {
        id: "reviewed-apply",
        title: "Prepare a reviewed application",
        summary:
          "Choose a saved resume and optional cover letter, copy factual fields from your application information pack, confirm that you reviewed the package, and store it in Application Tracker. NextHire then opens the official provider listing; it does not submit the form or infer sensitive answers.",
        links: [
          { label: "Find a job", to: "/jobs" },
          { label: "Application Tracker", to: "/applications" },
        ],
        keywords: ["apply", "auto apply", "application", "resume", "manual"],
      },
      {
        id: "application-reminders",
        title: "Deadlines and follow-up reminders",
        summary:
          "Add a deadline or follow-up time when creating or editing an application. Notifications highlights upcoming or overdue actions, while the calendar shows deadlines, follow-ups, and applied dates by month.",
        links: [
          { label: "Track applications", to: "/applications" },
          { label: "View notifications", to: "/notifications" },
        ],
        keywords: ["deadline", "follow up", "reminder", "notification"],
      },
    ],
  },
  {
    id: "career-tools",
    title: "Career tools",
    description: "Use saved profile and resume evidence across the platform.",
    articles: [
      {
        id: "job-match",
        title: "Job Match",
        summary:
          "Paste a job description to compare it with your latest saved resume and profile. The match explains strengths and gaps without treating profile preferences as proof of resume experience.",
        links: [{ label: "Open Job Match", to: "/job-match" }],
        keywords: ["match", "score", "job description", "skills"],
      },
      {
        id: "skill-gap",
        title: "Skill Gap Analysis",
        summary:
          "Compare your current skills with your target role and turn the missing skills into a practical development plan.",
        links: [{ label: "Analyze skill gaps", to: "/skill-gap" }],
        keywords: ["skill gap", "target role", "development"],
      },
      {
        id: "interview-learning",
        title: "Interview and learning plans",
        summary:
          "Interview Center builds a role-focused plan and scores the structure, evidence, clarity, and ownership in written practice answers. The score does not judge technical correctness or hiring likelihood. Learning creates a structured plan for a target role or custom skill.",
        links: [
          { label: "Prepare for interviews", to: "/interview" },
          { label: "Build a learning plan", to: "/learning" },
        ],
        keywords: ["interview", "learning", "study", "practice"],
      },
    ],
  },
  {
    id: "availability",
    title: "Availability and plans",
    description: "Know which capabilities depend on deployment configuration.",
    articles: [
      {
        id: "ai-availability",
        title: "AI features are temporarily unavailable",
        summary:
          "Resume analysis, tailoring, cover letters, matching, interview preparation, and learning plans require a configured production AI service. Existing saved data and non-AI workflows remain available during an AI outage.",
        links: [{ label: "View account settings", to: "/settings" }],
        keywords: ["ai", "unavailable", "timeout", "model", "limit"],
      },
      {
        id: "billing",
        title: "Free and Pro plans",
        summary:
          "The Free plan remains usable when billing is disabled. Upgrade and subscription management become available only after the deployment has approved Stripe products, pricing, webhooks, and policies configured.",
        links: [{ label: "View plan", to: "/settings#billing" }],
        keywords: ["billing", "stripe", "pro", "free", "upgrade"],
      },
      {
        id: "privacy-safety",
        title: "Privacy and job-source safety",
        summary:
          "Use synthetic or non-sensitive resume data during a controlled beta. Verify every job on the identified provider site before applying. A listing does not imply a provider partnership or guarantee employment.",
        links: [
          { label: "Privacy Notice", to: "/privacy" },
          { label: "Terms of Use", to: "/terms" },
        ],
        keywords: ["privacy", "safety", "provider", "terms"],
      },
    ],
  },
];

export const searchableHelpArticles = helpSections.flatMap((section) =>
  section.articles.map((article) => ({
    ...article,
    sectionId: section.id,
    sectionTitle: section.title,
  })),
);
