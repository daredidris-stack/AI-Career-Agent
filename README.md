# NextHire AI

NextHire AI is an AI-powered career platform for building professional profiles, analyzing resumes, identifying skill gaps, and finding better-matched job opportunities.

The project is evolving toward a production SaaS architecture. The current implementation uses authenticated user profiles, layered backend services, and a responsive React application.

## Current capabilities

- User registration and JWT authentication
- Protected frontend routes
- Persistent career profiles
- Personalized dashboard data
- Resume analysis for PDF and DOCX uploads
- Skill-gap analysis
- Job aggregation and profile-based ranking
- Resume tailoring, job matching, and cover-letter prototypes
- AI-assisted resume template selection with three ATS-safe Word exports
- Reviewed application packages with explicit user-controlled submission

## Architecture

Backend business flows follow:

```text
Route → Service → Repository → Database
```

```text
backend/
├── auth/           JWT and password utilities
├── core/           Environment settings and shared utilities
├── database/       SQLAlchemy engine and sessions
├── dependencies/   FastAPI dependency injection
├── exceptions/     Domain-specific exceptions
├── models/         SQLAlchemy and Pydantic models
├── repositories/   Database access
├── routes/         HTTP endpoints
└── services/       Application and AI orchestration

frontend/src/
├── components/     Reusable UI components
├── context/        Authentication state
├── hooks/          Shared React hooks
├── layouts/        Application layout
├── pages/          Route-level screens
├── routes/         Route protection
└── services/       Backend API client
```

## Technology stack

### Backend

- FastAPI
- SQLAlchemy
- SQLite for local development
- JWT authentication
- Ollama for local AI inference

### Frontend

- React and TypeScript
- Vite
- Tailwind CSS
- React Router
- Axios
- Recharts

## Prerequisites

- Python 3.12 or newer
- Node.js 20 or newer
- npm
- [Ollama](https://ollama.com/) with the `qwen3:8b` model for AI-backed features

## Local setup

All commands below run from the repository root unless noted otherwise.

### 1. Configure the backend

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
```

Create a private local environment file:

```bash
cp .env.example .env
```

Open `.env`, replace `JWT_SECRET_KEY`, and add any optional Adzuna and Jooble credentials. The backend loads this file automatically for local development. Existing shell or deployment environment variables take precedence over `.env` values.

Generate a strong local JWT secret with `openssl rand -hex 32`. Never commit `.env` or paste credentials into documentation, issues, or chat. If a credential has been shared publicly, rotate it before saving the replacement.

Production databases use Alembic migrations. See [Database operations](docs/database-operations.md) for PostgreSQL setup, existing-database adoption, backups, and restore drills.

The available variables are documented in `.env.example`. Do not commit real credentials.

Initialize the database and start the API:

```bash
python -m backend.database.init_db
uvicorn backend.main:app --reload
```

The API is available at `http://127.0.0.1:8000`, with interactive documentation at `http://127.0.0.1:8000/docs`.

### 2. Configure the frontend

In a second terminal:

```bash
cd frontend
npm install
npm run dev
```

Open the local URL printed by Vite, normally `http://127.0.0.1:5173`.

### 3. Configure local AI

```bash
ollama pull qwen3:8b
ollama serve
```

Features that call Ollama require the local model service to be running.

### Resume template agent

The Resume Tailor page loads its template catalog from the authenticated
`GET /resume/templates` endpoint. Users can select **ATS Professional**,
**ATS Modern**, or **ATS Classic**, or leave the choice on **AI recommended**.
The tailoring agent returns structured, factual resume content and recommends
a template when automatic selection is enabled. The deterministic Word
renderer applies the selected design and keeps layout generation separate from
AI-written content.

No third-party template API key is required. Template source files live in
`backend/templates/`, and the catalog can be regenerated with:

```bash
python scripts/build_resume_template_catalog.py --directory backend/templates
```

## Verification

Run backend tests from the repository root:

```bash
.venv/bin/python -m unittest discover -s tests -v
```

Run frontend checks:

```bash
npm --prefix frontend run lint
npm --prefix frontend run build
```

## Environment variables

| Variable | Required | Purpose |
| --- | --- | --- |
| `JWT_SECRET_KEY` | Yes | Signs and validates authentication tokens |
| `JWT_ALGORITHM` | No | JWT algorithm; defaults to `HS256` |
| `ACCESS_TOKEN_EXPIRE_HOURS` | No | Token lifetime; defaults to 24 hours |
| `DATABASE_URL` | No | SQLAlchemy database URL; defaults to local SQLite |
| `GOOGLE_CLIENT_ID` | No | Verifies Google Identity Services ID tokens on the backend |
| `TURNSTILE_SECRET_KEY` | Production | Enables server-side Cloudflare Turnstile validation for login |
| `TURNSTILE_ALLOWED_HOSTNAMES` | Production | Comma-separated hostnames accepted from Turnstile validation |
| `VITE_TURNSTILE_SITE_KEY` | Production | Public Turnstile site key embedded in the login page at frontend build time |
| `VITE_GOOGLE_CLIENT_ID` | No | Public Google OAuth web client ID used to render Sign in with Google |
| `ADZUNA_APP_ID` | No | Enables Adzuna job search |
| `ADZUNA_APP_KEY` | No | Enables Adzuna job search |
| `ADZUNA_WORLDWIDE_MARKETS` | No | Comma-separated Adzuna country markets searched for Worldwide queries; defaults to `us,gb,ca,au,de,fr,in,mx` |
| `JOOBLE_API_KEY` | No | Enables paginated global Jooble job search |
| `THEIRSTACK_API_KEY` | No | Enables worldwide search across Indeed, Glassdoor, employer sites, and other indexed sources |
| `SERPAPI_API_KEY` | No | Enables Google Jobs results through SerpApi; each uncached result page consumes a SerpApi search credit |
| `FANTASTIC_JOBS_API_KEY` | No | Enables the Fantastic.jobs direct-employer ATS index |
| `FANTASTIC_JOBS_MAX_RESULTS` | No | Caps paid Fantastic.jobs results per search page; defaults to 20 |
| `FANTASTIC_JOBS_CACHE_SECONDS` | No | Reuses identical Fantastic.jobs searches to protect credits; defaults to 900 seconds |
| `FANTASTIC_JOBS_TIME_FRAME` | No | Fantastic.jobs active-job window: `1h`, `24h`, `7d`, or `6m`; defaults to `6m` for broad role coverage |
| `JOB_INGESTION_QUERIES` | No | Extra comma-separated `Role|Location` targets for background synchronization |
| `JOB_INGESTION_RESULTS_PER_TARGET` | No | Maximum jobs saved per target and sync; defaults to 20 |
| `JOB_INGESTION_INTERVAL_SECONDS` | No | Successful target-sync interval; defaults to 24 hours |
| `JOB_INGESTION_RETRY_SECONDS` | No | Retry delay after provider failure; defaults to one hour |
| `JOB_INGESTION_POLL_SECONDS` | No | Worker polling interval; defaults to 15 minutes |
| `JOB_LISTING_STALE_DAYS` | No | Deactivates unseen stored jobs after this many days; defaults to 45 |
| `USAJOBS_API_KEY` | No | Enables U.S. federal job search through the official USAJOBS API |
| `USAJOBS_USER_AGENT` | With USAJOBS | Email address registered with the USAJOBS API key |
| `GREENHOUSE_JOB_BOARDS` | No | Comma-separated `Company|board-token` entries for direct Greenhouse employer feeds |
| `LEVER_JOB_SITES` | No | Comma-separated `Company|site-name` entries for direct Lever employer feeds |
| `ASHBY_JOB_BOARDS` | No | Comma-separated `Company|board-name` entries for direct Ashby employer feeds |
| `DIRECT_EMPLOYER_JOB_SOURCES` | No | Opt-in comma-separated direct employer sources: `microsoft`, `apple`, and/or `crossover`; confirm production use with each employer first |
| `AI_MODEL` | No | Local Ollama model; defaults to `qwen3:8b` |
| `AI_REQUEST_TIMEOUT_SECONDS` | No | Maximum time for one model attempt; defaults to 45 seconds |
| `AI_MAX_RETRIES` | No | Retry count for transient model failures; defaults to 1 |
| `AI_MAX_PROMPT_CHARACTERS` | No | Caps model input size; defaults to 30,000 characters |
| `AI_REQUESTS_PER_HOUR` | No | Per-account hourly AI request allowance; defaults to 20 |
| `AI_REQUESTS_PER_DAY` | No | Per-account daily AI request allowance; defaults to 100 |
| `MAX_RESUME_UPLOAD_BYTES` | No | Maximum PDF/DOCX resume upload size; defaults to 5 MB |
| `MALWARE_SCANNING_ENABLED` | No | Fail-closed ClamAV upload scanning switch; defaults to `false` |
| `CLAMAV_HOST` | With scanning | Private-network hostname for the ClamAV daemon |
| `CLAMAV_PORT` | No | ClamAV daemon TCP port; defaults to `3310` |
| `CLAMAV_TIMEOUT_SECONDS` | No | Upload scan connection/read timeout; defaults to 10 seconds |
| `RESUME_PARSER_TIMEOUT_SECONDS` | No | Wall-clock limit for one parser subprocess; defaults to 20 seconds |
| `RESUME_PARSER_MAX_CPU_SECONDS` | No | CPU limit for one parser subprocess; defaults to 15 seconds |
| `RESUME_PARSER_MAX_MEMORY_MB` | No | Linux address-space limit for one parser subprocess; defaults to 512 MB |
| `RESUME_PARSER_MAX_TEXT_CHARACTERS` | No | Maximum extracted resume text; defaults to 200,000 characters |
| `FRONTEND_URL` | No | Frontend origin used in verification and reset links |
| `REQUIRE_EMAIL_VERIFICATION` | No | Blocks unverified login when set to `true` |
| `SMTP_HOST` | Production | SMTP server used for account emails |
| `SMTP_PORT` | No | SMTP port; defaults to `587` |
| `SMTP_USERNAME` | Production | SMTP login username |
| `SMTP_PASSWORD` | Production | SMTP login password |
| `SMTP_FROM_EMAIL` | Production | Sender address for account emails |
| `SMTP_USE_TLS` | No | Enables SMTP STARTTLS; defaults to `true` |
| `JOB_ALERT_EMAIL_ENABLED` | No | Explicit deployment switch for saved-search email alerts; defaults to `false` |
| `JOB_ALERT_BATCH_SIZE` | No | Maximum due saved searches processed per scheduled run; defaults to 50 |
| `JOB_ALERT_RETRY_MINUTES` | No | Delay before retrying a failed alert; defaults to 60 minutes |
| `JOB_ALERT_SEND_HOUR` | No | User-local delivery hour from 0 to 23; defaults to 8 |
| `JOB_ALERT_MAX_JOBS_PER_EMAIL` | No | Maximum job details included in one alert email; defaults to 10 |
| `ADMIN_EMAILS` | No | Comma-separated verified account emails allowed to access Operations |

### Direct job feeds and Google Jobs

SerpApi uses its Google Jobs engine and requires only `SERPAPI_API_KEY`. Google
Jobs currently returns up to ten results per page. The app reuses SerpApi's
next-page token when the user loads another page and does not make a page
request when no token is available.

Fantastic.jobs uses its current `/v1/active-ats` endpoint to search direct
employer career systems, including Workday, SmartRecruiters, iCIMS,
Greenhouse, Lever, Ashby, and many others. Configure the private server-side
key with:

```env
FANTASTIC_JOBS_API_KEY=your-key
```

Fantastic.jobs charges for each returned job. The adapter therefore defaults
to at most 20 results per page, searches active jobs from the last six months,
and caches identical searches for 15 minutes.
Its separate LinkedIn/Wellfound/Y Combinator endpoint is intentionally not
queried, avoiding an extra paid request and duplicates of direct employer
listings. The key must never be placed in a frontend environment file.

USAJOBS requires both the API key and the email address used when requesting
that key:

```env
USAJOBS_API_KEY=your-key
USAJOBS_USER_AGENT=you@example.com
```

Greenhouse, Lever, and Ashby publish jobs per employer rather than through one
global search endpoint. Configure the employer display name and public board
identifier using `Company|identifier` entries:

```env
GREENHOUSE_JOB_BOARDS=Example Corp|example,Another Corp|another
LEVER_JOB_SITES=Example Labs|examplelabs
ASHBY_JOB_BOARDS=Example AI|example-ai
```

These direct employer feeds provide canonical listing or application URLs and
full descriptions when present. A failing or stale employer identifier is
isolated so it cannot break the other job sources.

Microsoft, Apple, and Crossover career-site interfaces are available only as
explicit opt-ins because they are not documented as general public job APIs.
After confirming the intended production use with each employer, enable only
the approved sources:

```env
DIRECT_EMPLOYER_JOB_SOURCES=microsoft,apple,crossover
```

### Persistent job ingestion

Job searches now check the SQL-backed `job_listings` catalog first. When no
stored match exists, the existing live providers are queried and their results
are saved for later searches. Records are deduplicated by normalized company,
title, and location; richer descriptions and direct application links update
the existing record instead of creating another card.

Run a one-time profile-targeted Fantastic.jobs synchronization after applying
database migrations:

```bash
.venv/bin/alembic upgrade head
.venv/bin/python -m backend.jobs.sync_job_catalog
```

The first successful target sync backfills up to six months. Later syncs pull
the latest 24 hours and are skipped until the configured interval is due. To
run the scheduler continuously in a separate terminal:

```bash
.venv/bin/python -m backend.jobs.sync_job_catalog --watch
```

The worker derives targets from user profiles. Extra all-industry targets can
be supplied without changing code:

```env
JOB_INGESTION_QUERIES=Registered Nurse|Worldwide,Accountant|Mexico,Warehouse Manager|Canada
```

Docker users can enable the separate worker service explicitly:

```bash
docker compose --profile ingestion up --build
```

Expired listings are deactivated using provider expiry dates, with a stale-job
fallback for records that have not been seen within the configured retention
window. Provider failures do not delete cached jobs or prevent local search.

### Saved-search email alerts

Saved searches always support manual checks and in-app new-match notifications.
Automatic email is off by default at both the deployment and user levels.
After SMTP and the scheduled worker are verified, a user with a verified email
can explicitly enable a daily or weekly alert for each saved search in Job
Library. The first scheduled search establishes a baseline and sends nothing;
later emails contain only previously unseen matches and include a signed
unsubscribe link for that one search.

Run one due batch and exit with:

```bash
.venv/bin/python -m backend.jobs.send_job_alerts
```

Use a scheduler to invoke that command periodically; do not run it as a
continuous process. Setup, staged activation, verification, and rollback are
documented in [Saved-search email alert setup](docs/job-alert-email-setup.md).

### Administrator operations and auditing

Verified accounts listed in `ADMIN_EMAILS` can review aggregate deployment
status and manage support requests from Operations. Every support status or
internal-note change creates an append-only audit event containing the
administrator identity, request ID, target, status transition, and note-presence
change. Ticket messages and internal-note text are not duplicated into the
audit history. Application code and database triggers reject audit event
updates and deletions.

Production operations must assign access ownership and approve an audit-event
retention/archive policy before public launch.

### Resume upload malware scanning

Every uploaded PDF or DOCX used by Resume Studio, profile autofill, or Resume
Tailor passes through the same temporary-file boundary. When
`MALWARE_SCANNING_ENABLED=true`, the complete bounded upload is streamed to a
configured ClamAV daemon before any document parser runs. A detection returns a
generic rejection; scanner connection, timeout, or protocol failures return
HTTP 503 and do not parse the file. Temporary files are removed in every path.

Scanning is disabled by default so local development does not claim protection
it does not have. Private-network deployment, safe validation, rollback, and
resource requirements are documented in
[Resume upload malware scanning](docs/upload-malware-scanning.md).

After validation and the optional malware scan, document parsing always runs
in a fresh subprocess that the API awaits asynchronously. The subprocess
receives only the temporary file path and bounded parser settings; database,
JWT, SMTP, provider, and other application secrets are not inherited. It has
CPU, file-descriptor, output, and wall-clock limits, plus a Linux memory limit,
and is stopped if the request is cancelled or times out. There is no
in-process parsing fallback. Deployment limitations and staged checks are in
[Resume parser isolation](docs/resume-parser-isolation.md).

### Apply Assistant

Open a job’s details and choose **Prepare application** to build a reviewed
application package from documents already saved in NextHire. A resume is
required and a cover letter is optional. The package is stored in the
Application Tracker with status `preparing`.

The official provider link appears only after the user confirms that the job
and selected documents were reviewed and that the employer form will be
completed manually. NextHire does not answer work-authorization, sponsorship,
salary, or voluntary demographic questions, bypass account security or
CAPTCHA, or submit the external form. After submitting on the employer site,
the user records the final status in the Application Tracker.

## Development principles

- Work on one verified milestone at a time.
- Keep business logic out of route handlers.
- Maintain one active implementation of each feature.
- Preserve responsive behavior across desktop, tablet, and mobile.
- Keep generated documents, databases, secrets, build output, and virtual environments out of Git.

## Authentication setup

### Cloudflare Turnstile login protection

Create a Turnstile widget in Cloudflare and configure its allowed hostnames. Then set:

- `TURNSTILE_SECRET_KEY` and `TURNSTILE_ALLOWED_HOSTNAMES` in the backend environment.
- `VITE_TURNSTILE_SITE_KEY` in `frontend/.env.local`, or in the root `.env` when building with Docker Compose.

Turnstile enforcement is disabled when `TURNSTILE_SECRET_KEY` is empty, which keeps local development available without Cloudflare credentials. In production, configure both keys together; the secret key must never be exposed to the frontend.

When Turnstile is enabled, server-side validation requires the expected
`login` action and a hostname in `TURNSTILE_ALLOWED_HOSTNAMES`; an empty
hostname allowlist fails closed. For local end-to-end testing, Cloudflare's
public dummy keys are supported when `APP_ENV` is not `production`. The
published dummy secret keys are deliberately rejected in production.

### Google sign-in

Create an OAuth 2.0 client in Google Cloud Console with application type
**Web application**. Add the frontend origin, such as
`http://localhost:5173`, under **Authorized JavaScript origins**. The popup
credential flow used by this app does not require a redirect URI or client
secret.

Set the same client ID in both places:

```env
GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
VITE_GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
```

Run `python -m backend.database.init_db` for local SQLite or
`alembic upgrade head` for a migrated database, then restart both the API and
frontend. Google-created accounts use Google's verified email and stable
account identifier; an existing account with the same verified email is linked
instead of duplicated only when Google is authoritative for that address
(Gmail or Google Workspace). A Google Account using a third-party email must
use the password flow until an explicit account-linking challenge is added.

## Current roadmap

The authenticated SaaS foundation and commercialization-readiness roadmap are implemented. See the [beta readiness report](docs/beta-readiness-report.md), [beta release checklist](docs/beta-release-checklist.md), and [roadmap handoff](docs/roadmap-handoff.md) for verified evidence, remaining launch blockers, and evidence-driven next work.
5. Add migrations, PostgreSQL support, observability, subscriptions, and deployment automation.
