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

Set the required JWT secret and any optional integrations:

```bash
export JWT_SECRET_KEY="$(openssl rand -hex 32)"
export DATABASE_URL="sqlite:///./career_agent.db"
export ADZUNA_APP_ID=""
export ADZUNA_APP_KEY=""
export JOOBLE_API_KEY=""
export FRONTEND_URL="http://localhost:5173"
export REQUIRE_EMAIL_VERIFICATION="false"
```

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
| `ADZUNA_APP_ID` | No | Enables Adzuna job search |
| `ADZUNA_APP_KEY` | No | Enables Adzuna job search |
| `JOOBLE_API_KEY` | No | Enables paginated global Jooble job search |
| `AI_MODEL` | No | Local Ollama model; defaults to `qwen3:8b` |
| `AI_REQUEST_TIMEOUT_SECONDS` | No | Maximum time for one model attempt; defaults to 45 seconds |
| `AI_MAX_RETRIES` | No | Retry count for transient model failures; defaults to 1 |
| `AI_MAX_PROMPT_CHARACTERS` | No | Caps model input size; defaults to 30,000 characters |
| `AI_REQUESTS_PER_HOUR` | No | Per-account hourly AI request allowance; defaults to 20 |
| `AI_REQUESTS_PER_DAY` | No | Per-account daily AI request allowance; defaults to 100 |
| `FRONTEND_URL` | No | Frontend origin used in verification and reset links |
| `REQUIRE_EMAIL_VERIFICATION` | No | Blocks unverified login when set to `true` |
| `SMTP_HOST` | Production | SMTP server used for account emails |
| `SMTP_PORT` | No | SMTP port; defaults to `587` |
| `SMTP_USERNAME` | Production | SMTP login username |
| `SMTP_PASSWORD` | Production | SMTP login password |
| `SMTP_FROM_EMAIL` | Production | Sender address for account emails |
| `SMTP_USE_TLS` | No | Enables SMTP STARTTLS; defaults to `true` |

## Development principles

- Work on one verified milestone at a time.
- Keep business logic out of route handlers.
- Maintain one active implementation of each feature.
- Preserve responsive behavior across desktop, tablet, and mobile.
- Keep generated documents, databases, secrets, build output, and virtual environments out of Git.

## Current roadmap

The authenticated SaaS foundation and commercialization-readiness roadmap are implemented. See the [beta readiness report](docs/beta-readiness-report.md), [beta release checklist](docs/beta-release-checklist.md), and [roadmap handoff](docs/roadmap-handoff.md) for verified evidence, remaining launch blockers, and evidence-driven next work.
5. Add migrations, PostgreSQL support, observability, subscriptions, and deployment automation.
