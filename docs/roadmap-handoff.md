# NextHire AI roadmap handoff

## Project 1 continuation snapshot — July 26, 2026

This continuation began from `main` at `0418879` with an intentionally
uncommitted feature batch. The five feature groups are now separated into
auditable commits, and the complete implementation passes the automated
release gate:

- 356 backend tests pass with `ResourceWarning` treated as an error.
- Alembic upgrades an empty database through `20260729_0012`, reports no
  schema drift, downgrades to base, and upgrades to head again.
- Frontend lint and the production Vite build pass.
- `git diff --check` passes.

The Alembic blocker was that `migrations/env.py` loads model metadata through
`backend.models`, but `JobListing` and `JobSyncState` were not imported by that
package. `backend/models/__init__.py` now imports and exports both models. This
verifies the repository implementation. Credentialed production services and
the deployment-specific checks listed below remain separate release gates.

### Completed feature batch

The original dirty worktree was reviewed and separated into these bounded
groups:

1. **Login protection and Google identity — code verified**
   - Google ID-token verification, account linking, login UI, Turnstile
     verification, and migration `20260720_0005`.
   - 36 focused auth tests pass. An independently reconstructed staged
     snapshot passes 203 backend tests, its complete Alembic cycle with no
     drift, and frontend lint/build. The combined worktree passes the full
     282-test release gate.
   - Google client IDs are configured on both sides and match. A local browser
     smoke test rendered Google sign-in, exercised the password-login error
     path against the API, and found no browser console errors.
   - Google auto-linking is limited to authoritative Gmail/Workspace
     identities. Turnstile rejects published dummy secrets in production and
     fails closed without an allowed hostname.
   - Live Turnstile remains a deployment check because no local site key,
     secret, or hostname allowlist is currently configured.
2. **Profile intake and resume cleanup — code and browser verified**
   - Resume-driven profile autofill, normalized target-role suggestions, and
     removal of markdown/template artifacts from uploaded resume text.
   - 27 focused route, service, resume-reader, and cleanup tests pass. An
     independently reconstructed staged snapshot passes 219 backend tests, its
     complete Alembic cycle with no drift, frontend lint/build, and the staged
     diff whitespace check.
   - An authenticated local browser smoke test completed real PDF and DOCX
     uploads against `qwen3:8b`. Both requests returned 200, empty profile
     fields were populated, a manually entered current role was preserved,
     target-role choices updated the form, and reloading confirmed that autofill
     does not save before the user presses the profile save button.
3. **ATS resume templates and deterministic Word export — code and render verified**
   - Three bundled templates, catalog/selection service, structured tailoring,
     export rendering, and the Resume Tailor/Document Library UI changes.
   - 23 focused template, tailoring, route, and export tests pass. An
     independently reconstructed staged snapshot passes 229 backend tests, its
     complete Alembic cycle with no drift, frontend lint/build, and the staged
     diff whitespace check.
   - Representative one-page exports were generated through the production
     export service for ATS Professional, ATS Modern, and ATS Classic. Every
     rendered page was inspected at full resolution and showed clean margins,
     typography, bullets, section flow, and page boundaries with no clipping,
     overlap, missing glyphs, placeholders, or broken layout.
   - Regenerating the three source templates produced identical unpacked OOXML
     package contents; only ZIP container metadata differed.
4. **Worldwide provider and job-detail expansion — code and bounded live verified**
   - Adzuna multi-market search, Jooble updates, TheirStack, SerpApi,
     Fantastic.jobs, USAJOBS, direct ATS feeds, direct employer feeds,
     job-title expansion, provider status reporting, and description
   enrichment.
   - 59 focused adapter, aggregation, route, search-service, and description
     tests pass. Provider failures are isolated and credential-bearing request
     errors are replaced with generic messages.
   - An independently reconstructed staged snapshot passes 264 backend tests,
     its complete Alembic cycle through `20260720_0005` with no schema drift,
     and frontend lint/build. The combined worktree passes the 282-test release
     gate through migration `20260721_0006`.
   - A bounded live Worldwide search returned one job, direct listing URL, and
     description from each of Adzuna, Jooble, TheirStack, and Fantastic.jobs.
     SerpApi completed successfully with `no_results`, not `unavailable`.
     USAJOBS and the Greenhouse, Lever, Ashby, Microsoft, Apple, and Crossover
     sources correctly reported `not_configured`.
   - A separate live Amazon Jobs lookup returned a complete description through
     the authenticated in-app enrichment route.
   - Provider attribution and the final “Continue to listing on [provider]”
     action remain in the job-details dialog. Adzuna cards and details render
     the required “Jobs by Adzuna” logo treatment.
   - Commercial-use approval remains an external deployment gate; details are
     recorded in the provider release review below.
5. **Persistent job catalog and ingestion — code, migration, and isolated live worker verified**
   - `JobListing`/`JobSyncState`, repository, migration `20260721_0006`,
     ingestion service, sync worker, cached-search integration, retention, and
     the optional Compose worker.
   - 31 focused repository, ingestion, worker, search, and profile-target tests
     pass. An independently reconstructed staged snapshot passes 282 backend
     tests, its complete Alembic cycle through `20260721_0006` with no schema
     drift, frontend lint/build, and the staged diff whitespace check.
   - A bounded one-shot Fantastic.jobs sync against an isolated, freshly
     migrated SQLite database fetched and stored one listing and recorded a
     successful sync state. Cached search then returned that stored listing.
     A second watch-mode cycle skipped the target according to its next-run
     schedule without another provider request, and the worker stopped cleanly
     on interruption.
   - Tests verify five-minute failure retry scheduling, generic persisted/logged
     errors that do not expose provider credentials, stale and expired listing
     exclusion, retention deactivation, safe listing URLs, normalized UTC
     timestamps, duplicate-target suppression, cached provider status, and
     live-search fallback when the cache is unavailable.
   - The Compose definition gates the worker on API and database health. A
     complete isolated local Compose verification now passes as recorded below;
     deployed staging observation remains a separate release check.

### Post-merge PostgreSQL verification — July 27, 2026

- PostgreSQL 16.14 was installed and an isolated, empty, loopback-only cluster
  was created for engine-specific release verification. Because the cluster
  contained no prior data, no backup was required; the temporary runtime and
  data directory were removed after the checks.
- The complete Alembic chain upgraded successfully through `20260721_0006`
  using PostgreSQL transactional DDL. `alembic check` reported no schema drift,
  and `alembic current` reported `20260721_0006 (head)`.
- The API started against PostgreSQL, and both `/health/live` and
  `/health/ready` returned HTTP 200 with `ok` and `ready` status payloads.
- A bounded Fantastic.jobs synchronization fetched one result, created one
  active `job_listings` row, and recorded one successful `job_sync_states` row
  with a future next-sync time and no error. Repository search returned the
  stored listing with its cached marker and listing URL.
- A second one-shot cycle and the watch worker both skipped the target according
  to its persisted schedule, with no additional provider result fetched.
- This closes the local PostgreSQL engine-validation gap. It does not replace a
  migration, backup, health, and long-running worker observation in the actual
  deployed staging environment.

### Local Docker Compose verification — July 28, 2026

- Docker Desktop 29.6.2 and Docker Compose 5.3.1 built and started the isolated
  `nexthireverify` project without changing the already-running IncidentPilot
  services. A temporary override exposed the API on loopback port 18080 and the
  frontend on loopback port 15173.
- The PostgreSQL 17, API, frontend, and optional ingestion-worker containers all
  started. PostgreSQL and API health checks passed before the worker started.
  The frontend build context was reduced to 320.48 kB by adding
  `frontend/.dockerignore`; the backend context was 2.42 MB.
- Inside the API container, `alembic current` reported
  `20260721_0006 (head)` and `alembic check` reported no new upgrade operations.
  `/health/live` and `/health/ready` returned HTTP 200 with `ok` and `ready`,
  and the frontend returned HTTP 200.
- A browser smoke test followed the protected-route redirect to `/login`,
  rendered the complete email/password sign-in form, and found no browser
  console errors.
- The worker ran with one bounded Fantastic.jobs target and a one-result cap.
  The provider returned HTTP 403 because the account's Jobs meter had exceeded
  its allowed limit. The worker isolated the failure, stored only the generic
  `Job ingestion failed.` message, scheduled a retry, skipped the not-yet-due
  target on a later poll, and did not expose the configured credential in its
  logs. Successful Compose ingestion remains blocked on renewed provider quota;
  the earlier isolated PostgreSQL verification proves the successful
  persistence path.
- `npm audit --omit=dev` reports two high-severity entries for the same
  React Router advisory in 7.18.1. The reviewed advisory states that it only
  affects unstable React Server Components APIs; this client-rendered
  `BrowserRouter` application imports none of those APIs. The registry's current
  `react-router-dom` release remains 7.18.1, while the advisory names 8.3.0 as
  patched. Monitor the package for a compatible patched release rather than
  downgrading to older versions with broader known advisories.
- After these Compose and build-context changes, `./scripts/verify_release.sh`
  passed all 282 backend tests, the complete Alembic upgrade/check/downgrade/
  re-upgrade cycle, frontend lint, the production frontend build, and the diff
  whitespace check.

### Apply Assistant foundation — July 28, 2026

- Migration `20260728_0007` adds owner-scoped resume and cover-letter
  references, provider metadata, and a reviewed-package timestamp to tracked
  applications.
- `POST /applications/prepare` requires two explicit confirmations, validates
  that the selected documents belong to the authenticated user and have the
  expected kinds, accepts only credential-free HTTPS application links, and
  records the package as `preparing`.
- Repeated preparation for the same job URL updates the existing application
  rather than creating duplicates. Already-applied, interview, offer, rejected,
  or archived statuses are never downgraded to `preparing`.
- The Jobs dialog now lets users select and download a saved resume and optional
  cover letter. The provider link appears only after the reviewed package is
  stored. The Application Tracker shows the selected document names and makes
  clear that NextHire has not submitted the employer form.
- An isolated authenticated browser test searched a seeded SQL-backed job,
  verified the action remained disabled until both confirmations were checked,
  saved the tailored resume and cover letter, exposed the correctly labeled
  provider link, and found one reviewed `preparing` application in the tracker.
  No browser console errors were recorded.
- The full release gate passes 290 backend tests, migration upgrade through
  `20260728_0007`, no schema drift, downgrade and re-upgrade, frontend lint,
  the production build, and the diff whitespace check.
- An empty ephemeral PostgreSQL 17 database also upgraded through
  `20260728_0007`, reported no schema drift, downgraded to base, and re-upgraded
  to head. Its temporary container and data were removed after verification.
- This is intentionally assisted apply, not a browser bot. It does not answer
  sensitive employer questions, bypass CAPTCHA or account security, or submit
  to external platforms. Direct ATS submission remains future work only where
  the employer provides credentials and written authorization.

### User-facing completion pass — July 28, 2026

- Every visible header and account-menu control now has a real destination or
  action. Global search navigates to product pages and matching Help Center
  articles; the notification bell and account-menu notification item open the
  notification center; Billing opens the existing plan section; and Help
  Center opens the new searchable documentation.
- The Help Center documents account access, profile and resume setup, document
  history and export, worldwide job search and provider states, reviewed
  applications, reminders, career tools, AI availability, billing, privacy,
  and job-source safety. It links directly to the relevant product workflow.
- Notifications derives real application follow-ups, deadlines, and reviewed
  packages from the authenticated user's Application Tracker data. It shows
  upcoming and overdue work, provides an unread badge, links each notification
  to the tracker, and keeps read state isolated by user in the current browser.
- Billing no longer appears as an unexplained disabled placeholder. Settings
  loads the backend billing status, routes errors to the correct section, and
  explains that Free remains available while paid plans are disabled until
  approved Stripe configuration exists.
- Unknown authenticated routes now render a useful 404 page instead of an
  empty screen. The account menu also falls back to the account email when the
  profile has no name, and its header colors match the light application
  header.
- An isolated authenticated browser smoke test registered and signed in a
  disposable user, navigated to Help Center through global search, filtered
  the articles, rendered the empty notification state, created an application,
  verified an overdue follow-up and unread badge from isolated SQL data, marked
  it read, opened Billing from the account menu, and verified the 404 route.
  A duplicate Google Identity initialization warning found during the test was
  fixed; a fresh login tab rendered the Google button with no console warnings
  or errors.
- The complete release gate still passes 290 backend tests, the Alembic
  upgrade/check/downgrade/re-upgrade cycle, frontend lint, the production
  build, and the whitespace check.
- Production Google sign-in remains a deployment configuration task: the same
  OAuth client ID must be provided to both services and the deployed frontend
  origin must be authorized in Google Cloud. SMTP, paid billing, credentialed
  job providers, and production AI remain separate external gates.

### Guided onboarding — July 29, 2026

- A protected Getting Started page now guides users through four durable
  activation steps: career profile, resume analysis, job preferences, and the
  first tracked opportunity. Each step links directly to the existing product
  workflow.
- Progress comes from the authenticated dashboard service and saved
  profile, resume-analysis, preference, and application records. Visiting a
  page alone never marks a step complete.
- Newly registered email/password users are routed to Getting Started after
  their first successful sign-in. Normal sign-ins for existing accounts still
  open the dashboard, and all users can reopen onboarding from the sidebar,
  global search, dashboard progress card, or Help Center.
- Eight focused dashboard service and route tests pass. An isolated local API
  check created a disposable user, returned zero of four onboarding steps,
  saved synthetic profile and preference data, and then returned two of four
  completed steps with the correct step flags.
- The complete release gate passes 291 backend tests, the full Alembic
  upgrade/check/downgrade/re-upgrade cycle with no schema drift, frontend lint,
  the production build, and the whitespace check.
- Automated control of the existing localhost preview tab was blocked by the
  browser URL safety policy during this pass, so no new visual browser-smoke
  claim is made for onboarding. The API behavior and compiled UI are verified;
  a manual visual pass remains before deployment.

### Product workflow completion batch — July 29, 2026

- Saved jobs can be added and removed from job results and reviewed in the new
  Job Library. Saved searches preserve the complete filter set, establish a
  first-run baseline, and report previously unseen matches on later checks.
  New-match counts appear in Job Library and the in-app notification center.
- Help Center now accepts owner-scoped feedback and support requests and shows
  each user's recent request status. Administrator access is enforced by the
  backend using the deployment's `ADMIN_EMAILS` allowlist and verified-email
  state. The protected
  Operations page reports aggregate account, job, application, AI-use, and
  support counts, shows configuration as boolean status only, and supports
  ticket status and internal-note updates.
- Resume Studio version history now compares an earlier revision with the
  current document side by side before restore. Application Tracker now
  switches between the existing pipeline and a monthly calendar of deadlines,
  follow-ups, and applied dates.
- Interview Center now stores owner-scoped practice attempts and provides a
  transparent structure score for clarity, STAR-style organization, evidence,
  and ownership. The interface explicitly states that this is not a technical
  correctness or hiring-likelihood score.
- Apply Assistant now provides a copyable information pack built only from the
  authenticated user's saved name, contact, location, role, experience, and
  professional-link fields. It does not infer work authorization, salary,
  demographic, disability, or other sensitive responses; it still does not
  bypass CAPTCHA, complete restricted forms, or submit to employers.
- The new workflows include a main-content skip link, keyboard-visible focus,
  reduced-motion handling, labeled dialogs, Escape-to-close behavior, body
  scroll locking, responsive titles, and bounded horizontal scrolling for
  dense comparison and calendar layouts.
- Migrations `20260729_0008`, `20260729_0009`, and `20260729_0010` add saved
  jobs/searches, support tickets, and interview practice attempts. Account
  export and deletion include all three data groups, and owner-isolation tests
  cover their repositories.
- `./scripts/verify_release.sh` passes 317 backend tests, the full Alembic
  upgrade/check/downgrade/re-upgrade cycle through `20260729_0010`, frontend
  lint, the production Vite build, and `git diff --check`.
- Automatic email delivery for saved-search alerts is intentionally not
  activated. In-app alerts are complete. Scheduled email alerts should be
  enabled only after the deployed SMTP sender, opt-in/opt-out behavior,
  deliverability, unsubscribe handling, rate controls, and background-worker
  observation are verified.
- No deployment was performed in this batch. The local implementation remains
  on `codex/complete-user-facing-workflows` for review before migration and
  staging deployment.

### Saved-search email alert foundation — July 29, 2026

- Migration `20260729_0011` adds per-search email consent, daily or weekly
  frequency, timezone-aware next-run state, last-send time, and owner-scoped
  delivery records with batch idempotency.
- Email alerts require three conditions: the deployment flag, configured SMTP,
  and an explicitly enabled saved search belonging to a verified-email account.
  They remain off by default. Disabling an alert still works when deployment
  delivery is unavailable.
- Job Library exposes consent, frequency, next-run, last-email, and recent
  delivery state. Email links open a public confirmation page and do not mutate
  the preference until the user chooses to turn off that one alert. Signed
  unsubscribe tokens authorize only that action for that saved search.
- The one-shot `backend.jobs.send_job_alerts` worker is suitable for a Railway
  cron service. It processes a bounded due batch and exits. A saved search's
  first scheduled run establishes a baseline without sending. Failed delivery
  records a generic error and leaves new jobs unseen for retry.
- Account export and deletion include alert delivery records. Operations
  exposes alert enablement and aggregate delivery state without configuration
  secrets.
- Focused coverage verifies SMTP header allowlisting, verified-email consent,
  timezone scheduling, tamper-resistant unsubscribe tokens, delivery history,
  owner scoping, first-run baseline, successful send, and retry-safe failure.
- `./scripts/verify_release.sh` passes 330 backend tests, the complete Alembic
  upgrade/check/downgrade/re-upgrade cycle through `20260729_0011`, frontend
  lint, the production build, and `git diff --check`.
- No external email provider was created or charged, and no deployment was
  performed. `JOB_ALERT_EMAIL_ENABLED` remains `false` by default. The exact
  Postmark/Railway staged activation and rollback procedure is recorded in
  `docs/job-alert-email-setup.md`.

### Administrator accountability and registration retry — July 29, 2026

- Migration `20260729_0012` adds administrator audit events. Support-ticket
  status and internal-note changes commit atomically with an event containing
  the administrator ID/email snapshot, request ID, target, status transition,
  and whether a note is present. Ticket messages and note text are excluded.
- Audit events are exposed only through the verified-email administrator
  dependency. The Operations page shows recent history and aggregate audited
  change counts without exposing secrets.
- SQLAlchemy mutation guards and SQLite/PostgreSQL database triggers reject
  updates and deletion. A migrated isolated SQLite database rejected direct
  SQL update and delete attempts and preserved the original event.
- Registration now clears stale success/error state for every attempt, reports
  accessible status, prevents duplicate submission while loading, uses email
  and password autocomplete metadata, and enforces the backend's password
  length in the browser.
- An isolated browser test reproduced a duplicate-account error, retried with a
  new disposable account, and confirmed that only the successful state
  remained. A verified disposable administrator then resolved a support
  request; Operations immediately displayed the append-only event and request
  ID without copied ticket or note text. Test accounts, ticket, and audit event
  were removed, and the isolated services were stopped.
- The complete suite passes 333 backend tests and frontend lint. Full release
  verification through migration `20260729_0012` is recorded after this
  documentation update.

### Resume upload malware-scanning foundation — July 29, 2026

- Resume Studio analysis, profile autofill, and Resume Tailor uploads all
  converge on `ResumeService.extract_text`; the new scanner therefore runs
  once after bounded extension/signature validation and before any PDF/DOCX
  parser.
- `MalwareScanService` implements ClamAV INSTREAM over a configured private
  connection. Clean responses continue, detections return a generic rejection,
  and missing configuration, timeouts, connection errors, empty responses, or
  unexpected responses fail closed with HTTP 503.
- Scanning and parsing run outside the async event loop. Temporary files remain
  bounded to 5 MB and are removed on clean, detected, unavailable, invalid, and
  parser-failure paths.
- Operations exposes configuration as a boolean only. The deployment switch is
  `false` by default, so no unverified protection is claimed and current local
  behavior is unchanged.
- Focused coverage verifies disabled behavior, clean protocol exchange,
  detection without signature disclosure, missing configuration, timeout,
  scan-before-parse ordering, and 503 handling across all three upload routes.
- Deployment guidance requires a private ClamAV network, maintained signature
  updates, measured memory capacity, fail-closed outage testing, monitoring,
  and continued parser isolation. No scanner service was deployed in this
  batch.
- The complete suite passes 342 backend tests. Full release verification
  through migration `20260729_0012` is recorded after this documentation
  update.

### Isolated resume-parser foundation — August 2, 2026

- After extension, size, signature, and optional malware validation, each PDF
  or DOCX is parsed in a fresh subprocess that the API awaits asynchronously.
  Document parsers no longer execute in the API process or its thread pool,
  and there is no in-process fallback.
- The worker receives only the application-generated temporary path, validated
  suffix, and bounded settings. Its environment excludes database, JWT, SMTP,
  provider, billing, and other application secrets.
- The worker applies CPU, core-dump, file-descriptor, extracted-text, and
  wall-clock limits, plus an address-space limit on Linux. Python socket entry
  points are disabled before parsing. Timeout or request cancellation stops
  the worker, and the parent removes the temporary file on every path.
- Malformed or unreadable documents return a generic HTTP 400 response. Worker
  startup, resource, timeout, protocol, and unexpected-exit failures fail
  closed with HTTP 503 without exposing parser output or internal exceptions.
- Real PDF and DOCX subprocess tests pass. Additional coverage verifies the
  secret-free environment, extracted-text limit, timeout termination,
  scan-before-parse ordering, cleanup, and 503 handling for Resume Studio,
  profile autofill, and Resume Tailor.
- The subprocess is not represented as a complete operating-system sandbox.
  Production still requires an unprivileged/read-only container, narrow temp
  storage, platform egress and cloud-metadata blocking, container resource and
  process limits, patched dependencies, monitoring, and deployed staging
  observation.
- The complete suite passes 354 backend tests. Full release verification
  through migration `20260729_0012` is recorded after this documentation
  update.

### Temporary Railway staging verification — August 2, 2026

- Commit `95c759f` from `codex/complete-user-facing-workflows` was deployed to
  an isolated `staging-pr6` Railway environment with separate PostgreSQL,
  backend, and frontend instances.
- The backend and frontend were connected to the feature branch. The frontend
  API URL, backend frontend URL, and CORS origin pointed only to the staging
  domains. `JOB_ALERT_EMAIL_ENABLED` and `MALWARE_SCANNING_ENABLED` remained
  explicitly `false`.
- Both application services and PostgreSQL reached Online. The live and ready
  health endpoints returned HTTP 200, reported release `95c759f`, and confirmed
  database readiness.
- Deployed browser smoke testing completed registration, login, onboarding,
  profile creation, Help Center rendering, support-request creation, and the
  recent-request status view against the isolated database.
- After verification, `staging-pr6` and its disposable data were permanently
  deleted. Railway showed the production API, PostgreSQL, and frontend still
  Online, and production was not redeployed or reconfigured.
- This proves the release build and core account/support persistence on
  Railway. It does not prove SMTP delivery, the scheduled alert worker,
  ClamAV, hardened parser controls, backup/restore, job-provider contracts, or
  production AI capacity; those gates remain open.

### Production email and scheduled-alert verification — August 11, 2026

- The production API and hourly Railway one-shot worker use Brevo's HTTPS
  transactional-email API. The deployment and per-search consent gates are
  enabled only for explicitly opted-in, verified-email accounts.
- A disabled safe run reported `configured: false`, `sent: 0`, and `failed: 0`.
  The first enabled due run established one baseline and sent nothing.
- After a new matching listing became available, the next due run sent one
  email with no failures. Brevo recorded Sent, Delivered, and First opening for
  the expected NextHire saved-search subject.
- Opening the public unsubscribe URL with GET did not change the preference.
  Submitting the confirmation with POST disabled only that saved search. The
  user then re-enabled it from Job Library and the next daily run appeared.
- This completes automatic saved-search email for the controlled production
  beta. A custom authenticated sender domain, ongoing deliverability and worker
  monitoring, and wider-user capacity remain public-launch operations.

### ClamAV deployment preparation — August 11, 2026

- The private-scanner implementation remains fail closed and all 23 focused
  scanner and upload-route tests pass. The complete release gate passes 356
  backend tests, the Alembic upgrade/check/downgrade/re-upgrade cycle, frontend
  lint, the production build, and `git diff --check`.
- `docker-compose.clamav.yml` adds an optional local proof using the official
  ClamAV 1.5 feature image, persistent signatures, a 4 GB memory limit, one
  vCPU, the image health check, and no published port. The merged Compose model
  validates. Docker was not running locally, so no live-container result is
  claimed.
- The Railway runbook now records the private-network, volume, health,
  clean-file, harmless-fixture, fail-closed outage, recovery, and no-public-port
  checks. The current billing cycle showed $0.93 usage against $5 included; a
  24-hour proof at the configured resource ceilings is bounded to roughly $2
  of compute, but ongoing monthly cost still requires owner approval.

### Temporary Railway ClamAV proof and cleanup — August 13, 2026

- A temporary `clamav/clamav:1.5_base` service ran in the production Railway
  environment with one replica, a one-vCPU limit, a 4 GB memory limit, a
  persistent `/var/lib/clamav` volume, and serverless sleeping disabled. It had
  no public domain or TCP proxy. FreshClam loaded daily database 28089, main
  database 63, and bytecode database 339 before `clamd` became ready.
- The production API was first redeployed healthy with scanning disabled, then
  with `MALWARE_SCANNING_ENABLED=true` and a Railway private-domain reference.
  Its deployed `MalwareScanService` reported active/configured, accepted a clean
  stream, rejected the exact approved harmless antivirus fixture with only the
  generic `The uploaded file failed security scanning.` message, and converted
  a simulated unreachable scanner into the generic temporarily-unavailable
  error. Public `/health/ready` remained HTTP 200 with healthy database checks.
- This proves private connectivity and the deployed service-layer clean,
  detection, and fail-closed paths. It does not prove valid PDF/DOCX behavior
  through Resume Studio, profile autofill, and Resume Tailor, restored-service
  recovery, or sustained signature, latency, memory, and restart monitoring.
- After proof, the API was redeployed with scanning disabled. The stale
  `CLAMAV_HOST`, `CLAMAV_PORT`, and `CLAMAV_TIMEOUT_SECONDS` variables were
  removed in a second successful deployment. The temporary scanner service and
  signature volume were then permanently deleted. Railway showed the API,
  frontend, and PostgreSQL Online, and `/health/ready` returned HTTP 200.
- Railway's usage page showed $1.80 current project usage and a $4.20 estimate.
  Deleted services, which include this temporary scanner, accounted for
  $0.7254. No recurring scanner resource remains. Ongoing deployment still
  requires owner cost approval.
- The readiness response still reports release `d4ab044` while Railway labels
  the active source deployment as `Add Brevo transactional email delivery
  (#7)`. Treat `APP_RELEASE` as stale configuration and correct it before using
  that field as production provenance evidence.

### Recommended continuation order

Review the current branch and the recorded Railway smoke evidence. Configure
at least one administrator email, verify the established admin workflows, and
complete a manual mobile/keyboard visual pass. The Brevo sender, scheduled
worker, baseline, delivery, and unsubscribe activation path are proven for the
controlled beta. The temporary ClamAV proof covers private service-layer clean,
detection, and fail-closed behavior; next approve a retained scanner and prove
all three upload routes, recovery, and monitoring while hardening the isolated
parser's container egress, filesystem, process, and resource controls. Retain
live
Turnstile, provider commercial approval and quota, and the remaining deployed
staging checks as release gates. Do not replace the July 17 beta assessment
with this engineering snapshot; its manual smoke-test evidence and external
launch blockers remain separate.

### Provider release review — July 26, 2026

- **Adzuna:** Worldwide search fans out across eight configured markets, so one
  user search can consume eight API requests. The default limits are 25
  requests/minute, 250/day, 1,000/week, and 2,500/month. Commercial evaluation
  is limited to 14 days unless Adzuna grants written consent or a licence.
  Production remains blocked on that approval and confirmation of the final
  logo asset. See the [Adzuna API terms](https://developer.adzuna.com/docs/terms_of_service).
- **Jooble:** The registered REST API is expressly designed to display Jooble
  search results in a site’s own UI, but the public documentation does not
  publish a quota or clearly grant this product’s ongoing commercial use.
  Confirm both with Jooble for the registered key before production. See the
  [Jooble REST API documentation](https://help.jooble.org/en/support/solutions/articles/60001448238-rest-api-documentation).
- **TheirStack:** Each returned job costs one API credit, including repeated
  requests. The adapter caps free-plan pages at 25 results; the free plan
  includes 200 API credits/month and has additional per-second, per-minute,
  hourly, and daily limits. Confirm that the selected subscription and licence
  permit the intended display and retention. See [credits](https://theirstack.com/en/docs/pricing/credits),
  [plans](https://theirstack.com/en/docs/pricing/plans), and
  [terms](https://theirstack.com/en/docs/legal/terms-and-conditions).
- **SerpApi:** One successful Google Jobs request consumes one search regardless
  of result count; up to ten jobs are returned per page and identical cached
  requests are free. The current free plan includes 250 searches/month. See the
  [Google Jobs API](https://serpapi.com/google-jobs-api) and
  [current pricing](https://serpapi.com/pricing).
- **Fantastic.jobs:** Active ATS responses consume one Jobs credit per returned
  record. The adapter caps responses at 20 and caches identical searches for 15
  minutes. The configured account returned `Jobs` meter quota exhaustion during
  the July 28 Compose verification. Production requires renewed quota plus an
  account plan and licence matching expected display, retention, and request
  volume. See the
  [endpoint documentation](https://developer.fantastic.jobs/documentation/endpoints/new-jobs).
- **USAJOBS:** API data is restricted to the requesting company and purpose on
  the registration form; other use requires prior written approval. Keep it
  disabled until a NextHire-specific key and approval exist. See the
  [USAJOBS terms](https://developer.usajobs.gov/guides/).
- **Employer ATS feeds:** Greenhouse GET job-board data is public, and Lever and
  Ashby document their postings feeds for organization career sites. Keep board
  identifiers empty until the relevant employer or account owner has approved
  aggregation. Microsoft, Apple, and Crossover use undocumented public
  career-site interfaces and are disabled unless explicitly opted in with
  `DIRECT_EMPLOYER_JOB_SOURCES`.

## Completed engineering foundation

- Authenticated profile, dashboard, career analytics, Resume Studio, document
  history/export, job search/matching, skill gap, tailoring, cover letters,
  reviewed application packages, and application tracking.
- Multi-provider job aggregation with filtering, pagination, deduplication, graceful provider failures, source attribution, and profile/resume-aware ranking.
- Registration, login protection, email verification, password recovery, token revocation, account deletion, versioned legal consent, and protected routes.
- PostgreSQL support, Alembic migrations, backup/restore guidance, tested schema upgrade/downgrade, deployment containers, health endpoints, request IDs, structured logs, and CI.
- AI timeouts, retries, structured-output requests, prompt caps, durable per-user Free/Pro allowances, and graceful ranking fallbacks.
- Owner-scoped persistence, secure upload limits/signature checks, complete data export, deletion coverage, and isolation tests.
- Stripe checkout, portal, signed subscription webhooks, entitlement state, and disabled-until-configured paid plans.
- Privacy-conscious dashboard analytics and commercial/legal operational checklists.

## External launch blockers

These cannot be completed honestly through repository code alone:

- Operating company identity, launch markets, counsel-approved legal documents, support/privacy contact, subprocessors, and jurisdiction-specific compliance.
- Written approval of each job provider’s commercial use and attribution requirements.
- Custom production domain and authenticated email-sender domain, monitoring,
  backup storage, secret manager, incident contacts, and restore drill.
  Railway hosting, PostgreSQL, Brevo transactional delivery, and the hourly
  alert worker are active for the controlled beta.
- Deployed PostgreSQL backup/restore plus extended ingestion-worker
  observation. The Railway application and migration smoke path is verified,
  but it does not replace backup restoration and long-running worker evidence.
- AI provider commercial/privacy approval and production capacity.
- Stripe account, approved product price, tax/refund/cancellation policy, webhook secret, live-mode testing, and reconciliation ownership.
- Retained private ClamAV deployment, signature/update monitoring, complete
  upload-route activation and recovery evidence, and platform-level egress,
  filesystem, process, and resource hardening for isolated asynchronous
  parsing. A temporary service-layer proof passed and was removed.

Until those items are resolved, run a controlled non-commercial beta, keep billing disabled, limit invited users, and avoid claims of provider partnership or guaranteed employment outcomes.

## Recommended next product work after beta evidence

1. Fix issues discovered in the controlled beta before expanding scope.
2. Assign operational ownership and approve the retention/archive period for
   the completed append-only administrator audit log.
3. Approve a retained private ClamAV service, complete all upload-route and
   recovery checks, and prove the parser-subprocess integration under
   platform-level sandboxing and monitoring.
4. Evaluate direct ATS application submission only through employer-authorized
   APIs with per-application consent, submission receipts, idempotency, and
   audit logs; do not automate restricted job platforms.
5. Monitor the proven opt-in saved-search email flow and collect delivery,
   bounce, complaint, unsubscribe, worker-failure, and latency evidence before
   considering application reminder emails.
6. Validate the completed responsive and keyboard behavior with beta users and
   address evidence-backed usability issues. Route-level code splitting is
   implemented and the production build has no large-bundle advisory.
7. Select further Resume Studio, interview, or learning features based on measured activation and retention rather than assumptions.
